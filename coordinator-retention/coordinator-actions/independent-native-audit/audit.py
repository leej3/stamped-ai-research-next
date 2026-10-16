#!/usr/bin/env python3
"""Audit a specific stored native shell write without replaying that command.

Read-only with respect to the judgment repository and external services. This
specialized proof does not alter or replace the stock native-capture verifier.
Only selected command events are retained; raw transcript and reasoning are not.
"""
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote, urlparse

BASE = Path('/Users/johnlee/.local/state/stamped-ai-research-next/preparation-20261015')
ROOT = BASE / 'cold-stamped-op-evidence/judgment-01/judgment'
OUT = Path(__file__).resolve().parent
COMMIT = 'e1b0ee05ad3406aede91ce1f62a092b48f30b40f'
SESSION = '01a14201-b7c3-7281-bcc6-cfe90c4b16a9'
CHECKPOINT = '01M510JADWN8W7J9GF1T3BQB04'
CODE_REF = 'refs/heads/codex/preparation-stamped-judgment-op-20261015'
CHECKPOINT_REF = 'refs/entire/checkpoints/04/' + CHECKPOINT
CHECKPOINT_OID = '8827b6eeaa95a0a7f5e8cca1d4da18377515c2ff'
FILE = '2026-10-16-remote-check.txt'
COMMANDS = []


def digest(data):
    return hashlib.sha256(data).hexdigest()


def call(argv, cwd=ROOT, allow_failure=False):
    p = subprocess.run(argv, cwd=cwd, capture_output=True, check=False)
    COMMANDS.append({'argv': argv, 'cwd': str(cwd), 'exit_code': p.returncode,
                     'stdout_bytes': len(p.stdout), 'stdout_sha256': digest(p.stdout),
                     'stderr_bytes': len(p.stderr), 'stderr_sha256': digest(p.stderr)})
    if p.returncode and not allow_failure:
        raise RuntimeError('Read-only command failed: ' + repr(argv))
    return p if allow_failure else p.stdout


def save(name, data):
    path = OUT / name
    with path.open('x') as f:
        f.write(json.dumps(data, indent=2) + '\n')


def cwd_path(value):
    if value.startswith('file:'):
        parsed = urlparse(value)
        assert parsed.netloc in ('', 'localhost')
        value = unquote(parsed.path)
    return Path(value).resolve()


def completed(row):
    payload = row.get('payload', {})
    event = payload.get('item', {})
    if (row.get('type') == 'event_msg' and payload.get('type') == 'item_completed'
            and isinstance(event, dict)
            and event.get('type') in ('CommandExecution', 'command_execution')
            and event.get('status') == 'completed' and event.get('exit_code') == 0):
        return event
    return None


