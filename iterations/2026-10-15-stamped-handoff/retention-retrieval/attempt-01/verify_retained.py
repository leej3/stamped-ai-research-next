from pathlib import Path
from datetime import datetime,timezone
import subprocess,json,hashlib,re
b=Path('/Users/johnlee/.local/state/stamped-ai-research-next/preparation-20261015');p=b/'cold-stamped-independent-retained';e=b/'cold-stamped-final-retrieval';e.mkdir()
manifest=b/'cold-stamped-coordinator/pixi.toml';cmds=[]
def run(args,cwd=b):
 n=len(cmds)+1;r=subprocess.run([str(a) for a in args],cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 (e/f'{n:02}-stdout.txt').write_bytes(r.stdout);(e/f'{n:02}-stderr.txt').write_bytes(r.stderr)
 cmds.append({'argv':[str(a) for a in args],'cwd':str(cwd),'returncode':r.returncode})
 (e/'commands.json').write_text(json.dumps(cmds,indent=2)+'\n')
 if r.returncode:raise RuntimeError(f'Command {n} failed: see retained logs')
 return r.stdout.decode()
def git(*args):return run(['git','-C',p,*args])
def annex(*args):return run(['pixi','run','--manifest-path',manifest,'git','-C',p,'annex',*args])
run(['git','init','--template=','-b','codex/preparation-stamped-independent-retained',p])
git('remote','add','origin','git@github.com:leej3/stamped-ai-research-next.git')
git('config','remote.origin.annex-ignore','true')
git('fetch','--depth=2','--no-tags','origin','refs/heads/codex/preparation-stamped-retained-20261015:refs/heads/codex/preparation-stamped-independent-retained','refs/heads/codex/preparation-stamped-annex-retained-20261015:refs/heads/git-annex')
git('reset','--hard','codex/preparation-stamped-independent-retained')
assert git('rev-parse','HEAD').strip()=='5e85b7a5118a1c7ff7d7fe0406cf0292fb239726'
assert git('rev-parse','git-annex').strip()=='f8486a1541b76d1c2df664d6fd13e47ece8a0722'
assert git('rev-parse','HEAD^').strip()=='8b5bcdaa999289a47f066ba829511d450301c573'
diff=git('diff-tree','--no-commit-id','--name-status','-r','HEAD').splitlines()
assert all(x.startswith('A\tcoordinator-evidence/') for x in diff)
links=[x for x in git('ls-files','--stage').splitlines() if x.startswith('160000 ')]
assert len(links)==1 and links[0].endswith('\tskills')
assert not (p/'.git/objects/info/alternates').exists()
assert not (p/'.git/annex/objects').exists()
annex('init')
config=json.loads((b/'cold-stamped-private/launch.json').read_text())
git('remote','add','con-hub',config['annex_git_url']);git('config','remote.con-hub.annexurl',config['annex_url']);git('config','remote.con-hub.skipFetchAll','true')
rows=[json.loads(x) for x in annex('find','--anything','--json','coordinator-evidence').splitlines() if x]
annex('get','--from=con-hub','coordinator-evidence')
verified=[]
for row in rows:
 path=row['file'];data=(p/path).read_bytes();src=b/'cold-stamped-evidence'/Path(path).relative_to('coordinator-evidence');digest=hashlib.sha256(data).hexdigest()
 match=re.fullmatch(r'SHA256E-s([0-9]+)--([0-9a-f]{64})(?:\..*)?',row['key'])
 assert match and len(data)==int(match[1]) and digest==match[2]
 assert data==src.read_bytes()
 verified.append({'path':path,'key':row['key'],'sha256':digest,'bytes':len(data)})
assert git('status','--porcelain')==''
remote=git('ls-remote','--refs','origin','refs/heads/codex/preparation-stamped-worker-20261015','refs/heads/codex/preparation-stamped-result-20261015')
assert all(x.split()[0]=='8b5bcdaa999289a47f066ba829511d450301c573' for x in remote.splitlines())
result={'schema_version':1,'verified_at':datetime.now(timezone.utc).isoformat(),'passed':True,'retained_commit':'5e85b7a5118a1c7ff7d7fe0406cf0292fb239726','annex_metadata_commit':'f8486a1541b76d1c2df664d6fd13e47ece8a0722','retained_additions_only':len(diff),'annex_paths':len(verified),'annex_bytes':sum(x['bytes'] for x in verified),'payloads':verified,'result_refs_unchanged':True,'unexpected_gitlinks':False,'scope':'Fresh repository and empty annex object store on same host. Only added coordinator evidence downloaded; exact original research payload retrieval was independently verified earlier. No scientific execution.'}
(e/'result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
