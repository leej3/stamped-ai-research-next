import datetime,hashlib,json,os,pathlib,shutil,subprocess
BASE=pathlib.Path('/Users/johnlee/.local/state/stamped-ai-research-next/pilots');WORK=pathlib.Path('/Users/johnlee/.local/share/stamped-ai-research-next/workers')
def cmd(argv,cwd,log,input=None):
 p=subprocess.run(argv,cwd=cwd,input=input,text=True,capture_output=True)
 with log.open('a') as f:f.write(json.dumps({'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'argv':argv,'cwd':str(cwd),'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr})+'\n')
 if p.returncode:raise RuntimeError(str(argv)+' '+p.stderr[-1500:])
 return p.stdout
def commit(w,b,log,subject,body):
 provenance=cmd(['/Users/johnlee/.agents/skills/commit-provenance/scripts/resolve.sh'],w,log)
 msg=b/'publication/final-commit-message.txt';msg.write_text(subject+'\n\n'+body+'\n\n'+provenance)
 cmd(['pixi','run','git','commit','-F',str(msg)],w,log)
 return cmd(['git','rev-parse','HEAD'],w,log).strip()
for n in ['01','02','03']:
 rid='narps-suitability-20261015-'+n;b=BASE/rid;w=WORK/rid;log=b/'publication/finalization.jsonl';branch='codex/'+rid;envbranch='codex/env-'+rid
 # Preserve completed publication and retrieval evidence; finalization's own log
 # stays external until the coordinator iteration records its final receipt.
 for p in (b/'publication').iterdir():
  if p.is_file() and p.name not in ['finalization.jsonl','final-commit-message.txt']:
   dst=w/'execution/publication'/p.name
   if not dst.exists() or dst.read_bytes()!=p.read_bytes():shutil.copy2(p,dst)
 for p in (BASE/'coordinator-tools').glob('*.py'):shutil.copy2(p,w/'execution/coordinator-tools'/p.name)
 cmd(['git','add','execution/assessment/README.md','execution/coordinator-tools','execution/publication'],w,log)
 # Final additions are small Git files. All annex payloads were verified at the
 # preceding package commit, so no unverified final annex key is introduced.
 staged=cmd(['git','diff','--cached','--raw'],w,log)
 assert '120000' not in staged,staged
 final=commit(w,b,log,'chore(pilot): link checklists and retain retrieval proof','Retain independently verified annex retrieval and public assessment links.\nPreserve scientific outputs unchanged; final additions are Git text records.')
 cmd(['git','push','--porcelain','origin',f'HEAD:refs/heads/{branch}'],w,log)
 lock=(w/'pixi.lock').read_bytes();expected=json.loads((b/'scientific-completion.json').read_text())['final_working_lock_sha256'];assert hashlib.sha256(lock).hexdigest()==expected
 (b/'final-pixi.lock').write_bytes(lock)
 cmd(['git','switch','-c',envbranch],w,log)
 blob=cmd(['git','hash-object','-w','pixi.lock'],w,log).strip();cmd(['git','update-index','--add','--cacheinfo',f'100644,{blob},pixi.lock'],w,log)
 envcommit=commit(w,b,log,'build(env): preserve final pilot lock snapshot','Preserve the exact working Pixi lock from research completion.\nThis branch is one commit above the final packaged experiment and is not\nintended to merge into the coordinator branch.')
 assert cmd(['git','rev-parse','HEAD^'],w,log).strip()==final
 assert cmd(['git','diff','--name-only',final,envcommit],w,log).strip()=='pixi.lock'
 assert cmd(['git','ls-tree','HEAD','pixi.lock'],w,log).startswith('100644 blob')
 cmd(['git','push','--porcelain','origin',f'HEAD:refs/heads/{envbranch}'],w,log)
 cmd(['git','switch',branch],w,log);(w/'pixi.lock').write_bytes(lock)
 assert not cmd(['git','status','--porcelain'],w,log).strip()
 # Check final small Git additions from the same independent recipient.
 r=b/'fresh-recipient';cmd(['git','fetch','origin',f'refs/heads/{branch}:refs/remotes/origin/{branch}',f'refs/heads/{envbranch}:refs/remotes/origin/{envbranch}'],r,log);cmd(['git','checkout','--detach',final],r,log)
 files=cmd(['git','ls-files','-z'],w,log).split('\0')
 for file in filter(None,files):assert (w/file).read_bytes()==(r/file).read_bytes(),file
 fetched_lock=subprocess.check_output(['git','show',envcommit+':pixi.lock'],cwd=r);assert fetched_lock==lock
 result={'run_id':rid,'science_commit':(b/'scientific-result-commit.txt').read_text().strip(),'packaged_commit':final,'branch':branch,'environment_commit':envcommit,'environment_branch':envbranch,'environment_parent':final,'lock_sha256':expected,'lock_retrieved_and_identical':True,'final_git_files_verified':len(list(filter(None,files))),'annex_verification':'execution/publication/assessment-delta-retrieval.json','assessment_index':'execution/assessment/README.md','reviewed_report':'execution/assessment/reviewed/2026-10-15-2-assessment.md','original_report':'execution/assessment/native/judgment/2026-10-15-assessment.md','verified_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 (b/'final-publication.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
