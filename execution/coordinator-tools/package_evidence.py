import collections,datetime,hashlib,json,pathlib,shutil,subprocess
BASE=pathlib.Path('/Users/johnlee/.local/state/stamped-ai-research-next/pilots')
WORK=pathlib.Path('/Users/johnlee/.local/share/stamped-ai-research-next/workers')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
for n in ['01','02','03']:
 run=f'narps-suitability-20261015-{n}'; b=BASE/run;w=WORK/run;a=b/'assessment'
 launch=json.loads((a/'native/launch.json').read_text());result=json.loads((a/'native/result.json').read_text());home=pathlib.Path(launch['codex_home']);sess=result['native_session_ids'][0]
 raw=next((home/'sessions').rglob('*'+sess+'.jsonl'));local=a/'native-session-local';local.mkdir(exist_ok=True);shutil.copy2(raw,local/raw.name)
 public=a/'native-session';public.mkdir(exist_ok=True);out=[];omitted=collections.Counter();identity={}
 for ordinal,line in enumerate(raw.read_text().splitlines()):
  row=json.loads(line);t=row['type'];p=row.get('payload',{});kind=p.get('type');keep=False
  if t=='session_meta':p={k:v for k,v in p.items() if k in ['id','session_id','timestamp','cwd','cli_version','source','model_provider','git']};keep=True;identity.update(p)
  elif t=='turn_context':p={k:v for k,v in p.items() if k in ['turn_id','model','effort','cwd','approval_policy','sandbox_policy']};keep=True;identity.update({k:p[k] for k in ['model','effort'] if k in p})
  elif t=='response_item':
   keep=kind in ['function_call','function_call_output','custom_tool_call','custom_tool_call_output'] or (kind=='message' and (p.get('role')=='user' or p.get('role')=='assistant' and p.get('channel') in ['final','commentary']))
  elif t=='token_usage_record':keep=True
  elif t=='event_msg':keep=kind in ['task_started','task_complete','agent_message','user_message']
  if keep:out.append({'timestamp':row.get('timestamp'),'ordinal':ordinal,'record_type':t,'payload':p})
  else:omitted[t+':'+str(kind)]+=1
 path=public/'execution-transcript.jsonl';path.write_text(''.join(json.dumps(x)+'\n' for x in out))
 dump(public/'export.json',{'source_basename':raw.name,'source_sha256':sha(raw),'raw_source_retained_locally':str(local/raw.name),'export_sha256':sha(path),'exported_records':len(out),'omitted_record_counts':dict(omitted),'scope':'Public messages, tool calls/outputs, timestamps, identity and usage. Internal reasoning, base instructions and redundant bookkeeping excluded. Original raw native rollout retained locally; native CLI events retained unchanged.'})
 dump(public/'verified-identity.json',identity)
 # Copy all public assessment evidence; raw rollouts stay local.
 dest=w/'execution/assessment';dest.mkdir(exist_ok=True)
 for item in a.iterdir():
  if item.name=='native-session-local':continue
  if item.is_dir():shutil.copytree(item,dest/item.name,dirs_exist_ok=True)
  else:shutil.copy2(item,dest/item.name)
 shutil.copytree(b/'publication',w/'execution/publication',dirs_exist_ok=True)
 shutil.copytree(BASE/'coordinator-tools',w/'execution/coordinator-tools',dirs_exist_ok=True)
 text=(w/'execution/README.md').read_text().replace('No experimental research skills or frozen judging round were used.','No experimental research skills were exposed to the research workers.\nA later frozen judging round assessed the exact science commits; `assessment/` preserves original independent judgments and explicitly coordinator-reviewed revisions.\nThese later additions do not earn original-worker credit.')
 text+='\n`publication/` retains SSH/annex publication and independent retrieval receipts, including failed coordinator command attempts and corrected retries.\nHosted Entire checks verify the exact native research session linked to each scientific commit; this evidence applies to these prepared fresh repositories.\n'
 (w/'execution/README.md').write_text(text)
 with (w/'README.md').open('a') as f:f.write('\n[Reviewed STAMPED assessment](execution/assessment/reviewed/2026-10-15-2-assessment.md) · [Original independent assessment](execution/assessment/native/judgment/2026-10-15-assessment.md).\n')
 if n=='03':
  dump(w/'execution/assessment/reviewed/retrieval-timing.json',{'original_http422_tool_output_at':'2026-10-15T20:47:43.209Z','publication_completed_by':'2026-10-15T20:48:05.179451+00:00','publication_time_evidence':'Retained corrected-git-publication.jsonl mtime; command record confirms successful branch creation. Timestamp is filesystem completion bound, not server acknowledgment timestamp.','second_422_occurrence_at':'2026-10-15T20:50:34.756Z','second_occurrence_kind':'Rendering the earlier checklist finding, not a second HTTP query.','later_exact_fetch':'../current-exact-fetch.json'})
 # All science bytes, including manifest, must be unchanged.
 for item in json.loads((b/'scientific-completion.json').read_text())['artifact_inventory']:
  assert sha(w/item['path'])==item['sha256'],item['path']
 subprocess.run(['/Users/johnlee/.local/bin/snapper','--in-place',str(w/'README.md'),str(w/'execution/README.md'),str(dest/'reviewed/2026-10-15-2-assessment.md')],check=True,capture_output=True)
 print(n,'public evidence prepared; science unchanged')
