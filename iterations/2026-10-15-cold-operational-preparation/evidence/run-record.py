#!/usr/bin/env python3
"""Retain coordinator command bytes and status outside scientific checkouts."""
import datetime
import json
import pathlib
import subprocess
import sys
import time

directory = pathlib.Path(sys.argv[1]).resolve()
cwd = pathlib.Path(sys.argv[2]).resolve()
argv = sys.argv[3:]
directory.mkdir(parents=True, exist_ok=False)
record = {"argv": argv, "cwd": str(cwd),
          "started_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
          "complete": False}
receipt = directory / "command.json"
receipt.write_text(json.dumps(record, indent=2) + "\n")
start = time.monotonic()
with (directory / "stdout.txt").open("wb") as stdout, (directory / "stderr.txt").open("wb") as stderr:
    child = subprocess.Popen(argv, cwd=cwd, stdout=stdout, stderr=stderr)
    record["pid"] = child.pid
    receipt.write_text(json.dumps(record, indent=2) + "\n")
    status = child.wait()
record.update(returncode=status, complete=True, elapsed_seconds=time.monotonic()-start,
              finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
receipt.write_text(json.dumps(record, indent=2) + "\n")
print(json.dumps(record))
raise SystemExit(status)