def main():
    if (OUT / 'result.json').exists():
        raise SystemExit('Existing audit result must be preserved')
    started = datetime.now(timezone.utc).isoformat()
    before = {'head': call(['git', 'rev-parse', 'HEAD']).decode().strip(),
              'branch': call(['git', 'symbolic-ref', 'HEAD']).decode().strip(),
              'status': call(['git', 'status', '--porcelain=v1', '-z']).decode(),
              'refs_sha256': digest(call(['git', 'for-each-ref', '--format=%(refname) %(objectname)']))}
    call(['git', 'merge-base', '--is-ancestor', COMMIT, before['head']])
    assert before['branch'] == 'refs/heads/codex/judgment'
    assert before['status'] == ''
    local = json.loads(call(['entire', 'checkpoint', 'explain', '--commit', COMMIT, '--json']))
    assert local['checkpoint_id'] == CHECKPOINT
    sessions = [s for s in local['sessions'] if s['session_id'] == SESSION]
    assert len(sessions) == 1
    native = sessions[0]
    assert native['agent'].lower() == 'codex' and native['model'] == 'gpt-6-luna'
    assert FILE in native['files_touched']
    raw = call(['entire', 'checkpoint', 'explain', '--commit', COMMIT, '--transcript',
                '--session-index', str(native['index'])])
    rows = [(i, json.loads(line)) for i, line in enumerate(raw.splitlines(), 1)]
    identities = [{'line': i, **{k: r['payload'].get(k) for k in ('id', 'cwd', 'source', 'cli_version')}}
                  for i, r in rows if r.get('type') == 'session_meta']
    assert len(identities) == 1 and identities[0]['id'] == SESSION
    assert cwd_path(identities[0]['cwd']) == ROOT.resolve()
    contexts = [{'line': i, **{k: r['payload'].get(k) for k in ('cwd', 'model', 'effort')}}
                for i, r in rows if r.get('type') == 'turn_context']
    assert contexts and all(cwd_path(c['cwd']) == ROOT.resolve()
                            and c['model'] == 'gpt-6-luna' and c['effort'] == 'high'
                            for c in contexts)
    events = [(i, e) for i, r in rows if (e := completed(r)) is not None]
    env_command = (
        "printf 'TARGET=%s\\nOUTPUT=%s\\nRUNNER=%s\\nPYTHON=%s\\n' "
        '"$STAMPED_JUDGE_TARGET" "$STAMPED_JUDGE_OUTPUT" '
        '"$STAMPED_ASSESSMENT_RUNNER" "$STAMPED_ASSESSMENT_PYTHON"\n'
        'git -C "$STAMPED_JUDGE_TARGET" rev-parse HEAD\npwd\n')
    env_matches = [(i, e) for i, e in events
                   if e.get('command') == ['/opt/homebrew/bin/bash', '-lc', env_command]]
    assert len(env_matches) == 1
    env_line, env = env_matches[0]
    env_output = env['aggregated_output'].splitlines()
    expected_target = str(BASE / 'cold-stamped-op-judge-target')
    expected_runner = str(BASE / 'cold-stamped-op-coordinator/scripts/assessment.py')
    expected_python = str(BASE / 'cold-stamped-op-coordinator/.pixi/envs/default/bin/python')
    assert env_output == [
        'TARGET=' + expected_target, 'OUTPUT=' + str(ROOT),
        'RUNNER=' + expected_runner, 'PYTHON=' + expected_python,
        '8b5bcdaa999289a47f066ba829511d450301c573', str(ROOT)]
    assert cwd_path(env['cwd']) == ROOT.resolve()
    write_command = (
        'git -C "$STAMPED_JUDGE_TARGET" ls-remote --heads con-hub > '
        '"$STAMPED_JUDGE_OUTPUT/2026-10-16-remote-check.txt"\n'
        'git -C "$STAMPED_JUDGE_TARGET" remote -v >> '
        '"$STAMPED_JUDGE_OUTPUT/2026-10-16-remote-check.txt"\n'
        'cat "$STAMPED_JUDGE_OUTPUT/2026-10-16-remote-check.txt"\n')
    write_matches = [(i, e) for i, e in events
                     if e.get('command') == ['/opt/homebrew/bin/bash', '-lc', write_command]]
    assert len(write_matches) == 1
    write_line, write = write_matches[0]
    assert write_line > env_line and cwd_path(write['cwd']) == ROOT.resolve()
    # No transcript command is executed. The final cat output is compared as
    # recorded, including every tab and newline, with the immutable Git blob.
    readback = write['aggregated_output'].encode('utf-8')
    blob = call(['git', 'show', COMMIT + ':' + FILE])
    assert readback == blob and blob == (ROOT / FILE).read_bytes()
    changed = call(['git', 'diff-tree', '--root', '--no-commit-id', '--name-only', '-z', '-r', COMMIT]).split(b'\0')
    assert FILE.encode() in changed
    message = call(['git', 'show', '-s', '--format=%B', COMMIT]).decode()
    assert 'Co-Authored-By: Codex Desktop ' in message and 'Codex-Reasoning-Effort: ' in message
    local_refs = {ref: call(['git', 'rev-parse', ref]).decode().strip()
                  for ref in (CODE_REF, CHECKPOINT_REF)}
    expected_refs = {CODE_REF: COMMIT, CHECKPOINT_REF: CHECKPOINT_OID}
    assert local_refs == expected_refs
    remote = call(['git', 'remote', 'get-url', '--push', 'origin']).decode().strip()
    assert remote == 'git@github.com:leej3/stamped-ai-research-next.git'
    remote_raw = call(['git', 'ls-remote', '--refs', remote, CODE_REF, CHECKPOINT_REF])
    remote_refs = {ref: oid for oid, ref in (line.split() for line in remote_raw.decode().splitlines())}
    assert remote_refs == expected_refs
    hosted_args = ['entire', 'checkpoint', 'explain', CHECKPOINT,
                   '--repo', 'gh/leej3/stamped-ai-research-next', '--json']
    ambiguous_hosted = json.loads(call(hosted_args))
    outside = Path('/tmp').resolve()
    git_context = call(['git', 'rev-parse', '--show-toplevel'], cwd=outside, allow_failure=True)
    assert git_context.returncode != 0 and not git_context.stdout
    hosted_attempt = call(hosted_args, cwd=outside, allow_failure=True)
    try:
        hosted = json.loads(hosted_attempt.stdout)
    except (ValueError, UnicodeError):
        hosted = {}
    hosted_sessions = [s for s in hosted.get('sessions', []) if s.get('session_id') == SESSION]
    hosted_verified = bool(hosted_attempt.returncode == 0
        and hosted.get('checkpoint_id') == CHECKPOINT and len(hosted_sessions) == 1
        and hosted_sessions[0].get('model') == 'gpt-6-luna'
        and hosted_sessions[0].get('agent', '').lower() == 'codex'
        and FILE in hosted_sessions[0].get('files_touched', []))
    after = {'head': call(['git', 'rev-parse', 'HEAD']).decode().strip(),
             'branch': call(['git', 'symbolic-ref', 'HEAD']).decode().strip(),
             'status': call(['git', 'status', '--porcelain=v1', '-z']).decode(),
             'refs_sha256': digest(call(['git', 'for-each-ref', '--format=%(refname) %(objectname)']))}
    assert before == after
    save('local-checkpoint.json', local)
    save('hosted-ambiguous-inside-repository.json', {
        'status': 'ambiguous-not-proof', 'cwd': str(ROOT), 'argv': hosted_args,
        'reason': 'The CLI can return local checkpoint metadata inside a Git checkout despite --repo.',
        'metadata': ambiguous_hosted})
    save('hosted-outside-repository.json', {
        'cwd': str(outside), 'argv': hosted_args, 'exit_code': hosted_attempt.returncode,
        'git_context_exit_code': git_context.returncode,
        'git_context_stderr': git_context.stderr.decode(),
        'stdout': hosted_attempt.stdout.decode(), 'stderr': hosted_attempt.stderr.decode(),
        'metadata': hosted, 'verified': hosted_verified})
    save('remote-refs.json', {'remote': remote, 'expected': expected_refs, 'observed': remote_refs})
    save('selected-native-evidence.json', {
        'transcript_source': 'Entire stored checkpoint transcript, session index 0',
        'transcript_sha256': digest(raw), 'transcript_bytes': len(raw),
        'identities': identities, 'turn_contexts': contexts,
        'completed_events': [{'line': env_line, 'event': env}, {'line': write_line, 'event': write}],
        'raw_transcript_saved': False, 'reasoning_saved': False})
    save('commands.json', COMMANDS)
    result = {
        'started_at': started, 'verified_at': datetime.now(timezone.utc).isoformat(),
        'audit_method': 'Independent specific-command inspection and byte comparison; no transcript command replay',
        'checkout': str(ROOT), 'commit': COMMIT, 'session_id': SESSION,
        'checkpoint_id': CHECKPOINT, 'checkpoint_ref': CHECKPOINT_REF,
        'checkpoint_oid': CHECKPOINT_OID, 'code_ref': CODE_REF,
        'native_capture_verified': True, 'uploaded_refs_verified': True, 'hosted_verified': hosted_verified,
        'statuses': {'local_native_capture': 'verified', 'github_checkpoint_sync': 'verified',
                     'entire_hosted_visibility': 'verified' if hosted_verified else 'blocked'},
        'native_model': 'gpt-6-luna', 'native_reasoning_effort': 'high',
        'file': FILE, 'file_bytes': len(blob), 'file_sha256': digest(blob),
        'completed_readback_equals_committed_blob': True,
        'working_file_equals_committed_blob': True,
        'file_present_in_commit_diff': True,
        'environment_observation_line': env_line, 'completed_write_and_read_line': write_line,
        'transcript_bytes': len(raw), 'transcript_sha256': digest(raw),
        'raw_transcript_saved': False, 'reasoning_saved': False,
        'repository_before': before, 'repository_after': after,
        'repository_head_branch_status_refs_unchanged': True,
        'limitations': [
            'The stock verifier did not recognize this variable-based compound shell command. Its rejection remains unchanged; this is a separate specific-command audit, not a stock-verifier success.',
            'The output directory variable was observed at session startup. The write event records cwd and the literal variable-based command, not a separate environment snapshot. Matching the successful cat output byte-for-byte to the committed file corroborates that mapping.',
            'The compound command lacks errexit: exit 0 proves the final cat succeeded, not each preceding Git subcommand independently. The exact recorded six-line readback is preserved and equals the committed file.',
            'This confirms native capture and publication of the remote-check artifact. It does not establish scientific correctness, successful replay, data availability, or compliance with the replay-attempt limit.',
            'The inside-repository --repo lookup is ambiguous and excluded from hosted proof. Hosted visibility is evaluated separately through Entire checkpoint explain from a verified non-Git /tmp context; no hosted raw-transcript or visual dashboard retrieval was performed.'
        ],
        'audit_script_sha256': digest(Path(__file__).read_bytes())
    }
    save('result.json', result)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
