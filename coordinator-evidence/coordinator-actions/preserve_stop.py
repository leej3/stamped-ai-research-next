from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil,tarfile
base=Path('/Users/johnlee/.local/state/stamped-ai-research-next/preparation-20261015')
w=base/'cold-stamped-worker'
e=base/'cold-stamped-evidence'
rpath=e/'launch/native/worker-end-state.json'
r=json.loads(rpath.read_text())
assert r['capture_status']=='complete' and not r['errors']
p=e/'worker-stop-original'
p.mkdir()
shutil.copy2(rpath,p/rpath.name)
for name in ['pixi.lock','pixi.toml']:
 shutil.copy2(w/name,p/name)
archive=p/'artifacts.tar.gz'
with tarfile.open(archive,'w:gz',dereference=False) as t:
 for row in r['worktree']:
  if row['kind'] in ('file','symlink'):
   t.add(w/row['path'],arcname='worktree/'+row['path'],recursive=False)
   if row.get('annex_content',{}).get('available'):
    t.add((w/row['path']).resolve(),arcname='annex-objects/'+row['annex_key'],recursive=False)
receipt={'schema_version':1,'preserved_at':datetime.now(timezone.utc).isoformat(),'worker_head_commit':r['head_commit'],'source_stop_receipt_sha256':hashlib.sha256(rpath.read_bytes()).hexdigest(),'files':{q.name:{'sha256':hashlib.sha256(q.read_bytes()).hexdigest(),'bytes':q.stat().st_size} for q in p.iterdir()},'omissions':['Reconstructible .pixi cache and Git object storage; committed submodule identities remain in original stop receipt.'],'coordinator_action':'Preservation only; no worker environment resolution, scientific edits or new execution.'}
(p/'preservation.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
