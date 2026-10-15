"""Link a completed duct analysis run to its exact inputs and environment."""
import argparse
import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import nibabel
import nilearn
import numpy
import pandas
import scipy

ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--code-revision", required=True)
    parser.add_argument("--working-tree-state", choices=["clean", "dirty"], required=True)
    parser.add_argument("--log-prefix", required=True)
    args = parser.parse_args()
    prefix = ROOT / args.log_prefix
    info_path = Path(str(prefix) + "info.json")
    info = json.loads(info_path.read_text())
    sources = json.loads((ROOT / "input/sources.json").read_text())
    outputs = sorted(p for p in (ROOT / "results").iterdir()
                     if p.is_file() and p.name != "report.md")
    manifest = {
        "run_id": args.run_id,
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "code_revision": args.code_revision,
        "working_tree_before_run": args.working_tree_state,
        "command": "pixi run duct ... pixi run analysis",
        "duct_info": str(info_path.relative_to(ROOT)),
        "duct_summary": info.get("execution_summary"),
        "environment": {
            "pixi_manifest_sha256": sha256(ROOT / "pixi.toml"),
            "pixi_lock_sha256": sha256(ROOT / "pixi.lock"),
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "packages": {"nibabel": nibabel.__version__, "nilearn": nilearn.__version__,
                         "numpy": numpy.__version__, "scipy": scipy.__version__,
                         "pandas": pandas.__version__},
        },
        "inputs": {
            "sources_manifest": {"path": "input/sources.json", "sha256": sha256(ROOT / "input/sources.json")},
            "participants_tsv": {"path": "input/participants.tsv", "sha256": sha256(ROOT / "input/participants.tsv")},
            "participant_maps": sources["files"],
        },
        "outputs": [{"path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size,
                     "sha256": sha256(path)} for path in outputs],
    }
    destination = ROOT / "logs" / f"{args.run_id}-provenance.json"
    destination.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"run_provenance": str(destination.relative_to(ROOT)),
                      "outputs": len(outputs), "lock_sha256": manifest["environment"]["pixi_lock_sha256"]}, indent=2))


if __name__ == "__main__":
    main()
