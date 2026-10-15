#!/usr/bin/env python3
"""Apply the explicitly authorized, reversible Unity startup diagnostic repair."""

import subprocess

REMOTE = r'''
from pathlib import Path
import hashlib, json, shutil, stat, time
path = Path.home() / ".bashrc"
before = path.read_bytes()
old = b"echo Sourcing .bashrc\n"
new = b"case $- in *i*) echo Sourcing .bashrc ;; esac\n"
lines = before.splitlines(keepends=True)
if len(lines) < 4 or lines[3] != old or lines.count(old) != 1:
    raise RuntimeError("Expected unique exact diagnostic on line 4; no edit made")
backup = path.with_name(".bashrc.stamped-ai-backup-" + time.strftime("%Y%m%dT%H%M%S"))
if backup.exists():
    raise RuntimeError("Backup already exists; no edit made")
shutil.copy2(path, backup)
lines[3] = new
after = b"".join(lines)
path.write_bytes(after)
assert stat.S_IMODE(path.stat().st_mode) == stat.S_IMODE(backup.stat().st_mode)
assert backup.read_bytes() == before
assert path.read_bytes() == before.replace(old, new, 1)
print(json.dumps({"status": "repaired", "path": str(path), "backup": str(backup),
                  "changed_line": 4, "before_sha256": hashlib.sha256(before).hexdigest(),
                  "after_sha256": hashlib.sha256(after).hexdigest(),
                  "scope": "Gate only startup diagnostic to interactive shells"}))
'''

raise SystemExit(subprocess.run(
    ["ssh", "-o", "BatchMode=yes", "unity", "python3 -"],
    input=REMOTE, text=True, check=False).returncode)
