#!/usr/bin/env python3
"""Verify a native DataLad run and two fresh-clone reruns of the SciPy fixture."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
MODULE = Path('experiments/datalad-native')
OUTPUTS = MODULE / 'outputs'
SCIENCE = Path('experiments/datalad-annex')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(root):
    """Closed-form known answers; no SciPy call or reimplementation of its test."""
    output = root / OUTPUTS
    if not all((output / name).is_file() for name in ('statistics.tsv', 'figure.svg', 'figure.png')):
        return {'ok': False, 'reason': 'output absent'}
    rows = pd.read_csv(output / 'statistics.tsv', sep='\t')
    expected = dict(n=5, mean=3, sd=math.sqrt(2.5), t=math.sqrt(18), df=4,
                    p=1 - 36 / (11 * math.sqrt(11)),
                    ci_low=1.036756838522439, ci_high=4.963243161477560)
    checks = {key: len(rows) == 1 and math.isclose(float(rows.iloc[0][key]), value,
              rel_tol=1e-10, abs_tol=1e-11) for key, value in expected.items()}
    return {'ok': all(checks.values()), 'numeric_checks': checks,
            'hashes': {p.name: sha(p) for p in output.iterdir()}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-id', required=True)
    parser.add_argument('--resolver', type=Path)
    args = parser.parse_args()
    if not args.run_id or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_' for c in args.run_id):
        parser.error('run-id must use letters, digits, hyphens or underscores')
    resolver = args.resolver
    if resolver is None:
        config = Path.home() / '.config/stamped-ai-research-next/launch.json'
        resolver = Path(json.loads(config.read_text())['resolver'])
    resolver = resolver.expanduser().resolve(strict=True)
    receipts = ROOT / MODULE / 'receipts' / args.run_id
    receipts.mkdir(parents=True, exist_ok=False)
    external = Path(tempfile.mkdtemp(prefix='stamped-native-datalad-'))
    commands, checks = [], []
    summary = {'status': 'failed', 'external_clones': str(external)}

    def save(name, value):
        (receipts / name).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')

    def run(argv, cwd=ROOT):
        argv = list(map(str, argv))
        number = len(commands) + 1
        print(f'COMMAND {number}: {json.dumps(argv)}', flush=True)
        started = time.time()
        result = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, timeout=180,
                                env=dict(os.environ, GIT_TERMINAL_PROMPT='0', DATALAD_UI_PROGRESSBAR='none'))
        (receipts / f'{number:03d}.stdout').write_text(result.stdout)
        (receipts / f'{number:03d}.stderr').write_text(result.stderr)
        commands.append(dict(argv=argv, cwd=str(cwd), returncode=result.returncode,
                             started_unix=started, elapsed_seconds=time.time() - started))
        save('commands.json', commands)
        print(result.stdout, end='', flush=True)
        print(result.stderr, end='', file=sys.stderr, flush=True)
        result.check_returncode()
        return result.stdout.strip()

    def pixi(root, *argv):
        return run(['pixi', 'run', '--locked', '--manifest-path', root / 'pixi.toml', *argv], root)

    def check(name, passed, **evidence):
        checks.append(dict(name=name, passed=bool(passed), **evidence))
        save('checks.json', checks)
        if not passed:
            raise AssertionError(name)

    def discover(root, revision):
        records = [json.loads(line) for line in pixi(root, 'datalad', '-f', 'json', 'rerun',
                   '--report', revision).splitlines() if line.startswith('{')]
        check(f'native_discovery_{revision[:8]}', any(r.get('rerun_action') == 'run' for r in records),
              records=records)

    try:
        base = run(['git', 'rev-parse', 'HEAD'])
        manifest_hash, lock_hash = sha(ROOT / 'pixi.toml'), sha(ROOT / 'pixi.lock')
        save('sources.json', dict(base_revision=base, manifest_sha256=manifest_hash,
             lock_sha256=lock_hash, compute_sha256=sha(ROOT / SCIENCE / 'compute.py'),
             datalad_version=pixi(ROOT, 'datalad', '--version')))
        check('producer_outputs_absent_and_oracle_rejects', not (ROOT / OUTPUTS).exists() and not verify(ROOT)['ok'])
        pixi(ROOT, 'datalad', 'run', '--explicit', '-i', SCIENCE / 'input.csv', '-i', SCIENCE / 'compute.py',
             '-i', 'pixi.toml', '-o', OUTPUTS, '-m', 'compute SciPy known-answer fixture natively', '--',
             'python', SCIENCE / 'compute.py', '--output-directory', OUTPUTS)
        revision = run(['git', 'rev-parse', 'HEAD'])
        original = verify(ROOT)
        check('producer_independent_known_answers', original['ok'], result=original)
        message = run(['git', 'show', '-s', '--format=%B', revision])
        check('native_subject_and_fresh_provenance', message.startswith('[DATALAD RUNCMD] ')
              and 'Co-Authored-By: Codex Desktop ' in message and 'Codex-Reasoning-Effort: ' in message)
        key = pixi(ROOT, 'git', 'annex', 'lookupkey', OUTPUTS / 'statistics.tsv')
        check('table_annexed', bool(key) and (ROOT / OUTPUTS / 'statistics.tsv').is_symlink(), key=key)
        discover(ROOT, revision)
        replay_source, replay_revision = ROOT, revision
        replay_revisions = []
        for index in (1, 2):
            clone = external / f'replay-{index}'
            branch = f'codex/proof-native-datalad-replay-0{index}'
            run(['git', 'clone', '--no-hardlinks', replay_source, clone])
            run(['git', 'checkout', '--detach', base], clone)
            run(['git', 'submodule', 'update', '--init', '--recursive'], clone)
            shutil.copyfile(ROOT / 'pixi.lock', clone / 'pixi.lock')
            run(['pixi', 'install', '--locked', '--manifest-path', clone / 'pixi.toml'], clone)
            pixi(clone, 'git', 'annex', 'init', f'native replay {index}')
            pixi(clone, 'python', ROOT / 'scripts/prepare_checkout.py', '--checkout', clone,
                 '--resolver', resolver, '--provenance-only', '--receipt', receipts / f'replay-{index}-prepared.json')
            check(f'replay_{index}_starts_without_outputs', not (clone / OUTPUTS).exists() and not verify(clone)['ok'])
            discover(clone, replay_revision)
            pixi(clone, 'datalad', 'rerun', '--onto', base, '--branch', branch, replay_revision)
            result = verify(clone)
            check(f'replay_{index}_matches_oracle_and_all_output_bytes', result['ok'] and result['hashes'] == original['hashes'], result=result)
            replay_revision = run(['git', 'rev-parse', 'HEAD'], clone)
            replay_revisions.append(replay_revision)
            discover(clone, replay_revision)
            run(['git', 'fetch', clone, f'refs/heads/{branch}:refs/heads/{branch}'])
            check(f'replay_{index}_environment_unchanged', sha(clone / 'pixi.lock') == lock_hash
                  and sha(clone / 'pixi.toml') == manifest_hash)
            replay_source = clone
        summary.update(status='passed', base_revision=base, run_revision=revision,
                       replay_revisions=replay_revisions, checks=len(checks), output_hashes=original['hashes'])
    except Exception as error:
        summary.update(error=f'{type(error).__name__}: {error}')
    finally:
        save('summary.json', summary)
        print(json.dumps(summary, indent=2))
    return 0 if summary['status'] == 'passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
