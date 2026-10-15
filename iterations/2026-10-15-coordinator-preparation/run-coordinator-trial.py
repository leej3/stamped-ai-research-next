from pathlib import Path
import os, sys, json, subprocess, hashlib, time, tomllib
root=Path('/Users/johnlee/.local/share/wt-utils/worktrees/776c/stamped-ai-research-next')
sys.path.insert(0,str(root/'scripts'))
from launch_native_probe import launch_profile, host_skill_paths, skill_catalog
base=Path.home()/'.local/state/stamped-ai-research-next/preparation-20261015'
checkout=base/'coordinator-trial-02'
out=base/'cold-coordinator-02';out.mkdir(exist_ok=False)
prepared=Path.home()/'.local/state/stamped-ai-research-next/codex-public-v3-20261015'
profile=launch_profile(prepared)
config=tomllib.loads((profile/'config.toml').read_text())
overrides={i['path']:i['enabled'] for i in config.get('skills',{}).get('config',[])}
overrides.update({str(p):False for p in host_skill_paths(prepared)})
skill_config='skills.config=['+','.join('{path='+json.dumps(p)+',enabled='+str(enabled).lower()+'}' for p,enabled in sorted(overrides.items()))+']'
prompt='''Prepare to coordinate this repository using its README.md, AGENTS.md and prompt.md. The user selects studies/narps as the first formal study. Their host requirements are working Entire capture, annex upload/retrieval and HPC access. Host launcher choices are supplied in /Users/johnlee/.config/stamped-ai-research-next/launch.json; credentials stay with existing host providers. You have no prior conversation or prior study conclusions.

This is a coordinator preparation trial, not a formal research run. Inspect the tracked coordinator context and selected study guidance; initialize only selected submodules if needed. Do not read iterations/, experiment results, old Git history, other chats or personal memory. Do not launch scientific workers or judges, submit cluster jobs or publish. Give an actionable first-round plan with the commands you would execute, identify unresolved prerequisites or ambiguities, and identify what must remain fixed and what may evolve. Do not substitute assumed success for unperformed checks.

Write coordinator-trial.md with your findings and commit only that file. Use a Conventional Commit and the required exact Codex provenance: run /Users/johnlee/.agents/skills/commit-provenance/scripts/resolve.sh immediately before the commit and preserve its trailers. Use /Users/johnlee/.local/bin/snapper --in-place coordinator-trial.md before committing. No user is available for this trial; record missing information clearly rather than inventing it. End with a concise report.
'''
(out/'prompt.txt').write_text(prompt)
cli='/Applications/ChatGPT.app/Contents/Resources/codex-cli/bin/codex'
cmd=[cli,'--no-daemon','-a','never','-s','danger-full-access','-m','gpt-6-luna','-c','model_reasoning_effort="high"','-c',skill_config,'-c','project_doc_max_bytes=0']
env=os.environ.copy();env['CODEX_HOME']=str(profile)
for k in ('CODEX_THREAD_ID','CODEX_PARENT_THREAD_ID','CODEX_SESSION_ID','PIXI_PROJECT_MANIFEST','PIXI_IN_SHELL','PIXI_PROJECT_ROOT','PIXI_PROJECT_NAME','PIXI_PROJECT_VERSION','PIXI_ENVIRONMENT_NAME','PIXI_ENVIRONMENT_PLATFORMS','PIXI_PROMPT'):env.pop(k,None)
preview=subprocess.run(cmd+['-C',str(checkout),'debug','prompt-input',prompt],env=env,capture_output=True,check=True)
catalog=skill_catalog(preview.stdout)
unexpected=[i for i in catalog if not Path(i['path']).is_relative_to((profile/'skills/.system').resolve())]
assert not unexpected, unexpected
(out/'preflight.json').write_text(json.dumps({'catalog':catalog,'unexpected':unexpected,'prompt_preview_sha256':hashlib.sha256(preview.stdout).hexdigest()},indent=2)+'\n')
cmd+=['exec','--json','--color','never','-C',str(checkout),'-o',str(out/'final.txt'),'-']
record={'argv':cmd,'checkout':str(checkout),'profile':str(profile),'coordinator_commit':subprocess.check_output(['git','-C',str(checkout),'rev-parse','HEAD'],text=True).strip(),'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest()}
(out/'launch.json').write_text(json.dumps(record,indent=2)+'\n')
start=time.monotonic()
with (out/'events.jsonl').open('wb') as stdout,(out/'stderr.txt').open('wb') as stderr:
    result=subprocess.run(cmd,input=prompt.encode(),env=env,stdout=stdout,stderr=stderr)
record.update(returncode=result.returncode,elapsed_seconds=time.monotonic()-start)
(out/'result.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'returncode':result.returncode,'elapsed_seconds':record['elapsed_seconds'],'evidence':str(out)}))
