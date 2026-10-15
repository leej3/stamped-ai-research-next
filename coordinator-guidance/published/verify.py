"""Verify prepared inputs; this does not execute the NARPS analysis."""
import gzip
import hashlib
import io
import json
import platform
import re
import tarfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import nibabel as nib
import numpy as np
import openpyxl
import pandas as pd

root = Path(__file__).resolve().parent
sources = json.loads((root / "sources.json").read_text())
report = {
    "verified_at": datetime.now(timezone.utc).isoformat(),
    "command": "pixi exec --spec nibabel --spec pandas --spec openpyxl python studies/narps-figure2/verify.py",
    "versions": {"python": platform.python_version(), "nibabel": nib.__version__,
                 "numpy": np.__version__, "pandas": pd.__version__,
                 "openpyxl": openpyxl.__version__},
    "payloads": {},
}
for source in [sources["input_archive"], sources["reference_archive"], *sources["templates"]]:
    path = root / source["path"]
    algorithm, expected = source["checksum"].split(":", 1)
    with path.open("rb") as stream:
        checksum = hashlib.file_digest(stream, algorithm).hexdigest()
    assert path.stat().st_size == source["bytes"] and checksum == expected, path
    report["payloads"][path.name] = {"bytes": path.stat().st_size,
                                   "checksum": f"{algorithm}:{checksum}", "match": True}

with tarfile.open(root / sources["reference_archive"]["path"]) as archive:
    report["reference_members"] = len(archive.getmembers())
    matrix = pd.read_csv(archive.extractfile(
        "./output/correlation_unthresh/spearman_unthresh_hyp1.csv"), index_col=0)
    membership = json.load(archive.extractfile(
        "./output/correlation_unthresh/unthresh_cluster_membership_spearman.json"))["1"]
    assert matrix.shape == (64, 64) and list(matrix.index) == list(matrix.columns)
    assert np.isfinite(matrix.to_numpy()).all()
    teams = set(matrix.index)
    assert Counter(team for cluster in membership.values() for team in cluster) == Counter(matrix.index)
    for number in (1, 2, 3):
        image = nib.Nifti1Image.from_bytes(gzip.decompress(archive.extractfile(
            f"./output/cluster_maps/hyp1_cluster{number}_mean.nii.gz").read()))
        assert image.shape == (91, 109, 91)
    report["reference"] = {"matrix_shape": list(matrix.shape),
                           "cluster_sizes": {key: len(value) for key, value in membership.items()},
                           "mean_maps_readable": 3}

maps, metadata = {}, {}
with tarfile.open(root / sources["input_archive"]["path"], mode="r|gz") as archive:
    count = 0
    for member in archive:
        count += 1
        match = re.fullmatch(r"\./orig/\d+_([A-Z0-9]+)/hypo1_unthresh\.nii\.gz", member.name)
        if match:
            image = nib.Nifti1Image.from_bytes(gzip.decompress(archive.extractfile(member).read()))
            maps[match[1]] = {"path": member.name, "shape": list(image.shape),
                              "nonfinite_voxels": int(np.count_nonzero(~np.isfinite(np.asanyarray(image.dataobj))))}
        elif member.name in ("./orig/narps_results.xlsx", "./orig/analysis_pipelines_for_analysis.xlsx"):
            sheets = pd.read_excel(io.BytesIO(archive.extractfile(member).read()), sheet_name=None)
            metadata[member.name] = {name: list(table.shape) for name, table in sheets.items()}
        elif member.name == "./orig/narps_neurovault_images_details_responses_corrected.csv":
            metadata[member.name] = list(pd.read_csv(io.BytesIO(archive.extractfile(member).read())).shape)
report["input_members"] = count
assert teams <= set(maps), sorted(teams - set(maps))
assert len(metadata) == 3
report["inputs"] = {"hypothesis1_maps": len(maps), "missing_reference_teams": sorted(teams - set(maps)),
                    "metadata": metadata, "maps": maps}
report["templates"] = {source["path"]: list(nib.load(root / source["path"]).shape)
                       for source in sources["templates"]}
assert all(shape == [91, 109, 91] for shape in report["templates"].values())
report["analysis_executed"] = False
(root / "verification.json").write_text(json.dumps(report, indent=2) + "\n")
print(f"Verified four payloads, {len(maps)} input maps, three metadata tables and the 64-team reference.")
