"""Independent local recipient, annex retrieval, and genuine native rerun."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',required=True)
    ap.add_argument('--snapshot',required=True)
    ap.add_argument('--run',required=True)
    ap.add_argument('--destination',required=True)
    ap.add_argument('--receipt',required=True)
    ap.add_argument('--provenance-resolver')
    args=ap.parse_args()
    destination=Path(args.destination).resolve()
    receipt=Path(args.receipt).resolve();receipt.mkdir(parents=True,exist_ok=True)
    assert not destination.exists(), 'Destination must be a fresh checkout'
    command_log=[]
    def run(cmd,cwd=None):
        result=subprocess.run(cmd,cwd=cwd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        command_log.append({'command':cmd,'cwd':str(cwd) if cwd else None,
                            'exit_code':result.returncode,'output':result.stdout})
        (receipt/'commands.json').write_text(json.dumps(command_log,indent=2)+'\n')
        if result.returncode: raise RuntimeError(result.stdout)
        return result.stdout
    def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
    run(['pixi','run','datalad','clone',args.source,str(destination)])
    initial_commit=run(['git','rev-parse','HEAD'],destination).strip()
    run(['git','fetch','origin',args.snapshot],destination)
    lock=subprocess.check_output(['git','show',f'{args.snapshot}:pixi.lock'],cwd=destination)
    locked_manifest=subprocess.check_output(['git','show',f'{args.snapshot}:pixi.toml'],cwd=destination)
    assert (destination/'pixi.toml').read_bytes()==locked_manifest
    (destination/'pixi.lock').write_bytes(lock)
    run(['pixi','install','--locked'],destination)
    # Capture absence before retrieval; ordinary git clone contains annex pointers only.
    pointers={str(p.relative_to(destination)): {'is_symlink':p.is_symlink(),'content_present':p.exists()}
              for folder in ['results','logs'] for p in (destination/folder).rglob('*') if p.is_symlink()}
    assert pointers and not any(v['content_present'] for v in pointers.values())
    run(['pixi','run','git','annex','get','--from=origin','results','logs'],destination)
    hashes={name:digest(destination/name) for name in pointers}
    assert len(hashes)==len(pointers)
    run(['pixi','run','git','annex','whereis','--json','results/summary.json'],destination)
    discovery=run(['pixi','run','datalad','-f','json','rerun','--report',args.run],destination)
    assert '"rerun_action": "run"' in discovery
    expected={name:hashes[name] for name in hashes if name.startswith('results/')}
    # Checkout the recorded input revision: declared generated paths disappear,
    # while their annex payloads stay safely in the object database.
    input_commit=run(['git','rev-parse',f'{args.run}^'],destination).strip()
    run(['git','checkout','--detach',input_commit],destination)
    assert (destination/'pixi.toml').read_bytes()==locked_manifest
    (destination/'pixi.lock').write_bytes(lock)
    run(['pixi','install','--locked'],destination)
    run(['git','submodule','update','--init','--recursive'],destination)
    for folder in ['results','logs']:
        assert not (destination/folder).exists(), f'{folder} was not absent before rerun'
    if args.provenance_resolver:
        run(['git','config','provenance.resolver',args.provenance_resolver],destination)
        hook=destination/'.git/hooks/prepare-commit-msg'
        hook.write_text('#!/bin/sh\nset -eu\nresolver=$(git config --get provenance.resolver)\ntrailers=$($resolver)\nprintf "\\n%s\\n" "$trailers" >> "$1"\n')
        hook.chmod(0o755)
    if (destination/'hooks/pre-commit').exists():
        shutil.copyfile(destination/'hooks/pre-commit',destination/'.git/hooks/pre-commit')
        (destination/'.git/hooks/pre-commit').chmod(0o755)
    run(['pixi','run','datalad','rerun','--branch','verified-rerun','--onto',input_commit,args.run],destination)
    regenerated={name:digest(destination/name) for name in expected}
    assert regenerated==expected, {'expected':expected,'regenerated':regenerated}
    rerun_commit=run(['git','rev-parse','HEAD'],destination).strip()
    assert rerun_commit != input_commit, 'No-op is not a replay'
    result={'status':'passed','source':args.source,'recipient':str(destination),
            'initial_commit':initial_commit,'input_commit':input_commit,
            'snapshot_commit':args.snapshot,'original_run_commit':args.run,
            'rerun_commit':rerun_commit,'lock_sha256':hashlib.sha256(lock).hexdigest(),
            'annex_files_absent_before_get':len(pointers),'retrieved_payload_sha256':hashes,
            'declared_outputs_absent_before_rerun':True,'regenerated_sha256':regenerated,
            'comparison':'Exact SHA-256 agreement for every results artifact',
            'scope':'Same-host independent clone; Pixi download caches reused; no online publication or second platform tested.'}
    (receipt/'receipt.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=='__main__':main()
