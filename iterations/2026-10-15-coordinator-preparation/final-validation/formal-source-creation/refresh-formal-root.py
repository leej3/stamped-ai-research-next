from pathlib import Path
import subprocess,json
base=Path(__file__).parent
source=base/'formal-root-source';dest=base/'formal-root-build'
adapted={'.datalad/config','.gitmodules','.gitattributes','AGENTS.md','README.md','pixi.toml','prompt.md'}
def git(*args):return subprocess.check_output(['git','-C',str(source),*args])
ref=git('rev-parse','HEAD').decode().strip();inventory=[]
for row in git('ls-tree','-rz','HEAD').split(b'\0'):
 if not row:continue
 header,name=row.split(b'\t',1);mode,kind,oid=header.decode().split();name=name.decode()
 if name.startswith('iterations/'):continue
 inventory.append({'path':name,'mode':mode,'source_blob':oid})
 if kind=='commit' or name in adapted:continue
 data=git('cat-file','blob',oid);path=dest/name;path.parent.mkdir(parents=True,exist_ok=True)
 if mode=='120000':
  if path.is_symlink() and path.readlink().as_posix()==data.decode():continue
  if path.exists() or path.is_symlink():path.unlink()
  path.symlink_to(data.decode())
 else:
  assert not path.is_symlink(),name
  path.write_bytes(data);path.chmod(0o755 if mode=='100755' else 0o644)
manifest=git('show','HEAD:pixi.toml').decode().replace('name = "stamped-ai-research-next"','name = "stamped-in-practice"')
(dest/'pixi.toml').write_text(manifest)
p=dest/'source-version.json';v=json.loads(p.read_text());v.update(source_commit=ref,source_tree=git('rev-parse','HEAD^{tree}').decode().strip(),preparation_evidence_url='https://github.com/leej3/stamped-ai-research-next/tree/'+ref+'/iterations/2026-10-15-coordinator-preparation');p.write_text(json.dumps(v,indent=2)+'\n')
(base/'formal-root-export.json').write_text(json.dumps({'source_commit':ref,'exported_entries':inventory,'adapted_paths':sorted(adapted),'destination':str(dest)},indent=2)+'\n')
subprocess.run(['git','-C',str(dest),'add','--all'],check=True)
for name,oid in [('skills','c90252a7b9072a4828e9c0b1fa6e5f48409a9cfa'),('assessment','0208f82504f15b82b7582f34143ab889dd52c68d'),('studies/narps','c7a135f92f92df15c379f7c2d9231f13981d76e4')]:
 subprocess.run(['git','-C',str(dest),'update-index','--add','--cacheinfo','160000,'+oid+','+name],check=True)
print(json.dumps({'source_commit':ref,'source_entries':len(inventory),'adapted_paths':sorted(adapted)}))
