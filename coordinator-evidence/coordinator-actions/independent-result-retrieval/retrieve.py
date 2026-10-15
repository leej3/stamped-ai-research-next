#!/usr/bin/env python3
"""Retrieve the single new published result and compare its original stop receipt."""
import collections
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.parse

ROOT = Path('/Users/johnlee/.local/state/stamped-ai-research-next/preparation-20261015')
DEST = ROOT / 'cold-stamped-independent-result'
EVIDENCE = ROOT / 'cold-stamped-evidence/coordinator-actions/independent-result-retrieval'
MANIFEST = ROOT / 'cold-stamped-coordinator/pixi.toml'
STOP = ROOT / 'cold-stamped-evidence/launch/native/worker-end-state.json'
HOST = Path('/Users/johnlee/.config/stamped-ai-research-next/launch.json')
RESULT = '8b5bcdaa999289a47f066ba829511d450301c573'
RESULT_REF = 'refs/heads/codex/preparation-stamped-result-20261015'
ANNEX_REF = 'refs/heads/codex/preparation-stamped-annex-result-20261015'
URL = 'git@github.com:leej3/stamped-ai-research-next.git'
commands = []
env = os.environ.copy()
env['GIT_TERMINAL_PROMPT'] = '0'
for key in list(env):
    if key.startswith('GIT_TRACE'):
        env.pop(key)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def save(name, data):
    (EVIDENCE / name).write_text(json.dumps(data, indent=2) + '\n')

