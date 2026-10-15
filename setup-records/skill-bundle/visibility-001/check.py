import json, os, subprocess
from pathlib import Path
root=Path.cwd()
out=root/'experiments/skill-bundle/visibility-001'
config=json.loads((Path.home()/'.config/stamped-ai-research-next/launch.json').read_text())
environment=os.environ.copy()
environment['CODEX_HOME']=config['codex_home']
for condition in ('baseline','skills'):
 subprocess.run(['python','scripts/launch_native_probe.py','--checkout',str(root),'--prompt',str(out/'prompt.txt'),'--output',str(out/condition),'--cli',config['cli'],'--condition',condition,'--preflight-only'],env=environment,check=True)
