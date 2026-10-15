"""Independent anonymous retrieval of the published blind trial's ten payloads."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = 'https://github.com/leej3/stamped-ai-research-next.git'
BRANCH = 'codex/proof-skill-followability'
REVISION = '9c15dfe23eb8ad03ac6420f381ca645a6c3dddda'
HUB = 'https://hub.centerforopenneuroscience.org/leej3/stamped-ai-research-next.git'
ENDPOINT = 'annex+https://hub.centerforopenneuroscience.org:443/git-annex-p2phttp'
EXPECTED = json.loads((HERE.parent / 'blind-001/delivery/receipt.json').read_text())['retrieved_payload_sha256']
if (HERE / 'receipt.json').exists():
    raise SystemExit('Receipt exists; preserve the completed attempt.')
recipient = Path(tempfile.mkdtemp(prefix='stamped-online-blind-')) / 'recipient'
result = dict(status='failed', source=SOURCE, branch=BRANCH, expected_revision=REVISION,
              recipient=str(recipient), metadata_source=HUB, files=[],
              authentication='Global and system Git configuration disabled; credential helpers empty; terminal/askpass prompts disabled',
              scope='Online GitHub clone, online CON Hub annex metadata and anonymous payload retrieval; no science rerun')
env = {key: value for key, value in os.environ.items() if not key.startswith('GIT_CONFIG_')}
env.update(GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL='/dev/null',
           GIT_TERMINAL_PROMPT='0', GIT_ASKPASS='/usr/bin/false')
commands = []


def run(*args, cwd=recipient):
    argv = ['git', '-c', 'credential.helper=', '-c', 'core.askPass=/usr/bin/false',
            '-c', 'user.name=Anonymous retrieval probe', '-c', 'user.email=codex@openai.com', *map(str, args)]
    print(json.dumps(dict(argv=argv, cwd=str(cwd))), flush=True)
    started = time.time()
    process = subprocess.run(argv, cwd=cwd, env=env, capture_output=True, text=True, timeout=120)
    number = len(commands) + 1
    (HERE / f'{number:03d}.stdout').write_text(process.stdout)
    (HERE / f'{number:03d}.stderr').write_text(process.stderr)
    commands.append(dict(argv=argv, cwd=str(cwd), returncode=process.returncode,
                         started_unix=started, elapsed_seconds=time.time()-started))
    (HERE / 'commands.json').write_text(json.dumps(commands, indent=2) + '\n')
    print(process.stdout, end='', flush=True)
    print(process.stderr, end='', flush=True)
    process.check_returncode()
    return process.stdout.strip()


try:
    if len(EXPECTED) != 10:
        raise RuntimeError('Expected exactly ten payloads')
    run('clone', '--single-branch', '--branch', BRANCH, SOURCE, recipient, cwd=recipient.parent)
    result['revision'] = run('rev-parse', 'HEAD')
    if result['revision'] != REVISION:
        raise RuntimeError('Published branch moved from the expected revision')
    run('annex', 'init', 'independent anonymous online blind-trial recipient')
    run('remote', 'add', 'con-hub', HUB)
    run('config', 'remote.con-hub.annexurl', ENDPOINT)
    run('fetch', 'con-hub', 'refs/heads/git-annex:refs/remotes/con-hub/git-annex')
    result['annex_metadata_revision'] = run('rev-parse', 'refs/remotes/con-hub/git-annex')
    run('annex', 'merge')
    absent = {name: (recipient / name).is_symlink() and not (recipient / name).exists() for name in EXPECTED}
    result['absent_before_get'] = absent
    if not all(absent.values()):
        raise RuntimeError('Every expected annex payload must be absent before retrieval')
    for name, expected in EXPECTED.items():
        key = run('annex', 'lookupkey', name)
        run('annex', 'get', '--from', 'con-hub', name)
        actual = hashlib.sha256((recipient / name).read_bytes()).hexdigest()
        result['files'].append(dict(path=name, key=key, expected_sha256=expected,
                                    actual_sha256=actual, match=expected == actual))
        if actual != expected:
            raise RuntimeError(f'Hash mismatch: {name}')
    result.update(status='passed', verified_payloads=len(result['files']))
except Exception as error:
    result['error'] = f'{type(error).__name__}: {error}'
finally:
    (HERE / 'receipt.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
raise SystemExit(0 if result['status'] == 'passed' else 1)
