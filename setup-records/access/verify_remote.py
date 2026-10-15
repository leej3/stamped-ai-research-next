"""Fetch actual annex payloads into an independent anonymous recipient clone."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

SOURCE = 'https://hub.centerforopenneuroscience.org/leej3/stamped-ai-research-next.git'
PATHS = [
    'experiments/access/annex-probe.bin',
    'experiments/datalad-annex/outputs/statistics.tsv',
    'experiments/datalad-annex/outputs/figure.png',
]
root = Path(__file__).resolve().parents[2]
receipt = root / 'experiments/access/remote-retrieval.json'
if receipt.exists():
    raise SystemExit('Preserve existing receipt; choose a fresh path before repeating')
result = {'ok': False, 'source': SOURCE, 'authentication': 'credential helpers disabled', 'files': []}

def run(*args, cwd):
    command = ['git', '-c', 'credential.helper=', *args]
    print(json.dumps({'command': command, 'cwd': str(cwd)}), flush=True)
    p = subprocess.run(command, cwd=cwd, text=True, capture_output=True,
                       env={**os.environ, "GIT_TERMINAL_PROMPT": "0", "GIT_ASKPASS": "/usr/bin/false"})
    print(p.stdout, end='', flush=True)
    print(p.stderr, end='', flush=True)
    if p.returncode:
        raise RuntimeError(f'command exited {p.returncode}')
    return p.stdout.strip()

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

try:
    with tempfile.TemporaryDirectory(prefix='stamped-public-annex-') as parent:
        dest = Path(parent) / 'recipient'
        run('clone', SOURCE, str(dest), cwd=parent)
        result['revision'] = run('rev-parse', 'HEAD', cwd=dest)
        run('annex', 'init', 'independent anonymous retrieval check', cwd=dest)
        run('config', 'remote.origin.annexurl',
            'annex+https://hub.centerforopenneuroscience.org:443/git-annex-p2phttp', cwd=dest)
        for name in PATHS:
            target = dest / name
            if target.exists():
                raise RuntimeError(f'Payload unexpectedly already available: {name}')
            expected = digest(root / name)
            key = run('annex', 'lookupkey', name, cwd=dest)
            run('annex', 'get', '--from', 'origin', name, cwd=dest)
            actual = digest(target)
            result['files'].append({'path': name, 'key': key, 'expected_sha256': expected,
                                    'actual_sha256': actual, 'match': actual == expected})
            if actual != expected:
                raise RuntimeError(f'Hash mismatch: {name}')
        result['ok'] = True
except Exception as e:
    result['error'] = f'{type(e).__name__}: {e}'
finally:
    receipt.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
raise SystemExit(0 if result['ok'] else 1)