def run(argv, cwd=DEST, required=True):
    number = len(commands) + 1
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    before = time.monotonic()
    proc = subprocess.run([str(a) for a in argv], cwd=cwd, env=env,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    record = {'number': number, 'argv': [str(a) for a in argv], 'cwd': str(cwd),
              'started_at': started, 'returncode': proc.returncode,
              'elapsed_seconds': time.monotonic() - before}
    for stream in ('stdout', 'stderr'):
        content = getattr(proc, stream)
        name = f'{number:02d}-{stream}.txt'
        (EVIDENCE / name).write_bytes(content)
        record[stream] = {'path': name, 'bytes': len(content), 'sha256': sha(content)}
    commands.append(record)
    save('commands.json', commands)
    print(f'command {number}: {argv[0]} returned {proc.returncode}', flush=True)
    if required and proc.returncode:
        raise RuntimeError(f'command {number} failed; retained logs identify details')
    return proc

def git(*args):
    return run(['git', *args])

def annex(*args):
    return run(['pixi', 'run', '--frozen', '--manifest-path', MANIFEST,
                'git', '-C', DEST, 'annex', *args])

def main():
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    if DEST.exists():
        raise RuntimeError('fresh destination already exists; refusing to replace it')
    stop = json.loads(STOP.read_text())
    if stop['head_commit'] != RESULT or stop['status_porcelain_v1_z_base64']:
        raise RuntimeError('stop receipt does not identify the expected clean result')
    host = json.loads(HOST.read_text())
    for name in ('annex_git_url', 'annex_url'):
        parsed = urllib.parse.urlsplit(host[name])
        if parsed.password or parsed.query or parsed.fragment:
            raise RuntimeError('unexpected potentially sensitive endpoint configuration')
    DEST.mkdir()
    git('init')
    git('config', 'core.hooksPath', '/dev/null')
    git('remote', 'add', 'origin', URL)
    git('config', '--unset-all', 'remote.origin.fetch')
    git('config', '--add', 'remote.origin.fetch', f'{RESULT_REF}:refs/remotes/origin/result')
    git('config', '--add', 'remote.origin.fetch', f'{ANNEX_REF}:refs/heads/git-annex')
    git('config', 'remote.origin.annex-ignore', 'true')
    git('config', 'remote.origin.tagOpt', '--no-tags')
    git('fetch', '--no-tags', '--no-recurse-submodules', '--depth=1', 'origin',
        f'{RESULT_REF}:refs/remotes/origin/result', f'{ANNEX_REF}:refs/heads/git-annex')
    actual = git('rev-parse', 'refs/remotes/origin/result').stdout.decode().strip()
    if actual != RESULT:
        raise RuntimeError('published result ref differs from the original stop receipt')
    metadata_commit = git('rev-parse', 'refs/heads/git-annex').stdout.decode().strip()
    git('checkout', '--detach', RESULT)
    index = git('ls-files', '--stage', '-z').stdout
    indexed = []
    for entry in index.split(b'\0'):
        if not entry:
            continue
        fields, path = entry.split(b'\t', 1)
        mode, obj, stage = fields.decode().split()
        indexed.append({'path': path.decode(), 'mode': mode, 'object_id': obj,
                        'stage': int(stage)})
    if indexed != stop['index']:
        raise RuntimeError('published result index differs from original stop receipt')
    expected = {x['path']: x for x in stop['worktree'] if x.get('annex_key')}
    preexisting = [p for p in expected if (DEST / p).exists()]
    if preexisting:
        raise RuntimeError('fresh repository unexpectedly contains annex payloads')
    if (DEST / '.git/objects/info/alternates').exists():
        raise RuntimeError('fresh repository unexpectedly has Git object alternates')
    save('pre-retrieval.json', {'result_commit': actual, 'metadata_commit': metadata_commit,
         'stop_receipt_sha256': sha(STOP.read_bytes()), 'index_matches': True,
         'annex_expected_path_count': len(expected), 'annex_payloads_present': preexisting,
         'git_object_alternates': False, 'coordinator_manifest_sha256': sha(MANIFEST.read_bytes()),
         'coordinator_lock_sha256': sha(MANIFEST.with_name('pixi.lock').read_bytes())})
    annex('version')
    annex('init', 'cold-stamped-independent-result-20261015')
    git('remote', 'add', 'con-hub', host['annex_git_url'])
    git('config', 'remote.con-hub.skipFetchAll', 'true')
    git('config', 'remote.con-hub.annexurl', host['annex_url'])
    annex('info', 'con-hub', '--json')
    listing = annex('find', '--anything', '--json').stdout.decode().splitlines()
    files = [json.loads(line) for line in listing if line.strip()]
    if {item['file'] for item in files} != set(expected):
        raise RuntimeError('annex inventory differs from original stop receipt')
    for item in files:
        if item['key'] != expected[item['file']]['annex_key']:
            raise RuntimeError('annex key differs from original stop receipt')
    save('required-annex-paths.json', files)
    annex('get', '--from=con-hub', '--json', '--', *sorted(expected))
    verified = []
    for path, item in sorted(expected.items()):
        target = DEST / path
        content = target.read_bytes()
        want = item['annex_content']
        verified.append({'path': path, 'annex_key': item['annex_key'],
             'bytes': len(content), 'sha256': sha(content),
             'matches_stop_receipt': want['available'] and len(content) == want['size']
                 and sha(content) == want['sha256'],
             'link_matches_stop_receipt': os.readlink(target) == item['link_target']})
    save('verified-annex-artifacts.json', verified)
    regular = []
    for item in stop['worktree']:
        if item['kind'] == 'file' and item.get('tracked'):
            content = (DEST / item['path']).read_bytes()
            regular.append({'path': item['path'], 'bytes': len(content), 'sha256': sha(content),
                            'matches_stop_receipt': sha(content) == item['sha256']
                                and len(content) == item['size']})
    save('verified-git-files.json', regular)
    end_head = git('rev-parse', 'HEAD').stdout.decode().strip()
    end_status = git('status', '--porcelain=v1', '--untracked-files=all').stdout.decode()
    refs = git('for-each-ref', '--format=%(refname) %(objectname)').stdout.decode().splitlines()
    passed = (all(x['matches_stop_receipt'] and x['link_matches_stop_receipt'] for x in verified)
              and all(x['matches_stop_receipt'] for x in regular)
              and end_head == RESULT and not end_status)
    outcome = {'schema_version': 1, 'passed': passed,
        'result_commit': RESULT, 'published_annex_metadata_commit': metadata_commit,
        'destination': str(DEST), 'source_remote': URL, 'result_ref': RESULT_REF,
        'annex_metadata_ref': ANNEX_REF, 'annex_content_source': 'con-hub',
        'annex_required_paths': len(expected), 'annex_retrieved_paths': len(verified),
        'annex_unique_keys': len({x['annex_key'] for x in verified}),
        'annex_verified_bytes': sum(x['bytes'] for x in verified),
        'annex_all_hashes_match_original_stop_receipt': all(x['matches_stop_receipt'] for x in verified),
        'git_regular_files_verified': len(regular), 'git_index_matches_original_stop_receipt': True,
        'all_git_regular_file_hashes_match_original_stop_receipt': all(x['matches_stop_receipt'] for x in regular),
        'end_head': end_head, 'end_status_porcelain': end_status, 'end_refs': refs,
        'stop_receipt_path': str(STOP), 'stop_receipt_sha256': sha(STOP.read_bytes()),
        'finished_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'limitations': ['Independent fresh repository and empty annex store on the same host; not a second-host test.',
                       'No scientific replay, worker environment resolution, source changes, source commits, pushes, or worker intervention.',
                       'Skills submodule left uninitialized; exact gitlink is covered by original stop-receipt index comparison.',
                       'Local git-annex initialization and retrieval update local annex bookkeeping only.']}
    save('result.json', outcome)
    print(json.dumps(outcome, indent=2), flush=True)
    if not passed:
        sys.exit(1)

if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        EVIDENCE.mkdir(parents=True, exist_ok=True)
        save('failure.json', {'error': str(exc), 'completed_commands': len(commands)})
        print(str(exc), file=sys.stderr)
        sys.exit(1)
