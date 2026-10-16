#!/usr/bin/env python3
"""Confirm hosted metadata from a newly initialized repository with no objects.

Entire 0.11.4 requires a Git cwd even when --repo selects a hosted repository.
No commits, remotes, checkpoint refs, copied credentials, or configuration are
created. Existing user-level Entire authentication supplies the remote request.
"""
import hashlib
import json
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parent
CHECKPOINT = '01M510JADWN8W7J9GF1T3BQB04'
SESSION = '01a14201-b7c3-7281-bcc6-cfe90c4b16a9'
FILE = '2026-10-16-remote-check.txt'
env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
removed_names = sorted(k for k in os.environ if k.startswith('GIT_'))
commands = []


def run(argv, cwd):
    p = subprocess.run(argv, cwd=cwd, env=env, capture_output=True, text=True, check=False)
    commands.append({'argv': argv, 'cwd': str(cwd), 'exit_code': p.returncode,
                     'stdout': p.stdout, 'stderr': p.stderr})
    return p


def state(cwd):
    result = {}
    for key, args in (
            ('refs', ['git', 'for-each-ref', '--format=%(refname) %(objectname)']),
            ('remotes', ['git', 'remote', '-v']),
            ('objects', ['git', 'count-objects', '-v']),
            ('head', ['git', 'rev-parse', '--verify', 'HEAD'])):
        p = run(args, cwd)
        result[key] = {'exit_code': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr}
    assert result['refs']['exit_code'] == 0 and not result['refs']['stdout']
    assert result['remotes']['exit_code'] == 0 and not result['remotes']['stdout']
    assert result['head']['exit_code'] != 0
    counts = dict(line.split(': ', 1) for line in result['objects']['stdout'].splitlines())
    assert counts['count'] == '0' and counts['in-pack'] == '0'
    return result


def main():
    output = OUT / 'hosted-empty-repository.json'
    if output.exists():
        raise SystemExit('Existing receipt must be preserved')
    scratch = Path(tempfile.mkdtemp(prefix='stamped-judge-hosted-audit-', dir='/private/tmp'))
    initialized = run(['git', 'init', '--quiet'], scratch)
    assert initialized.returncode == 0
    before = state(scratch)
    lookup = run(['entire', 'checkpoint', 'explain', CHECKPOINT,
                  '--repo', 'gh/leej3/stamped-ai-research-next', '--json'], scratch)
    after = state(scratch)
    assert before == after
    try:
        metadata = json.loads(lookup.stdout)
    except ValueError:
        metadata = {}
    sessions = [s for s in metadata.get('sessions', []) if s.get('session_id') == SESSION]
    verified = bool(lookup.returncode == 0 and metadata.get('checkpoint_id') == CHECKPOINT
                    and len(sessions) == 1 and sessions[0].get('model') == 'gpt-6-luna'
                    and sessions[0].get('agent', '').lower() == 'codex'
                    and FILE in sessions[0].get('files_touched', []))
    result = {
        'verified_at': datetime.now(timezone.utc).isoformat(),
        'hosted_verified': verified, 'checkpoint_id': CHECKPOINT, 'session_id': SESSION,
        'requested_hosted_repository': 'gh/leej3/stamped-ai-research-next',
        'empty_git_context': str(scratch), 'removed_git_environment_variable_names': removed_names,
        'before': before, 'after': after, 'commands': commands, 'metadata': metadata,
        'local_metadata_fallback_excluded': True,
        'reason': 'The scratch repository has no commits, Git objects, refs, remotes, or local Entire checkpoint data before or after the query.',
        'raw_transcript_requested': False,
        'audit_script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    }
    with output.open('x') as f:
        f.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
