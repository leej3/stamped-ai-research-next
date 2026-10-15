import hashlib, json, os, subprocess
from pathlib import Path
root=Path.cwd();out=root/'experiments/skill-bundle/final-routing-001'
config=json.loads((Path.home()/'.config/stamped-ai-research-next/launch.json').read_text())
environment=os.environ.copy();environment['CODEX_HOME']=config['codex_home']
profile=Path(config['codex_home'])/'config.toml';before=profile.read_bytes()
helper=Path(config['trust_sync']);hooks=Path(config['approved_hooks'])
assert helper.is_relative_to(root/'skills') and hooks.is_relative_to(root)
result=subprocess.run(['python',str(helper),'--worktree',str(root),'--source',str(hooks),'--dry-run'],env=environment,text=True,capture_output=True,check=True)
(out/'trust.stdout').write_text(result.stdout);(out/'trust.stderr').write_text(result.stderr)
assert before==profile.read_bytes()
(out/'host-routing.json').write_text(json.dumps({'helper':str(helper),'helper_sha256':hashlib.sha256(helper.read_bytes()).hexdigest(),'approved_hooks':str(hooks),'hooks_sha256':hashlib.sha256(hooks.read_bytes()).hexdigest(),'trust_config_unchanged':True},indent=2)+'\n')
prompt=root/'experiments/skill-bundle/visibility-001/prompt.txt'
for condition in ('baseline','skills'):
 subprocess.run(['python','scripts/launch_native_probe.py','--checkout',str(root),'--prompt',str(prompt),'--output',str(out/condition),'--cli',config['cli'],'--condition',condition,'--preflight-only'],env=environment,check=True)
 assert (out/condition/'prompt.txt').read_bytes()==prompt.read_bytes()
print(json.dumps({'passed':True,'exact_prompts_retained':2,'trust_config_unchanged':True}))
