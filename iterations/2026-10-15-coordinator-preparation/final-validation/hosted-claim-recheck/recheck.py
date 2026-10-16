#!/usr/bin/env python3
"""Read hosted checkpoint metadata from isolated, empty Git contexts."""
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
from datetime import datetime, timezone

OUT = Path(__file__).resolve().parent
OLD = Path('/Users/johnlee/code/CON/stamped-ai-research')
PREP = OUT.parent
ENV = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
REMOVED = sorted(k for k in os.environ if k.startswith('GIT_'))


def dump(path, value):
    with path.open('x') as f:
        json.dump(value, f, indent=2)
        f.write('\n')


def candidates():
    result = []
    for group, paths in (
        ('old-pilot-setup', sorted((OLD / '.setup/gates').glob('*.evidence.json'))),
        ('old-pilot-research', sorted((OLD / 'experiments').glob('*/capture/*.json'))),
        ('next-preparation', [
            PREP / 'cold-retry-evidence/worker-native-hosted-verification.json',
            PREP / 'native-capture-investigation-01/verified-native-capture.json',
            PREP / 'cold-stamped-evidence/coordinator-actions/worker-native-verification.json',
        ]),
    ):
        for path in paths:
            raw = path.read_bytes()
            d = json.loads(raw)
            result.append({
                'group': group, 'source': str(path),
                'source_sha256': hashlib.sha256(raw).hexdigest(),
                'checkpoint_id': d['checkpoint_id'],
                'expected_session_id': d.get('native_session_id', d.get('session_id')),
                'requested_hosted_repository': 'gh/leej3/stamped-ai-research' + ('-next' if group == 'next-preparation' else ''),
            })
    assert len(result) == 15
    return result


def audit(item):
    directory = OUT / item['checkpoint_id']
    directory.mkdir()
    commands = []
    cwd = Path(tempfile.mkdtemp(prefix='stamped-hosted-claim-', dir='/private/tmp'))

    def run(argv, stem):
        start = datetime.now(timezone.utc).isoformat()
        try:
            p = subprocess.run(argv, cwd=cwd, env=ENV, capture_output=True, timeout=90)
            rc, stdout, stderr = p.returncode, p.stdout, p.stderr
        except subprocess.TimeoutExpired as e:
            rc, stdout, stderr = None, e.stdout or b'', e.stderr or b''
        (directory / (stem + '.stdout')).write_bytes(stdout)
        (directory / (stem + '.stderr')).write_bytes(stderr)
        rec = {'argv': argv, 'cwd': str(cwd), 'started_at': start,
               'finished_at': datetime.now(timezone.utc).isoformat(),
               'exit_code': rc, 'stdout_file': stem + '.stdout', 'stderr_file': stem + '.stderr',
               'stdout_sha256': hashlib.sha256(stdout).hexdigest(),
               'stderr_sha256': hashlib.sha256(stderr).hexdigest()}
        commands.append(rec)
        return rc, stdout.decode(errors='replace'), stderr.decode(errors='replace')

    def state(prefix):
        s = {}
        for key, argv in (
            ('refs', ['git', 'for-each-ref', '--format=%(refname) %(objectname)']),
            ('remotes', ['git', 'remote', '-v']),
            ('objects', ['git', 'count-objects', '-v']),
            ('head', ['git', 'rev-parse', '--verify', 'HEAD']),
        ):
            rc, stdout, stderr = run(argv, prefix + '-' + key)
            s[key] = {'exit_code': rc, 'stdout': stdout, 'stderr': stderr}
        counts = dict(line.split(': ', 1) for line in s['objects']['stdout'].splitlines())
        s['empty_git_context'] = (
            s['refs']['exit_code'] == 0 and not s['refs']['stdout']
            and s['remotes']['exit_code'] == 0 and not s['remotes']['stdout']
            and s['head']['exit_code'] not in (0, None)
            and counts.get('count') == '0' and counts.get('in-pack') == '0'
            and not (cwd / '.entire').exists()
            and not (cwd / '.git/objects/info/alternates').exists()
        )
        return s

    assert run(['git', 'init', '--quiet'], 'git-init')[0] == 0
    before = state('before')
    assert before['empty_git_context']
    rc, stdout, stderr = run([
        'entire', 'checkpoint', 'explain', item['checkpoint_id'],
        '--repo', item['requested_hosted_repository'], '--json',
    ], 'hosted')
    after = state('after')
    try:
        metadata = json.loads(stdout)
    except ValueError:
        metadata = {}
    sessions = [s.get('session_id') for s in metadata.get('sessions', [])]
    verified = bool(
        rc == 0 and metadata.get('checkpoint_id') == item['checkpoint_id']
        and sessions.count(item['expected_session_id']) == 1
        and before['empty_git_context'] and after['empty_git_context']
        and before == after
    )
    result = dict(item, verified_at=datetime.now(timezone.utc).isoformat(),
                  hosted_verified=verified, command_exit_code=rc,
                  returned_checkpoint_id=metadata.get('checkpoint_id'),
                  returned_session_ids=sessions, metadata=metadata,
                  empty_git_context=str(cwd), before=before, after=after,
                  removed_git_environment_variable_names=REMOVED,
                  local_metadata_fallback_excluded=bool(before['empty_git_context'] and after['empty_git_context'] and before == after),
                  raw_transcript_requested=False,
                  url_available_in_metadata=any('url' in k.lower() for k in metadata))
    dump(directory / 'commands.json', commands)
    dump(directory / 'result.json', result)
    return {k: v for k, v in result.items() if k not in ('before', 'after', 'metadata')}


if __name__ == '__main__':
    items = candidates()
    dump(OUT / 'expected.json', items)
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(audit, items))
    summary = {
        'verified_at': datetime.now(timezone.utc).isoformat(),
        'scope': 'Hosted metadata identity only; not raw transcript, visual dashboard, or scientific validation.',
        'method': 'Fresh Git repositories containing zero objects, refs, remotes, HEAD commits, alternates, or local Entire data; all inherited GIT_* variables removed; before/after state retained.',
        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'results': results,
        'counts': {g: {'expected': sum(r['group'] == g for r in results),
                       'verified': sum(r['group'] == g and r['hosted_verified'] for r in results)}
                   for g in ('old-pilot-setup', 'old-pilot-research', 'next-preparation')},
        'checkpoint_web_urls': 'Not invented; CLI JSON metadata is checked for URLs. Repository evidence source paths and exact hosted query arguments are preserved.',
    }
    dump(OUT / 'summary.json', summary)
    print(json.dumps({'counts': summary['counts'], 'summary': str(OUT / 'summary.json')}, indent=2))
