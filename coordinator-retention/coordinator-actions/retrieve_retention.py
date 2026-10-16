from pathlib import Path
import subprocess,json,hashlib,time
b=Path('/Users/johnlee/.local/state/stamped-ai-research-next/preparation-20261015');c=b/'cold-stamped-op-coordinator';e=b/'cold-stamped-op-evidence/coordinator-actions/independent-retention-retrieval';d=b/'cold-stamped-op-retention-retrieval';e.mkdir();d.mkdir();calls=[]
def run(argv):
 r=subprocess.run(argv,cwd=d,capture_output=True,text=True);row={'argv':argv,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr};calls.append(row);(e/'commands.json').write_text(json.dumps(calls,indent=2)+'\n');assert r.returncode==0,row;return r.stdout
run(['git','init']);run(['git','remote','add','origin','git@github.com:leej3/stamped-ai-research-next.git']);run(['git','fetch','origin','refs/heads/codex/preparation-stamped-judge-retained-20261015:refs/remotes/origin/retained','refs/heads/codex/preparation-stamped-judgment-op-annex-20261015:refs/heads/git-annex']);run(['git','checkout','--detach','refs/remotes/origin/retained']);head=run(['git','rev-parse','HEAD']).strip();assert head=='5c2ab777351f882a1c5ff717e84544c94c38b999';run(['git','config','remote.origin.annex-ignore','true']);px=['pixi','run','--manifest-path',str(c/'pixi.toml'),'git'];run(px+['annex','init','independent operational judgment retrieval']);run(['git','remote','add','con-hub','https://hub.centerforopenneuroscience.org/leej3/stamped-ai-research-next.git']);run(['git','config','remote.con-hub.annexurl','annex+https://hub.centerforopenneuroscience.org:443/git-annex-p2phttp']);run(['git','config','remote.con-hub.skipFetchAll','true']);rows=[json.loads(x) for x in run(px+['annex','find','--include','*','--json']).splitlines()];assert len(rows)==3
regular=[]
for line in run(['git','ls-files','--stage']).splitlines():
 mode,blob,stage,path=line.split(None,3)
 assert mode!='160000'
 if mode=='100644':
  data=(d/path).read_bytes();expected=subprocess.check_output(['git','show',head+':'+path],cwd=d);assert data==expected;regular.append({'path':path,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)})
result={'source':'GitHub SSH refs','head':head,'ordinary_git_files_verified':regular,'annex_keys':rows,'annex_payload_retrieval':'pending publication and credential unlock; not attempted','scope':'Fresh Git/annex repository on same host; no science executed.','clean':run(['git','status','--porcelain']).strip()==''};(e/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'head':head,'regular_files':len(regular),'annex_files':len(rows),'clean':result['clean']}))
