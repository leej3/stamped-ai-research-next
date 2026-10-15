#!/usr/bin/env python3
"""Check a recipient's empty starting state or independent fixture result."""

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

from trial import OUTPUTS, verify, write_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--receipt", type=Path, required=True)
    expected = parser.add_mutually_exclusive_group()
    expected.add_argument("--expect-absent", action="store_true")
    expected.add_argument("--expected-summary", type=Path)
    args = parser.parse_args()
    if args.receipt.exists():
        parser.error("Receipt exists; use a fresh path and preserve prior evidence")
    repo = args.dataset.resolve()
    if args.expect_absent:
        objects = Path(subprocess.check_output(
            ["git", "-C", str(repo), "rev-parse", "--git-path", "annex/objects"],
            text=True).strip())
        if not objects.is_absolute():
            objects = repo / objects
        payloads = [str(path.relative_to(objects)) for path in objects.rglob("*")
                    if path.is_file()]
        present = {str(path): os.path.lexists(repo / path) for path in OUTPUTS}
        result = dict(ok=not any(present.values()) and not payloads,
                      output_paths_exist=present, annex_payloads=payloads)
    else:
        result = verify(repo)
        if args.expected_summary:
            original = json.loads(args.expected_summary.read_text())
            result["hashes_match_original"] = result.get("hashes") == original["output_hashes"]
            result["ok"] = result["ok"] and result["hashes_match_original"]
    result.update(dataset=str(repo), python=sys.executable)
    write_json(args.receipt, result)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
