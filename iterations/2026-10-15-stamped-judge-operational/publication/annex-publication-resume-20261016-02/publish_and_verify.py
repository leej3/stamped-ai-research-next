from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, subprocess, time

base = Path('/Users/johnlee/.local/state/stamped-ai-research-next/preparation-20261015')
evidence = base / 'annex-publication-resume-20261016-02'
source = base / 'cold-stamped-op-evidence/judgment-01/judgment'
receiver = base / 'cold-stamped-op-retention-retrieval'
manifest = base / 'cold-stamped-op-coordinator/pixi.toml'
expected_head = 'd87c492f8acc0d7193914032bb099d359310dc77'
rows = json.loads((base / 'cold-stamped-op-evidence/coordinator-actions/independent-retention-retrieval/result.json').read_text())['annex_keys']
pixi_git = ['pixi', 'run', '--manifest-path', str(manifest), 'git']
commands = []

def run(label, argv, cwd, timeout=300):
    start = datetime.now(timezone.utc).isoformat()
    clock = time.monotonic()
    rc, error = None, None
    try:
        p = subprocess.run(argv, cwd=cwd, capture_output=True, timeout=timeout)
        stdout, stderr, rc = p.stdout, p.stderr, p.returncode
    except subprocess.TimeoutExpired as exc:
        stdout, stderr, error = exc.stdout or b'', exc.stderr or b'', 'timeout'
    (evidence / (label + '.stdout.txt')).write_bytes(stdout)
    (evidence / (label + '.stderr.txt')).write_bytes(stderr)
    record = {'label': label, 'argv': argv, 'cwd': str(cwd), 'started_at': start,
              'elapsed_seconds': time.monotonic() - clock, 'timeout_seconds': timeout,
              'returncode': rc, 'error': error,
              'stdout': label + '.stdout.txt', 'stderr': label + '.stderr.txt'}
    commands.append(record)
    (evidence / 'commands.json').write_text(json.dumps(commands, indent=2) + '\n')
    assert rc == 0, record
    return stdout.decode()

def verify_files(root):
    verified = []
    for row in rows:
        path = root / row['file']
        data = path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        assert row['key'].split('--')[1] == digest + '.tar.gz'
        assert len(data) == int(row['bytesize'])
        verified.append({'path': row['file'], 'key': row['key'], 'bytes': len(data), 'sha256': digest})
    return verified

try:
    assert len(rows) == 3
    for label, root in [('source', source), ('receiver', receiver)]:
        assert run(label + '-head', ['git', 'rev-parse', 'HEAD'], root).strip() == expected_head
        assert not run(label + '-status-before', ['git', 'status', '--porcelain'], root).strip()
    annex_objects = receiver / '.git/annex/objects'
    object_files = [str(p.relative_to(receiver)) for p in annex_objects.rglob('*') if p.is_file()] if annex_objects.exists() else []
    assert not object_files
    assert not (receiver / '.git/objects/info/alternates').exists()
    assert all(not (receiver / row['file']).exists() for row in rows)
    source_files = verify_files(source)
    preflight = {'recorded_at': datetime.now(timezone.utc).isoformat(), 'source_head': expected_head,
                 'receiver_head': expected_head, 'empty_annex_store_before': True,
                 'receiver_annex_object_files_before': object_files, 'git_alternates': False,
                 'files': source_files, 'scope': 'Publication and retrieval only; no worker, judge or scientific replay execution.'}
    (evidence / 'preflight.json').write_text(json.dumps(preflight, indent=2) + '\n')
    paths = [row['file'] for row in rows]
    annex_head = run('source-annex-head', ['git', 'rev-parse', 'git-annex'], source).strip()
    run('publish-annex-metadata', ['git', 'push', 'git@github.com:leej3/stamped-ai-research-next.git', 'git-annex:refs/heads/codex/preparation-stamped-judgment-op-annex-20261015'], source)
    run('fetch-annex-metadata', ['git', 'fetch', 'origin', 'refs/heads/codex/preparation-stamped-judgment-op-annex-20261015:refs/remotes/origin/git-annex'], receiver)
    run('merge-annex-metadata', pixi_git + ['annex', 'merge'], receiver)
    run('get-three-archives', pixi_git + ['annex', 'get', '--from', 'con-hub', '--json', '--'] + paths, receiver)
    retrieved = verify_files(receiver)
    assert retrieved == source_files
    assert not run('receiver-status-after', ['git', 'status', '--porcelain'], receiver).strip()
    assert run('receiver-head-after', ['git', 'rev-parse', 'HEAD'], receiver).strip() == expected_head
    assert not run('source-status-after', ['git', 'status', '--porcelain'], source).strip()
    result = {'publication_success': True, 'annex_metadata_commit': annex_head,
              'copy_receipt': '../annex-publication-resume-20261016/copy-three-archives.stdout.txt', 'retrieval_success': True, 'head': expected_head,
              'empty_annex_store_before': True, 'git_alternates': False, 'clean': True,
              'files': retrieved, 'bytes': sum(r['bytes'] for r in retrieved),
              'scientific_result_unchanged': '8b5bcdaa999289a47f066ba829511d450301c573',
              'judgment_preservation_unchanged': 'e1b0ee05ad3406aede91ce1f62a092b48f30b40f',
              'scope': 'Independent repository with an empty local annex store on the same host; GitHub code and configured CON Hub payload endpoint. No science or replay execution.',
              'completed_at': datetime.now(timezone.utc).isoformat()}
    (evidence / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
except BaseException as exc:
    (evidence / 'failure.json').write_text(json.dumps({'type': type(exc).__name__, 'message': str(exc), 'recorded_at': datetime.now(timezone.utc).isoformat()}, indent=2) + '\n')
    raise
