#!/usr/bin/env python3
"""Host-only readiness probes; every operation and scope is retained locally."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import uuid

BASE = Path('/Users/johnlee/.local/state/stamped-ai-research-next/preparation-20261015')
MANIFEST = Path('/Users/johnlee/code/CON/stamped-ai-research-next/pixi.toml')
TRIAL = BASE / 'coordinator-trial-02'
CHECKPOINT = '01M50SK1726HDTHJHVPPS8WED8'
SESSION = '01a14197-3860-72f0-8fbd-7f5bcec167cf'
CODE = 'baa6cf9bb823db2068453db71d822afc6e013667'
BRANCH = 'codex/coordinator-trial-20261015'
SSH_REMOTE = 'git@github.com:leej3/stamped-ai-research-next.git'


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


class Probe:
    def __init__(self, name):
        self.artifacts = Path(os.environ['READINESS_ARTIFACT_DIR']).resolve()
        self.commands = []
        self.started = time.monotonic()
        self.report = {
            'schema_version': 1, 'check': name, 'started_at': now(),
            'passed': False, 'observations': {}, 'sources': [], 'limitations': [],
        }
        shutil.copyfile(__file__, self.artifacts / 'probe.py')
        (self.artifacts / 'commands').mkdir()
        dump(self.artifacts / 'commands.json', self.commands)
        dump(self.artifacts / 'verification.json', self.report)

    def require(self, value, message):
        if not value:
            raise ValueError(message)

    def source(self, path):
        data = path.read_bytes()
        self.report['sources'].append({'path': str(path), 'sha256': sha(data), 'bytes': len(data)})
        return json.loads(data)

    def run(self, argv, cwd=None, allowed=(0,), timeout=45):
        argv = [str(x) for x in argv]
        directory = Path(cwd or self.artifacts).resolve()
        sequence = len(self.commands) + 1
        prefix = f'commands/{sequence:03d}'
        entry = {'argv': argv, 'cwd': str(directory), 'started_at': now(),
                 'stdout': prefix + '.stdout.txt', 'stderr': prefix + '.stderr.txt'}
        self.commands.append(entry)
        dump(self.artifacts / 'commands.json', self.commands)
        started = time.monotonic()
        try:
            response = subprocess.run(argv, cwd=directory, capture_output=True, timeout=timeout)
            stdout, stderr = response.stdout, response.stderr
            entry['returncode'] = response.returncode
        except subprocess.TimeoutExpired as error:
            stdout, stderr = error.stdout or b'', error.stderr or b''
            entry.update(returncode=None, error=f'Command timed out after {timeout} seconds')
        except OSError as error:
            stdout, stderr = b'', str(error).encode()
            entry.update(returncode=None, error=str(error))
        for name, data in (('stdout', stdout), ('stderr', stderr)):
            (self.artifacts / entry[name]).write_bytes(data)
            entry[name + '_sha256'] = sha(data)
            entry[name + '_bytes'] = len(data)
        entry.update(finished_at=now(), elapsed_seconds=time.monotonic() - started)
        dump(self.artifacts / 'commands.json', self.commands)
        self.require(entry['returncode'] in allowed, f'Command {sequence} failed: {entry.get("error", entry["returncode"])}')
        return stdout.decode('utf-8'), entry['returncode']

    def git(self, repo, *args, **kwargs):
        return self.run(['git', '-C', repo, *args], **kwargs)[0].strip()

    def annex(self, repo, *args, **kwargs):
        return self.run(['pixi', 'run', '--locked', '--manifest-path', MANIFEST,
                         'git', '-C', repo, 'annex', *args], **kwargs)[0].strip()

    def finish(self, error=None):
        self.report.update(finished_at=now(), elapsed_seconds=time.monotonic() - self.started,
                           passed=error is None)
        if error is not None:
            self.report['error'] = str(error)
        dump(self.artifacts / 'verification.json', self.report)
        print(json.dumps({'check': self.report['check'], 'passed': self.report['passed'],
                          'verification': str(self.artifacts / 'verification.json'),
                          'error': self.report.get('error')}))
        return 0 if error is None else 1


def native(p):
    p.report['limitations'] = [
        'Re-verifies the existing coordinator-trial native session, not a new scientific worker or every future checkout.',
        'Current remote reads establish availability and matching identities now; no new code/checkpoint publication is attempted.',
    ]
    saved = p.source(BASE / 'native-capture-investigation-01/local-checkpoint.json')
    launch = p.source(BASE / 'cold-coordinator-02/launch.json')
    result = p.source(BASE / 'cold-coordinator-02/result.json')
    inventory = p.source(BASE / 'native-capture-investigation-01/native-event-inventory.json')
    p.require(Path(launch['checkout']) == TRIAL and result['returncode'] == 0,
              'Original native session did not complete successfully in the expected checkout')
    p.require(inventory['session_id'] == SESSION and inventory['commit'] == CODE,
              'Original native inventory identity mismatch')
    event_bytes = (BASE / 'cold-coordinator-02/events.jsonl').read_bytes()
    events = [json.loads(line) for line in event_bytes.splitlines() if line.strip()]
    session_ids = {event.get('thread_id') for event in events if event.get('type') == 'thread.started'}
    p.require(SESSION in session_ids, 'Expected native session absent from original command stream')
    p.require(any(event.get('type') == 'turn.completed' for event in events),
              'Original native event stream lacks completed turn')
    p.report['sources'].append({'path': str(BASE / 'cold-coordinator-02/events.jsonl'),
                                'sha256': sha(event_bytes), 'bytes': len(event_bytes)})
    p.require(p.git(TRIAL, 'rev-parse', 'HEAD') == CODE, 'Trial checkout no longer at recorded code commit')
    message = p.git(TRIAL, 'show', '-s', '--format=%B', CODE)
    p.require(f'Entire-Checkpoint: {CHECKPOINT}' in message, 'Code commit lacks matching checkpoint trailer')
    p.git(TRIAL, 'cat-file', '-e', CODE + ':coordinator-trial.md')
    checkpoint_ref = f'refs/entire/checkpoints/{CHECKPOINT[-2:]}/{CHECKPOINT}'
    checkpoint_commit = p.git(TRIAL, 'rev-parse', checkpoint_ref)
    refs, _ = p.run(['git', 'ls-remote', SSH_REMOTE, 'refs/heads/' + BRANCH, checkpoint_ref], cwd=TRIAL)
    remote = {line.split()[1]: line.split()[0] for line in refs.splitlines() if line.strip()}
    p.require(remote.get('refs/heads/' + BRANCH) == CODE, 'Published code ref does not match trial code commit')
    p.require(remote.get(checkpoint_ref) == checkpoint_commit, 'Published checkpoint ref mismatch or absent')
    hosted_text, _ = p.run(['/opt/homebrew/bin/entire', 'checkpoint', 'explain', CHECKPOINT,
                             '--repo', 'gh/leej3/stamped-ai-research-next', '--json'], cwd=TRIAL)
    hosted = json.loads(hosted_text)
    p.require(hosted['checkpoint_id'] == saved['checkpoint_id'] == CHECKPOINT,
              'Hosted checkpoint identity mismatch')
    p.require(hosted['branch'] == saved['branch'] == BRANCH, 'Hosted branch mismatch')
    actual_sessions = {x['session_id']: x for x in hosted['sessions']}
    saved_sessions = {x['session_id']: x for x in saved['sessions']}
    p.require(SESSION in actual_sessions and SESSION in saved_sessions, 'Hosted native session absent')
    fields = ('agent', 'model', 'created_at', 'turn_id', 'files_touched')
    p.require(all(actual_sessions[SESSION][key] == saved_sessions[SESSION][key] for key in fields),
              'Hosted native session metadata differs from saved local metadata')
    p.require('coordinator-trial.md' in actual_sessions[SESSION]['files_touched'], 'Expected touched file absent')
    p.report['observations'] = {
        'checkout': str(TRIAL), 'code_commit': CODE, 'checkpoint_id': CHECKPOINT,
        'checkpoint_ref': checkpoint_ref, 'checkpoint_commit': checkpoint_commit,
        'session_id': SESSION, 'remote_refs': remote,
        'native_turn_completed': True, 'hosted_metadata_matches': True,
    }


def annex_round_trip(p):
    p.report['limitations'] = [
        'Tests a tiny new synthetic artifact on the configured CON Hub store; does not establish capacity, throughput, or all study inputs.',
        'Retains original and new artifacts and repositories. No remote Git branch publication is needed for content transfer.',
    ]
    old = p.source(BASE / 'annex-roundtrip.json')
    old_path = BASE / 'annex-recipient/annex-roundtrip.txt'
    old_bytes = old_path.read_bytes()
    p.require(len(old_bytes) == old['bytes'] and sha(old_bytes) == old['sha256'],
              'Existing independent recipient bytes differ from retained round-trip receipt')
    old_key = p.annex(old_path.parent, 'lookupkey', '--', old_path.name)
    p.require(old_key == old['annex_key'], 'Existing recipient key differs from receipt')
    remote_url = 'https://hub.centerforopenneuroscience.org/leej3/stamped-ai-research-next.git'
    annex_url = 'annex+https://hub.centerforopenneuroscience.org:443/git-annex-p2phttp'
    remote_uuid = '6215ce45-8f0f-4062-9bc0-d04781b4cd11'
    p.require(any(remote_url in cmd['argv'] for cmd in old['commands']), 'Remote not supported by existing receipt')
    p.require(any(annex_url in cmd['argv'] for cmd in old['commands']), 'Annex endpoint not supported by existing receipt')
    p.require(any(remote_uuid in cmd['argv'] for cmd in old['commands']), 'Annex store UUID not supported by existing receipt')
    working = BASE / ('annex-readiness-' + uuid.uuid4().hex)
    working.mkdir(mode=0o700)
    donor, recipient = working / 'donor', working / 'recipient'
    for repo in (donor, recipient):
        repo.mkdir(mode=0o700)
        p.git(repo, 'init', '--quiet')
        p.annex(repo, 'init', 'readiness-' + repo.name)
        p.git(repo, 'remote', 'add', 'con-hub', remote_url)
        p.git(repo, 'config', 'remote.con-hub.annexurl', annex_url)
        p.git(repo, 'config', 'remote.con-hub.annex-uuid', remote_uuid)
    payload = (json.dumps({'purpose': 'STAMPED readiness round trip', 'created_at': now(),
                           'nonce': str(uuid.uuid4())}, sort_keys=True) + '\n').encode()
    name = 'readiness-artifact.json'
    (donor / name).write_bytes(payload)
    (p.artifacts / 'payload.json').write_bytes(payload)
    p.annex(donor, 'add', '--backend=SHA256E', '--force', '--', name)
    key = p.annex(donor, 'lookupkey', '--', name)
    p.require(key.startswith(f'SHA256E-s{len(payload)}--{sha(payload)}'), 'New annex key does not match artifact bytes')
    p.annex(donor, 'copy', '--to', 'con-hub', '--', name, timeout=90)
    p.annex(donor, 'checkpresentkey', key, 'con-hub')
    p.annex(recipient, 'fromkey', '--force', key, name)
    p.require(not (recipient / name).exists(), 'Recipient unexpectedly had payload before remote transfer')
    p.require(not (recipient / '.git/objects/info/alternates').exists(), 'Recipient shares a Git object store')
    donor_uuid = p.git(donor, 'config', 'annex.uuid')
    recipient_uuid = p.git(recipient, 'config', 'annex.uuid')
    p.require(donor_uuid and recipient_uuid and donor_uuid != recipient_uuid, 'Donor and recipient are not independent annex repositories')
    p.annex(recipient, 'transferkey', key, '--from', 'con-hub', timeout=90)
    actual = (recipient / name).read_bytes()
    p.require(actual == payload, 'Independent remote retrieval bytes differ')
    p.require((recipient / name).resolve().is_relative_to(recipient / '.git/annex/objects'),
              'Recipient payload resolves outside its independent annex store')
    p.report['observations'] = {
        'old_receipt_bytes_reverified': len(old_bytes), 'old_receipt_sha256': sha(old_bytes),
        'new_payload_bytes': len(payload), 'new_payload_sha256': sha(payload), 'annex_key': key,
        'donor': str(donor), 'recipient': str(recipient), 'donor_uuid': donor_uuid,
        'recipient_uuid': recipient_uuid, 'recipient_payload': str((recipient / name).resolve()),
        'new_upload_command_succeeded': True, 'remote_presence_rechecked': True,
        'recipient_absent_before_transfer': True, 'independent_bytes_identical': True,
    }


def hpc(p):
    p.report['limitations'] = [
        'Re-verifies existing job 65726805; submits no new job and writes no remote files.',
        'Demonstrates this small CPU scheduler/output path, not scientific workload performance, queue time, or dependency readiness.',
    ]
    submission = p.source(BASE / 'hpc-submit.json')
    prior = p.source(BASE / 'hpc-verify.json')
    job = '65726805'
    p.require(submission['returncode'] == 0 and submission['stdout'].strip() == job and prior['job_id'] == job,
              'Original submission and job identity missing or inconsistent')
    remote_directory = submission['remote_directory']
    p.require(re.fullmatch(r'/work/[A-Za-z0-9_/-]+', remote_directory), 'Unexpected remote directory')
    ssh = ['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=10', 'unity']
    accounting, _ = p.run(ssh + ['sacct -n -P -j ' + job + ' --format=JobIDRaw,State,ExitCode,Elapsed,NodeList'])
    records = [line.split('|') for line in accounting.splitlines() if line.strip()]
    matches = [row for row in records if row[0] == job]
    p.require(len(matches) == 1 and matches[0][1] == 'COMPLETED' and matches[0][2] == '0:0',
              'Current sacct does not prove successful completion of the requested job')
    output, _ = p.run(ssh + ['cat ' + remote_directory + '/job-' + job + '.out'])
    errors, _ = p.run(ssh + ['cat ' + remote_directory + '/job-' + job + '.err'])
    lines = output.splitlines()
    p.require(len(lines) == 2 and lines[1] == 'stamped-readiness-ok', 'Completed job output marker missing or unexpected')
    p.require(lines[0] == matches[0][4], 'Job hostname and accounting node do not match')
    p.require(not errors.strip(), 'Job stderr is nonempty')
    p.report['observations'] = {'job_id': job, 'scheduler_record': matches[0],
                                'remote_directory': remote_directory, 'output': lines,
                                'stderr_empty': True, 'new_jobs_submitted': 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('check', choices=('native-capture', 'annex-round-trip', 'hpc-round-trip'))
    args = parser.parse_args()
    p = Probe(args.check)
    functions = {'native-capture': native, 'annex-round-trip': annex_round_trip, 'hpc-round-trip': hpc}
    try:
        functions[args.check](p)
    except Exception as error:
        return p.finish(error)
    return p.finish()


if __name__ == '__main__':
    sys.exit(main())
