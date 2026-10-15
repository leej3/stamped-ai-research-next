import datetime,json,os,pathlib,subprocess
BASE=pathlib.Path('/Users/johnlee/.local/state/stamped-ai-research-next/pilots');WORK=pathlib.Path('/Users/johnlee/.local/share/stamped-ai-research-next/workers')
def run(args,cwd,log,env=None,check=True):
 started=datetime.datetime.now(datetime.timezone.utc).isoformat();p=subprocess.run(args,cwd=cwd,env=env,text=True,capture_output=True)
 with log.open('a') as f:f.write(json.dumps({'started_at':started,'finished_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'argv':args,'cwd':str(cwd),'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr})+'\n')
 if check and p.returncode:raise RuntimeError(f'{args}: {p.stderr[-2000:]}')
 return p.stdout
for n in ['01','02','03']:
 rid=f'narps-suitability-20261015-{n}';w=WORK/rid;b=BASE/rid;log=b/'publication/assessment-packaging.jsonl'
 env=os.environ.copy()
 run(['pixi','run','git','annex','add','execution'],w,log)
 if n=='01':run(['pixi','run','git','annex','add','--force-large','execution/external-resources/nilearn_data/fsl/data/atlases/HarvardOxford/HarvardOxford-cort-maxprob-thr25-2mm.nii.gz'],w,log)
 run(['git','add','README.md','execution'],w,log)
 provenance=run(['/Users/johnlee/.agents/skills/commit-provenance/scripts/resolve.sh'],w,log)
 message='chore(pilot): retain assessments and verified publication evidence\n\nPreserve the original independent checklist judgments and explicitly reviewed\ncorrections. Retain public native judge execution, retrieval receipts and\nconfirmed hosted research-session linkage. Scientific artifacts are unchanged.\n\n'+provenance
 mp=b/'publication/assessment-commit-message.txt';mp.write_text(message)
 run(['pixi','run','git','commit','-F',str(mp)],w,log,env=env)
 package=run(['git','rev-parse','HEAD'],w,log).strip();(b/'publication/assessment-package-commit.txt').write_text(package+'\n')
 run(['pixi','run','git','annex','copy','--to','con-hub','--all','--json'],w,log)
 run(['git','fetch','origin','git-annex:refs/remotes/origin/git-annex'],w,log)
 run(['pixi','run','git','annex','merge'],w,log)
 run(['git','merge-base','--is-ancestor','origin/git-annex','git-annex'],w,log)
 run(['git','push','--porcelain','origin',f'HEAD:refs/heads/codex/{rid}','git-annex:git-annex'],w,log,env=env)
 print(n,package,flush=True)
