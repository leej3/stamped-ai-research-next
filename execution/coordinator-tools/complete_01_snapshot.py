import datetime,hashlib,json,pathlib,subprocess
B=pathlib.Path('/Users/johnlee/.local/state/stamped-ai-research-next/pilots/narps-suitability-20261015-01');W=pathlib.Path('/Users/johnlee/.local/share/stamped-ai-research-next/workers/narps-suitability-20261015-01');R=B/'fresh-recipient';LOG=B/'publication/finalization-recovery.jsonl';M='/Users/johnlee/code/CON/stamped-ai-research-next/pixi.toml'
def run(a,p=W):
 cp=subprocess.run(a,cwd=p,text=True,capture_output=True)
 with LOG.open('a') as f:f.write(json.dumps({'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'argv':a,'cwd':str(p),'returncode':cp.returncode,'stdout':cp.stdout,'stderr':cp.stderr})+'\n')
 assert cp.returncode==0,cp.stderr;return cp.stdout.strip()
final=run(['git','rev-parse','HEAD']);env=run(['git','rev-parse','codex/env-narps-suitability-20261015-01']);lock=(B/'final-pixi.lock').read_bytes()
assert run(['git','rev-parse',env+'^'])==final
run(['pixi','run','git','annex','copy','--to','con-hub','--all','--json']);run(['git','fetch','origin','git-annex:refs/remotes/origin/git-annex']);run(['pixi','run','git','annex','merge']);run(['git','push','--porcelain','origin','git-annex:git-annex'])
run(['git','fetch','origin','git-annex:refs/remotes/origin/git-annex'],R);run(['git','checkout','--detach',env],R);run(['pixi','run','--manifest-path',M,'git','annex','merge'],R);run(['pixi','run','--manifest-path',M,'git','annex','get','--from','con-hub','pixi.lock'],R);assert (R/'pixi.lock').read_bytes()==lock
run(['git','checkout','--detach',final],R)
files=run(['git','ls-files','-z']).split('\0')
for f in filter(None,files):assert (W/f).read_bytes()==(R/f).read_bytes(),f
result={'run_id':'narps-suitability-20261015-01','science_commit':(B/'scientific-result-commit.txt').read_text().strip(),'packaged_commit':final,'branch':'codex/narps-suitability-20261015-01','environment_commit':env,'environment_branch':'codex/env-narps-suitability-20261015-01','environment_parent':final,'lock_sha256':hashlib.sha256(lock).hexdigest(),'lock_storage':'annex; independently retrieved from CON Hub','lock_retrieved_and_identical':True,'final_git_files_verified':len(list(filter(None,files))),'annex_verification':'execution/publication/assessment-delta-retrieval.json','assessment_index':'execution/assessment/README.md','reviewed_report':'execution/assessment/reviewed/2026-10-15-2-assessment.md','original_report':'execution/assessment/native/judgment/2026-10-15-assessment.md','verified_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
(B/'final-publication.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
