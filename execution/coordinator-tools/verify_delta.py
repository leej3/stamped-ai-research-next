import datetime,hashlib,json,pathlib,subprocess,sys
B=pathlib.Path('/Users/johnlee/.local/state/stamped-ai-research-next/pilots');W=pathlib.Path('/Users/johnlee/.local/share/stamped-ai-research-next/workers');n=sys.argv[1];rid='narps-suitability-20261015-'+n;b=B/rid;w=W/rid;r=b/'fresh-recipient';log=b/'publication/assessment-delta-retrieval-commands.jsonl';manifest='/Users/johnlee/code/CON/stamped-ai-research-next/pixi.toml'
def cmd(argv,cwd=r):
 p=subprocess.run(argv,cwd=cwd,text=True,capture_output=True)
 with log.open('a') as f:f.write(json.dumps({'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'argv':argv,'cwd':str(cwd),'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr})+'\n')
 if p.returncode:raise RuntimeError(str(argv)+' '+p.stderr[-1500:])
 return p.stdout
def annex(*args,cwd=r):return cmd(['pixi','run','--manifest-path',manifest,'git','annex',*args],cwd)
commit=(b/'publication/assessment-package-commit.txt').read_text().strip()
cmd(['git','fetch','origin',f'refs/heads/codex/{rid}:refs/remotes/origin/codex/{rid}','git-annex:refs/remotes/origin/git-annex']);cmd(['git','checkout','--detach',commit]);annex('merge');annex('get','--from','con-hub','--json','.')
keys=sorted(annex('findkeys','--in=here',cwd=w).splitlines());got=set(annex('findkeys','--in=here').splitlines())
for key in keys:
 if key not in got:annex('transferkey',key,'--from','con-hub')
assert set(keys)<=set(annex('findkeys','--in=here').splitlines())
files=cmd(['git','ls-files','-z'],w).split('\0');rows=[]
for file in filter(None,files):
 src=(w/file).read_bytes();dst=(r/file).read_bytes();assert src==dst,file
 rows.append({'path':file,'bytes':len(src),'sha256':hashlib.sha256(src).hexdigest()})
d={'verified_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_commit':commit,'recipient':str(r),'independent_git_object_store':not (r/'.git/objects/info/alternates').exists(),'initial_empty_annex_proof':'independent-retrieval.json','current_and_historical_source_keys_verified':len(keys),'all_tracked_files_byte_identical':True,'tracked_files':len(rows),'files':rows,'scope':'Retrieval and byte identity only; no scientific rerun. This extends the initial independent recipient from its empty-annex test.'}
(b/'publication/assessment-delta-retrieval.json').write_text(json.dumps(d,indent=2)+'\n');print(n,len(keys),len(rows),flush=True)
