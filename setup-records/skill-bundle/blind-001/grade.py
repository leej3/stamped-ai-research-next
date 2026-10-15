"""Independently inspect the completed known-answer trial without rerunning science."""
import argparse
import csv
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import tempfile

TASK = '9c15dfe23eb8ad03ac6420f381ca645a6c3dddda'
SNAPSHOT = '472fbcfdcde21a4120a29ee2e6e3b13d8e72f67c'
RUN = '00103044a25dddb01aabda261fef06754ca5987a'
RERUN = '4956203d524b814e416e87260ce4d1ae82ac176e'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--recipient', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    receipt = json.loads((here/'delivery/receipt.json').read_text())
    checks = []

    def check(name, condition, evidence):
        checks.append({'check': name, 'passed': bool(condition), 'evidence': evidence})
        assert condition, name

    def git(path, *argv):
        return subprocess.check_output(['git', '-C', str(path), *argv]).decode().strip()

    def digest(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    check('graded task identity', git(args.source, 'rev-parse', 'HEAD') == TASK, TASK)
    check('original task tree clean', git(args.source, 'status', '--porcelain') == '', TASK)
    check('recipient rerun identity', git(args.recipient, 'rev-parse', 'HEAD') == RERUN, RERUN)
    check('snapshot directly above task', git(args.source, 'rev-parse', SNAPSHOT+'^') == TASK, SNAPSHOT)
    check('snapshot only adds lock', git(args.source, 'diff', '--name-only', TASK, SNAPSHOT) == 'pixi.lock', SNAPSHOT)
    check('lock ordinary Git blob', git(args.source, 'ls-tree', SNAPSHOT, 'pixi.lock').startswith('100644 blob '), SNAPSHOT)
    check('lock absent from task tree', not git(args.source, 'ls-tree', TASK, 'pixi.lock'), TASK)
    lock = subprocess.check_output(['git', '-C', str(args.source), 'show', SNAPSHOT+':pixi.lock'])
    check('exact lock hash', hashlib.sha256(lock).hexdigest() == receipt['lock_sha256'], receipt['lock_sha256'])
    check('working lock remains ignored', git(args.source, 'check-ignore', 'pixi.lock') == 'pixi.lock', '.gitignore')

    with (args.source/'data/paired.csv').open() as stream:
        rows = list(csv.DictReader(stream))
    known = [('A', 10, 11), ('B', 20, 21), ('C', 30, 32), ('D', 40, 42), ('E', 50, 53)]
    observed = [(r['participant'], float(r['before']), float(r['after'])) for r in rows]
    check('exact requested input', observed == known, 'data/paired.csv')
    result = json.loads((args.source/'results/summary.json').read_text())
    expected = {'n': 5, 'excluded': 0, 'df': 4, 'mean_change': 9/5,
                'sample_sd': math.sqrt(7/10), 'standard_error': math.sqrt(7/50),
                'ci_lower': 9/5 - 2.7764451051977987*math.sqrt(7/50),
                'ci_upper': 9/5 + 2.7764451051977987*math.sqrt(7/50)}
    check('independent arithmetic oracle', all(math.isfinite(result[k]) and math.isclose(result[k], v, rel_tol=0, abs_tol=1e-12) for k, v in expected.items()), expected)
    check('declared units and paired estimand', result['units'] == 'arbitrary units' and result['estimand'] == 'mean within-person change (after minus before)', result['estimand'])

    spec = importlib.util.spec_from_file_location('worker_analysis', args.source/'code/analyze.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    bad_inputs = {
        'duplicate_id': 'participant,before,after\nA,1,2\nA,2,3\n',
        'missing_id': 'participant,before,after\n,1,2\nB,2,3\n',
        'missing_value': 'participant,before,after\nA,1,NA\nB,2,3\n',
        'nonfinite': 'participant,before,after\nA,1,inf\nB,2,3\n',
        'nonnumeric': 'participant,before,after\nA,1,nope\nB,2,3\n',
        'singleton': 'participant,before,after\nA,1,2\n',
        'wrong_schema': 'participant,after,before\nA,2,1\nB,3,2\n',
    }
    with tempfile.TemporaryDirectory() as tmp:
        for name, content in bad_inputs.items():
            path = Path(tmp)/f'{name}.csv'
            path.write_text(content)
            rejected = False
            try:
                module.load_pairs(path)
            except (ValueError, TypeError):
                rejected = True
            check('reject '+name, rejected, content)

    check('ten absent annex payloads reported before retrieval', receipt['annex_files_absent_before_get'] == 10, 'delivery/receipt.json; replay.py absence assertions')
    check('ten delivered hashes match original', len(receipt['retrieved_payload_sha256']) == 10 and all(digest(args.source/p) == h for p, h in receipt['retrieved_payload_sha256'].items()), receipt['retrieved_payload_sha256'])
    check('five regenerated hashes independently match both checkouts', len(receipt['regenerated_sha256']) == 5 and all(digest(args.source/p) == digest(args.recipient/p) == h for p, h in receipt['regenerated_sha256'].items()), receipt['regenerated_sha256'])
    check('declared paths absent before rerun reported', receipt['declared_outputs_absent_before_rerun'], 'delivery/receipt.json; replay.py checkout/absence assertions')
    check('new native rerun commit', RERUN != RUN and git(args.recipient, 'rev-parse', RERUN+'^') == receipt['input_commit'], RERUN)
    for path, revision in [(args.source, RUN), (args.recipient, RERUN)]:
        message = git(path, 'show', '-s', '--format=%B', revision)
        record = json.loads(message.split('=== Do not change lines below ===\n', 1)[1].split('\n^^^ Do not change lines above ^^^', 1)[0])
        check('native record preserved '+revision[:7], message.startswith('[DATALAD RUNCMD] ') and record['cmd'] == 'pixi run analyze' and record['exit'] == 0 and {'results', 'logs'} <= set(record['outputs']), record)
        check('fresh provenance present '+revision[:7], 'Co-Authored-By: Codex Desktop ' in message and 'Codex-Reasoning-Effort: ' in message, revision)
    info = json.loads((args.source/'logs/paired/run_info.json').read_text())
    check('complete requested direct duct records', all((args.source/'logs/paired'/p).exists() for p in ['run_info.json','run_stdout','run_stderr','run_usage.jsonl','outer-summary.txt']) and info['execution_summary']['exit_code'] == 0 and 'Summary:' in (args.source/'logs/paired/outer-summary.txt').read_text(), 'logs/paired')
    commands = json.loads((here/'delivery/commands.json').read_text())
    check('retained successful delivery commands', all(c['exit_code'] == 0 for c in commands), len(commands))
    failed = json.loads((here/'delivery-failed/commands.json').read_text())
    check('failed abbreviated ref retained', any(c['exit_code'] == 128 and '472fbcf' in c['command'] for c in failed), 'delivery-failed/commands.json')
    manifest = json.loads((here/'snapshot-sha256.json').read_text())
    check('exact instruction snapshot retained', all(digest(here/'source-snapshot'/p) == h for p,h in manifest.items()), len(manifest))
    out = {'status': 'passed', 'task_commit': TASK, 'snapshot_commit': SNAPSHOT,
           'run_commit': RUN, 'rerun_commit': RERUN, 'checks': checks,
           'passed_checks': len(checks),
           'scope': 'Independent inspection and input-contract execution; original cold retrieval/rerun are retained worker evidence, not repeated by this grader.'}
    args.out.write_text(json.dumps(out, indent=2)+'\n')
    print(json.dumps({'status':out['status'], 'passed_checks':len(checks), 'output':str(args.out)}))


if __name__ == '__main__':
    main()
