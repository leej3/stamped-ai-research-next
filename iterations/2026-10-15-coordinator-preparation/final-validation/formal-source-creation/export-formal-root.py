from pathlib import Path
import subprocess,json,uuid
BASE=Path(__file__).parent
source=BASE/'formal-root-source'
dest=BASE/'formal-root-build'
def git(*args):
 return subprocess.check_output(['git','-C',str(source),*args])
if dest.exists(): raise SystemExit('Preserve existing destination')
ref=git('rev-parse','HEAD').decode().strip()
assert ref=='ea3fb355542fc9b85d82e51e90f0055103f26333'
dest.mkdir()
inventory=[]; gitlinks=[]
for row in git('ls-tree','-rz','HEAD').split(b'\0'):
 if not row: continue
 header,name=row.split(b'\t',1); mode,kind,oid=header.decode().split();name=name.decode()
 if name.startswith('iterations/'): continue
 inventory.append({'path':name,'mode':mode,'source_blob':oid})
 path=dest/name
 if kind=='commit':
  path.mkdir(parents=True,exist_ok=True);gitlinks.append((name,oid));continue
 data=git('cat-file','blob',oid);path.parent.mkdir(parents=True,exist_ok=True)
 if mode=='120000':path.symlink_to(data.decode())
 else:path.write_bytes(data);path.chmod(0o755 if mode=='100755' else 0o644)
new_study='c7a135f92f92df15c379f7c2d9231f13981d76e4'
manifest=dest/'pixi.toml';manifest.write_text(manifest.read_text().replace('name = "stamped-ai-research-next"','name = "stamped-in-practice"'))
(dest/'.datalad/config').write_text('[datalad "dataset"]\n\tid = '+str(uuid.uuid4())+'\n')
modules=dest/'.gitmodules';modules.write_text(modules.read_text().replace('https://github.com/leej3/stamped-ai-research-next.git','https://github.com/leej3/stamped-in-practice.git'))
p=dest/'README.md';s=p.read_text();s=s[:s.index('\nPreparation evidence is retained')]
p.write_text(s+'\nNARPS is the first formal study.\nThe tested source and preparation evidence are linked in [`source-version.json`](source-version.json); formal trials and skill iterations are recorded here.\n')
provenance={'schema_version':1,'source_repository':'https://github.com/leej3/stamped-ai-research-next.git','source_commit':ref,'source_tree':git('rev-parse','HEAD^{tree}').decode().strip(),'acquisition':'Depth-one clone, then exact published source revision fetched with depth one.','history':'Parentless initial commit derived from the prepared source tree; preparation history stays in the source repository.','excluded_paths':['iterations/'],'adaptations':['New dataset identity and workspace name','Study gitlink selects a parentless study with the identical frozen input tree','Study remote points to this repository','README links source provenance'],'study':{'commit':new_study,'source_commit':'a58e822761acfe35724d3557404fc55a297e1a19','input_tree':'a484f41db2095ef116f08d359f9b95ad41981698'},'working_skills_commit':'8fe0022dc272d777671e1c47eb24aea650ff6bd6','assessment_source_commit':'0208f82504f15b82b7582f34143ab889dd52c68d','preparation_evidence_url':'https://github.com/leej3/stamped-ai-research-next/tree/'+ref+'/iterations/2026-10-15-coordinator-preparation'}
(dest/'source-version.json').write_text(json.dumps(provenance,indent=2)+'\n')
subprocess.run(['git','init','-b','main',str(dest)],check=True)
for args in (['config','core.hooksPath',str(dest/'.git/hooks')],['remote','add','origin','git@github.com:leej3/stamped-in-practice.git'],['add','--all']):
 subprocess.run(['git','-C',str(dest),*args],check=True)
for name,oid in gitlinks:
 if name=='studies/narps':oid=new_study
 subprocess.run(['git','-C',str(dest),'update-index','--add','--cacheinfo','160000,'+oid+','+name],check=True)
(BASE/'formal-root-export.json').write_text(json.dumps({'source_commit':ref,'exported_entries':inventory,'destination':str(dest)},indent=2)+'\n')
print(json.dumps({'destination':str(dest),'source':ref,'source_entries':len(inventory),'gitlinks':gitlinks}))
