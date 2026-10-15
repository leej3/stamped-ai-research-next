"""Prepare original participant effect maps; never supply group answers."""
import argparse
import hashlib
import io
import json
import platform
import re
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import nibabel as nib
import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "input"
EVIDENCE = ROOT / "coordinator-guidance/participant-preparation"
DATA_COMMIT = "64ec117560ab58ed0fe1273f3e90887b1768b268"
METHODS_COMMIT = "0a9d71a5ab435b40dcd50fea82d2961a43f0a3fc"
API = "https://neurovault.org/api/collections/4932/images/?limit=2000"
PARTICIPANTS = f"https://raw.githubusercontent.com/OpenNeuroDatasets/ds001734/{DATA_COMMIT}/participants.tsv"
METHODS = f"https://raw.githubusercontent.com/poldrack/narps/{METHODS_COMMIT}/ImageAnalyses/metadata_files/analysis_pipelines_for_analysis.xlsx"


def sha256(payload):
    return hashlib.sha256(payload).hexdigest()


def download(url):
    response = requests.get(url, timeout=(15, 90), headers={"User-Agent": "Mozilla/5.0 (STAMPED public study preparation)"})
    response.raise_for_status()
    return response.content


def write_identical(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        assert path.read_bytes() == payload, f"Existing frozen input differs: {path}"
    else:
        path.write_bytes(payload)


def prepare():
    participants_bytes = download(PARTICIPANTS)
    participants = pd.read_csv(io.BytesIO(participants_bytes), sep="\t")
    selected = participants.loc[participants.group == "equalIndifference"].copy()
    assert len(selected) == 54 and selected.participant_id.is_unique
    expected = set(selected.participant_id)
    original = json.loads(download(API))
    assert original["next"] is None and len(original["results"]) == original["count"]
    images = []
    for image in original["results"]:
        match = re.fullmatch(r"sub (\d+) hypo1 cope", image["name"])
        if match and image["analysis_level"] == "single-subject":
            assert image["map_type"] == "univariate-beta map"
            assert image["number_of_subjects"] == 1
            assert image["is_thresholded"] is False
            assert image["target_template_image"] == "MNI152NLin2009cAsym"
            images.append({**image, "participant_id": "sub-" + match[1]})
    assert len(images) == 54 and {x["participant_id"] for x in images} == expected
    images.sort(key=lambda x: x["participant_id"])
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    # Only selected participant metadata, never the collection's group answers.
    write_identical(EVIDENCE / "neurovault-participant-metadata.json", (json.dumps(images, indent=2) + "\n").encode())
    write_identical(EVIDENCE / "original-participants.tsv", participants_bytes)
    methods_bytes = download(METHODS)
    methods = pd.read_excel(io.BytesIO(methods_bytes), header=1)
    row = methods.loc[methods.teamID.str.strip() == "AO86"]
    assert len(row) == 1
    fields = ["teamID", "n_participants", "used_fmriprep_data", "data_submitted_to_model",
              "independent_vars_first_level", "analysis_SW_with_version"]
    upstream = row.iloc[0][fields].to_dict()
    write_identical(EVIDENCE / "upstream-methods.json", (json.dumps(upstream, indent=2) + "\n").encode())
    write_identical(PACKAGE / "participants.tsv", selected.to_csv(sep="\t", index=False).encode())
    old_manifest = PACKAGE / "sources.json"
    old_files = json.loads(old_manifest.read_text())["files"] if old_manifest.exists() else {}

    def obtain(image):
        filename = image["file"].rsplit("/", 1)[-1]
        assert filename == image["participant_id"] + "_hypo1_cope.nii.gz"
        relative = "data/" + filename
        path = PACKAGE / relative
        url = image["file"].replace("http:", "https:", 1)
        payload = path.read_bytes() if path.exists() else download(url)
        assert len(payload) == image["file_size"], filename
        if relative in old_files:
            assert sha256(payload) == old_files[relative]["sha256"], filename
        write_identical(path, payload)
        return relative, {"url": url, "image_id": image["id"],
                          "participant_id": image["participant_id"],
                          "bytes": len(payload), "sha256": sha256(payload),
                          "transformation": "none"}

    with ThreadPoolExecutor(max_workers=4) as pool:
        files = dict(pool.map(obtain, images))
    for name in ("participants.tsv", "upstream-methods.md", "study-task.md"):
        payload = (PACKAGE / name).read_bytes()
        files[name] = {"bytes": len(payload), "sha256": sha256(payload)}
    manifest = {
        "study": "NARPS Hypothesis 1: group inference from fixed participant effects",
        "collection": "https://neurovault.org/collections/4932/",
        "team": "AO86", "image_metadata_api": API,
        "selection": "All single-subject unthresholded hypo1 cope images; participant IDs exactly match the 54 equalIndifference participants in the pinned source table.",
        "maps": len(images), "map_bytes": sum(x["file_size"] for x in images),
        "map_type": "participant contrast parameter estimate, not a z/t statistic or a group result",
        "spatial_reference": "MNI152NLin2009cAsym",
        "upstream_processing_fixed": True,
        "cohort_source": {"url": PARTICIPANTS, "git_commit": DATA_COMMIT,
                          "sha256": sha256(participants_bytes),
                          "transformation": "Select group == equalIndifference; preserve all columns and values."},
        "methods_source": {"url": METHODS, "git_commit": METHODS_COMMIT,
                           "sha256": sha256(methods_bytes), "sheet": "Sheet1",
                           "header_excel_row": 2, "team_id": "AO86"},
        "checksum_scope": "SHA256 values are computed from retrieved bytes; NeuroVault metadata independently supplies file sizes but no source checksums.",
        "files": dict(sorted(files.items())),
    }
    old_manifest.write_text(json.dumps(manifest, indent=2) + "\n")


def verify(started):
    manifest = json.loads((PACKAGE / "sources.json").read_text())
    expected = set(manifest["files"]) | {"sources.json"}
    actual = {str(p.relative_to(PACKAGE)) for p in PACKAGE.rglob("*") if p.is_file()}
    assert actual == expected, {"missing": sorted(expected - actual), "extra": sorted(actual - expected)}
    maps = []
    geometry = None
    for relative, info in manifest["files"].items():
        path = PACKAGE / relative
        assert path.stat().st_size == info["bytes"], relative
        with path.open("rb") as stream:
            assert hashlib.file_digest(stream, "sha256").hexdigest() == info["sha256"], relative
        if not relative.endswith(".nii.gz"):
            continue
        image = nib.load(path)
        data = np.asanyarray(image.dataobj)
        assert data.ndim == 3 and np.isfinite(data).all() and np.count_nonzero(data), relative
        if geometry is None:
            geometry = (image.shape, image.affine)
        assert image.shape == geometry[0] and np.allclose(image.affine, geometry[1]), relative
        maps.append({"path": relative, "shape": list(image.shape),
                     "nonzero_voxels": int(np.count_nonzero(data)), "finite": True})
    assert len(maps) == 54
    cohort = pd.read_csv(PACKAGE / "participants.tsv", sep="\t")
    assert len(cohort) == 54 and set(cohort.group) == {"equalIndifference"}
    assert set(cohort.participant_id) == {x["participant_id"] for x in manifest["files"].values() if "participant_id" in x}
    report = {
        "verified_at": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": time.monotonic() - started,
        "versions": {"python": platform.python_version(), "nibabel": nib.__version__,
                     "numpy": np.__version__, "pandas": pd.__version__},
        "input_manifest_sha256": sha256((PACKAGE / "sources.json").read_bytes()),
        "all_hashes_match": True, "cohort_matches": True,
        "all_maps_finite": True, "common_geometry": True,
        "affine": geometry[1].tolist(), "maps": maps,
        "scientific_analysis_executed": False,
    }
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    (EVIDENCE / "verification.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"Verified 54 participant maps ({manifest['map_bytes']:,} bytes), cohort, geometry and input hashes.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    started = time.monotonic()
    if not args.verify_only:
        prepare()
    verify(started)
