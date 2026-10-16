import sys,subprocess,json,time
from pathlib import Path
from datetime import datetime,timezone
b=Path('/Users/johnlee/.local/state/stamped-ai-research-next/preparation-20261015');e=b/'cold-stamped-op-evidence/coordinator-actions';name,cwd,*argv=sys.argv[1:];p=e/name;p.mkdir();start=datetime.now(timezone.utc).isoformat();t=time.monotonic()
r=subprocess.run(argv,cwd=cwd,capture_output=True);(p/'stdout.txt').write_bytes(r.stdout);(p/'stderr.txt').write_bytes(r.stderr);receipt={'argv':argv,'cwd':cwd,'started_at':start,'elapsed_seconds':time.monotonic()-t,'returncode':r.returncode};(p/'command.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt));print(r.stdout.decode(errors='replace')[-2500:]);print(r.stderr.decode(errors='replace')[-1000:]);sys.exit(r.returncode)
