#!/usr/bin/env python3
"""Continue the guarded retrieval, including unlocked annex files in the receipt."""
import datetime
import json
import os
import sys
import retrieve as r

def main():
    r.commands = json.loads((r.EVIDENCE / 'commands.json').read_text())
    prior = json.loads((r.EVIDENCE / 'pre-retrieval.json').read_text())
    stop = json.loads(r.STOP.read_text())
    if prior['result_commit'] != r.RESULT or prior['stop_receipt_sha256'] != r.sha(r.STOP.read_bytes()):
        raise RuntimeError('pre-retrieval identity mismatch')
    if r.git('rev-parse', 'HEAD').stdout.decode().strip() != r.RESULT:
        raise RuntimeError('destination head changed')
    listing = r.annex('find', '--anything', '--json').stdout.decode().splitlines()
    files = [json.loads(line) for line in listing if line.strip()]
    available_before = r.annex('find', '--in=here', '--json').stdout.decode().splitlines()
    if available_before:
        raise RuntimeError('fresh store already contains annex payloads')
    worktree = {x['path']: x for x in stop['worktree']}
    expected = {}
    for item in files:
        receipt_item = worktree[item['file']]
        if receipt_item.get('annex_key'):
            if item['key'] != receipt_item['annex_key']:
                raise RuntimeError('annex key mismatch against stop receipt')
            wanted = receipt_item['annex_content']
            if not wanted['available']:
                raise RuntimeError('original annex payload was unavailable')
        elif receipt_item['kind'] == 'file':
            wanted = {'sha256': receipt_item['sha256'], 'size': receipt_item['size']}
            if item['backend'] != 'SHA256E' or item['keyname'].split('.', 1)[0] != wanted['sha256']:
                raise RuntimeError('unlocked annex key mismatch against stop receipt payload hash')
        else:
            raise RuntimeError('unsupported original annex representation')
        if int(item['bytesize']) != wanted['size']:
            raise RuntimeError('annex key size mismatch against stop receipt')
        expected[item['file']] = {'inventory': item, 'receipt': receipt_item, 'wanted': wanted}
    original_locked = {x['path'] for x in stop['worktree'] if x.get('annex_key')}
    if not original_locked.issubset(expected):
        raise RuntimeError('missing originally locked annex paths')
    r.save('required-annex-paths.json', files)
    r.save('pre-retrieval-full-inventory.json', {
        'result_commit': r.RESULT, 'required_annex_paths': len(expected),
        'locked_in_original_receipt': len(original_locked),
        'unlocked_in_original_receipt': len(expected) - len(original_locked),
        'annex_payloads_present_before_get': 0,
        'all_inventory_keys_agree_with_original_receipt': True})
    r.annex('get', '--from=con-hub', '--json', '--', *sorted(expected))
    verified = []
    for path, item in sorted(expected.items()):
        target = r.DEST / path
        content = target.read_bytes()
        want = item['wanted']
        original = item['receipt']
        verified.append({'path': path, 'annex_key': item['inventory']['key'],
            'original_kind': original['kind'], 'bytes': len(content), 'sha256': r.sha(content),
            'matches_stop_receipt': len(content) == want['size'] and r.sha(content) == want['sha256'],
            'link_matches_stop_receipt': os.readlink(target) == original['link_target']
                if original['kind'] == 'symlink' else None})
    r.save('verified-annex-artifacts.json', verified)
    regular = []
    symlinks = []
    for item in stop['worktree']:
        if item['path'] in expected or not item.get('tracked'):
            continue
        if item['kind'] == 'file':
            content = (r.DEST / item['path']).read_bytes()
            regular.append({'path': item['path'], 'bytes': len(content), 'sha256': r.sha(content),
                'matches_stop_receipt': r.sha(content) == item['sha256'] and len(content) == item['size']})
        elif item['kind'] == 'symlink':
            link = os.readlink(r.DEST / item['path'])
            symlinks.append({'path': item['path'], 'link_target': link,
                'matches_stop_receipt': link == item['link_target'] and r.sha(link.encode()) == item['sha256']})
    r.save('verified-git-files.json', regular)
    r.save('verified-git-symlinks.json', symlinks)
    end_head = r.git('rev-parse', 'HEAD').stdout.decode().strip()
    end_status = r.git('status', '--porcelain=v1', '--untracked-files=all').stdout.decode()
    refs = r.git('for-each-ref', '--format=%(refname) %(objectname)').stdout.decode().splitlines()
    available_after = [json.loads(line) for line in
                       r.annex('find', '--in=here', '--json').stdout.decode().splitlines() if line.strip()]
    available_paths = {x['file'] for x in available_after}
    all_match = all(x['matches_stop_receipt'] and x['link_matches_stop_receipt'] is not False for x in verified)
    passed = (all_match and all(x['matches_stop_receipt'] for x in regular + symlinks)
              and end_head == r.RESULT and not end_status and available_paths == set(expected))
    outcome = {'schema_version': 1, 'passed': passed,
        'result_commit': r.RESULT, 'published_annex_metadata_commit': prior['metadata_commit'],
        'destination': str(r.DEST), 'source_remote': r.URL, 'result_ref': r.RESULT_REF,
        'annex_metadata_ref': r.ANNEX_REF, 'annex_content_source': 'con-hub',
        'annex_required_paths': len(expected), 'annex_retrieved_paths': len(verified),
        'annex_unique_keys': len({x['annex_key'] for x in verified}),
        'annex_input_paths': sum(p.startswith('input/') for p in expected),
        'annex_result_paths': sum(p.startswith('results/') for p in expected),
        'annex_verified_bytes': sum(x['bytes'] for x in verified),
        'annex_all_hashes_match_original_stop_receipt': all_match,
        'annex_all_required_paths_available_after_get': available_paths == set(expected),
        'git_regular_files_verified': len(regular), 'git_symlinks_verified': len(symlinks),
        'git_index_matches_original_stop_receipt': True,
        'all_git_file_hashes_match_original_stop_receipt': all(x['matches_stop_receipt'] for x in regular + symlinks),
        'end_head': end_head, 'end_status_porcelain': end_status, 'end_refs': refs,
        'stop_receipt_path': str(r.STOP), 'stop_receipt_sha256': r.sha(r.STOP.read_bytes()),
        'finished_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'initial_inventory_guard': 'Retained failure.json records the first check recognizing only 54 locked symlinks; continuation uses annex inventory and includes all four unlocked results.',
        'limitations': ['Independent fresh repository and initially empty annex store on the same host; not a second-host test.',
                       'No scientific replay, worker environment resolution, source changes, source commits, pushes, or worker intervention.',
                       'Skills submodule left uninitialized; exact gitlink is covered by original stop-receipt index comparison.',
                       'Local git-annex initialization and retrieval update local annex bookkeeping only.']}
    r.save('result.json', outcome)
    print(json.dumps(outcome, indent=2), flush=True)
    if not passed:
        sys.exit(1)

if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        r.save('continuation-failure.json', {'error': str(exc), 'completed_commands': len(r.commands)})
        print(str(exc), file=sys.stderr)
        sys.exit(1)
