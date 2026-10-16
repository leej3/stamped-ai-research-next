from pathlib import Path
from datetime import datetime,timezone
import sys,os,json,hashlib,tarfile,shutil,subprocess
b=Path('/Users/johnlee/.local/state/stamped-ai-research-next/preparation-20261015');c=b/'cold-stamped-op-coordinator';e=b/'cold-stamped-op-evidence';j=e/'judgment-01/judgment'
sys.path.insert(0,str(c/'scripts'));from worker_end_state import capture_worker_end_state
r=json.loads((e/'judgment-01/native/result.json').read_text());assert r.get('returncode') is not None
stop=capture_worker_end_state(j)
p=e/'judge-stop-original';p.mkdir();(p/'stop-state.json').write_text(json.dumps(stop,indent=2)+'\n')
# Archive all original delivered output before changing its layout. Git metadata
# and native config for this seed are already represented by native receipts;
# nested replay Git metadata is retained in the archive.
archive=p/'artifacts.tar.gz';omitted=[]
def filt(info):
 parts=Path(info.name).parts[1:]
 if (parts and parts[0] in ('.git','.entire','.codex')) or any(x in ('.pixi','__pycache__') for x in parts):
  omitted.append(info.name);return None
 return info
with tarfile.open(archive,'w:gz',dereference=False) as t:t.add(j,arcname='judgment',filter=filt)
(p/'preservation.json').write_text(json.dumps({'preserved_at':datetime.now(timezone.utc).isoformat(),'archive':archive.name,'bytes':archive.stat().st_size,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'omitted':omitted,'omission_reason':'Reconstructible Pixi/Python caches, and own seed Git/native configuration represented by seed and launch receipts; nested replay Git metadata retained.','original_stop_status':stop['capture_status']},indent=2)+'\n')
# Detect nested Git checkouts without traversing their Git/Pixi stores.
nested=[]
for root,dirs,files in os.walk(j,followlinks=False):
 root=Path(root)
 if root!=j and ('.git' in dirs or '.git' in files):nested.append(root)
 dirs[:]=[x for x in dirs if x not in ('.git','.pixi','.entire','.codex','__pycache__')]
tops=sorted({x.relative_to(j).parts[0] for x in nested})
records=[]
if tops:
 a=j/'archived-workspaces';a.mkdir();originals=b/'cold-stamped-op-replay-originals';originals.mkdir()
 for top in tops:
  source=j/top;dest=a/(top+'.tar.gz');excluded=[]
  def replay_filter(info):
   if any(x in ('.pixi','__pycache__') for x in Path(info.name).parts):excluded.append(info.name);return None
   return info
  with tarfile.open(dest,'w:gz',dereference=False) as t:t.add(source,arcname=top,filter=replay_filter)
  with tarfile.open(dest,'r:gz') as t:members=len(t.getmembers())
  record={'original_relative_path':top,'archive':str(dest.relative_to(j)),'bytes':dest.stat().st_size,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'tar_members':members,'omitted_reconstructible_caches':excluded,'original_preserved_at':str(originals/top)}
  shutil.move(source,originals/top);records.append(record)
 (a/'manifest.json').write_text(json.dumps({'coordinator_action':'Archive nested replay/retrieval workspaces before staging; no scientific changes.','workspaces':records},indent=2)+'\n')
(e/'coordinator-actions/judge-preservation.json').write_text(json.dumps({'native_result':r,'original_stop_receipt':str(p/'stop-state.json'),'nested_repositories':[str(x) for x in nested],'archived_workspaces':records},indent=2)+'\n')
print(json.dumps({'original_stop':stop['capture_status'],'nested_repositories':[str(x) for x in nested],'archives':records},indent=2))
