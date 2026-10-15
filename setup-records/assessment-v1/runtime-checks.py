"""Exercise installed helpers and reject changed assessment source."""
import json, subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[2]
out=Path(__file__).resolve().parent/'runtime-checks'
out.mkdir(exist_ok=False)
checks=[]
def run(name, argv, expected=0):
 result=subprocess.run(argv,cwd=root,text=True,capture_output=True)
 (out/(name+'.stdout')).write_text(result.stdout)
 (out/(name+'.stderr')).write_text(result.stderr)
 checks.append({'name':name,'argv':argv,'returncode':result.returncode,'expected':expected})
 assert result.returncode==expected,(name,result.stderr)
 return result
run('probe-help',['pixi','run','assessment-probes','--help'])
run('completed-response',['pixi','run','assessment-validate','experiments/assessment-v1/blind-001/out/2026-10-15-response.json'])
run('read-only-probe',['pixi','run','assessment-probes','assessment','--kind','skill','--only','tree-clean','-o',str(out/'probe.json')])
source=root/'assessment/skills/assess-alignment-with-stamped-principles/SKILL.md'
original=source.read_bytes()
try:
 source.write_bytes(original+b'\n')
 result=run('reject-source-drift',['pixi','run','assessment-check'],1)
 assert 'local changes' in result.stderr
finally:
 source.write_bytes(original)
run('restored-pin',['pixi','run','assessment-check'])
(out/'checks.json').write_text(json.dumps({'passed':len(checks),'checks':checks},indent=2)+'\n')
print(json.dumps({'passed':len(checks)}))
