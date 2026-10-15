#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, timezone
import json, subprocess, sys
root=Path('/Users/johnlee/.local/state/stamped-ai-research-next/preparation-20261015/cold-stamped-evidence/coordinator-actions')
label,cwd,*argv=sys.argv[1:]
base=root/label
if base.with_suffix('.json').exists(): raise SystemExit('Existing action receipt: preserve and choose a new label')
start=datetime.now(timezone.utc).isoformat()
r=subprocess.run(argv,cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
base.with_suffix('.stdout').write_bytes(r.stdout)
base.with_suffix('.stderr').write_bytes(r.stderr)
base.with_suffix('.json').write_text(json.dumps({'started_at':start,'finished_at':datetime.now(timezone.utc).isoformat(),'cwd':cwd,'argv':argv,'returncode':r.returncode},indent=2)+'\n')
sys.stdout.buffer.write(r.stdout);sys.stderr.buffer.write(r.stderr)
raise SystemExit(r.returncode)
