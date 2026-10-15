"""Curate archived team answers for coordinators, never as H1 worker inputs.

Run: pixi exec --spec nibabel --spec pandas --spec openpyxl python coordinator-guidance/prepare_team_results.py
"""
import gzip
import hashlib
import io
import json
import platform
import re
import tarfile
from datetime import datetime, timezone
from pathlib import Path

import nibabel as nib
import numpy as np
import openpyxl
import pandas as pd

root = Path(__file__).resolve().parents[1]
original = root / "coordinator-guidance/published"
package = root / "coordinator-guidance/team-results"
previous_sources = json.loads((original / "sources.json").read_text())
archive_source = previous_sources["input_archive"]
archive_path = original / archive_source["path"]
with archive_path.open("rb") as stream:
    assert hashlib.file_digest(stream, "md5").hexdigest() == archive_source["checksum"].split(":")[1]
assert archive_path.stat().st_size == archive_source["bytes"]

files, maps, raw = {}, {}, {}
metadata_names = {
    "./orig/narps_results.xlsx",
    "./orig/narps_neurovault_images_details_responses_corrected.csv",
    "./orig/analysis_pipelines_for_analysis.xlsx",
    "./orig/SuppTable3_exclusions.tsv",
}

def write_payload(relative, payload, provenance):
    path = package / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        assert path.read_bytes() == payload, f"Existing input differs: {path}"
    else:
        path.write_bytes(payload)
    files[relative] = {
        "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest(),
        "md5": hashlib.md5(payload).hexdigest(), **provenance,
    }

with tarfile.open(archive_path, mode="r|gz") as archive:
    for member in archive:
        match = re.fullmatch(r"\./orig/(\d+)_([A-Z0-9]{4})/hypo1_unthresh\.nii\.gz", member.name)
        if match:
            payload = archive.extractfile(member).read()
            image = nib.Nifti1Image.from_bytes(gzip.decompress(payload))
            assert len(image.shape) == 3
            team = match[2]
            assert team not in maps
            relative = "data/" + member.name.removeprefix("./")
            write_payload(relative, payload, {"archive_member": member.name, "transformation": "none"})
            maps[team] = {"path": relative, "collection_id": match[1],
                          "shape": list(image.shape),
                          "nonfinite_voxels": int(np.count_nonzero(~np.isfinite(np.asanyarray(image.dataobj))))}
        elif member.name in metadata_names:
            raw[member.name] = archive.extractfile(member).read()
assert maps and set(raw) == metadata_names
teams = set(maps)

# Decisions: original workbook cells only, with Excel row numbers retained.
decision_member = "./orig/narps_results.xlsx"
decisions = pd.read_excel(io.BytesIO(raw[decision_member]), sheet_name="all_results", header=None)
assert "Hypothesis 1" in str(decisions.iloc[0, 1]) and decisions.iloc[1, 1] == "Decision"
observations = []
for index, row in decisions.iloc[2:].iterrows():
    if row.iloc[0] in teams:
        assert row.iloc[1] in ("Yes", "No")
        observations.append({"team_id": row.iloc[0], "decision": row.iloc[1], "source_excel_row": int(index) + 1})
observations = pd.DataFrame(observations).sort_values("team_id")
assert observations.team_id.is_unique and set(observations.team_id) == teams

def write_table(name, table, member, transformation, **details):
    write_payload("data/observations/" + name, table.to_csv(sep="\t", index=False).encode(), {
        "archive_member": member,
        "source_member_md5": hashlib.md5(raw[member]).hexdigest(),
        "source_member_sha256": hashlib.sha256(raw[member]).hexdigest(),
        "transformation": transformation, **details,
    })

write_table("hypothesis1_decisions.tsv", observations, decision_member,
            "Rows for supplied-map teams; original cells A (team) and B (Hypothesis 1 decision); no recoding.",
            source_sheet="all_results", source_header_rows=[1, 2])

image_member = "./orig/narps_neurovault_images_details_responses_corrected.csv"
images = pd.read_csv(io.BytesIO(raw[image_member]))
# Preserve metadata values verbatim, changing column labels only.
image_columns = {"source_timestamp": 0, "team_id": 1, "software": 2, "statistic_type": 3,
                 "reported_template": 5, "image_comments": 9}
selected = images.iloc[:, list(image_columns.values())].copy()
selected.columns = list(image_columns)
selected["source_csv_row"] = selected.index + 2
selected = selected[selected.team_id.isin(teams)].sort_values("team_id")
assert set(selected.team_id) == teams
image_metadata_repeated_teams = sorted(selected.loc[selected.team_id.duplicated(), "team_id"].unique())
write_table("image_metadata.tsv", selected, image_member,
            "Rows for supplied-map teams; selected descriptive columns; no interpretation or recoding.",
            source_columns={name: str(images.columns[index]) for name, index in image_columns.items()})

pipeline_member = "./orig/analysis_pipelines_for_analysis.xlsx"
pipelines = pd.read_excel(io.BytesIO(raw[pipeline_member]), sheet_name="Sheet1", header=1)
columns = ["teamID", "n_participants", "exclusions_details", "used_fmriprep_data",
           "inter_subject_reg", "spatial_smoothing", "data_submitted_to_model",
           "spatial_region_modeled", "independent_vars_first_level",
           "independent_vars_higher_level", "model_type", "model_settings",
           "inference_contrast_effect", "search_region", "statistic_type",
           "pval_computation", "multiple_testing_correction",
           "region_definition_vmpfc", "analysis_SW_with_version"]
selected = pipelines.loc[:, columns].copy()
selected["source_excel_row"] = selected.index + 3
selected["source_team_id"] = selected.teamID
selected["teamID"] = selected.teamID.str.strip()
selected = selected[selected.teamID.isin(teams)].sort_values("teamID")
assert selected.teamID.is_unique and set(selected.teamID) == teams
write_table("pipeline_metadata.tsv", selected, pipeline_member,
            "Rows for supplied-map teams; selected methods fields; trim surrounding whitespace from teamID while retaining source_team_id. No result-comment or aggregate-result fields.",
            source_sheet="Sheet1", source_header_rows=[1, 2], source_columns=columns)

exclusion_member = "./orig/SuppTable3_exclusions.tsv"
write_payload("data/orig/SuppTable3_exclusions.tsv", raw[exclusion_member],
              {"archive_member": exclusion_member, "transformation": "none"})
for template in previous_sources["templates"]:
    payload = (original / template["path"]).read_bytes()
    assert "sha256:" + hashlib.sha256(payload).hexdigest() == template["checksum"]
    write_payload("data/templates/" + template["path"], payload,
                  {"url": template["url"], "source_release": template["source_release"],
                   "source_commit": template["source_commit"], "transformation": "none"})

manifest = {
    "study": "NARPS gain consistency",
    "data_source": {key: archive_source[key] for key in ("url", "bytes", "checksum", "license")},
    "data_description_doi": "10.1038/s41597-019-0113-7",
    "team_analysis_publication_doi": "10.1038/s41586-020-2314-9",
    "selection": "Every original ./orig/<numeric collection>_<four-character team>/hypo1_unthresh.nii.gz member in the input archive; metadata restricted to those team IDs. No computed reference outputs used for selection.",
    "hypothesis": "Positive parametric effect of potential gains in vmPFC, equal-indifference group.",
    "hypothesis_source": {"archive_member": decision_member, "sheet": "all_results", "cell": "B1"},
    "team_count": len(teams), "files": dict(sorted(files.items())),
}
(package / "sources.json").write_text(json.dumps(manifest, indent=2) + "\n")
expected = set(files) | {"prompt.md", "sources.json"}
actual = {str(path.relative_to(package)) for path in package.rglob("*") if path.is_file()}
assert actual == expected, {"unexpected": sorted(actual - expected), "missing": sorted(expected - actual)}
report = {
    "verified_at": datetime.now(timezone.utc).isoformat(),
    "command": "pixi exec --spec nibabel --spec pandas --spec openpyxl python coordinator-guidance/prepare_team_results.py",
    "versions": {"python": platform.python_version(), "nibabel": nib.__version__,
                 "numpy": np.__version__, "pandas": pd.__version__, "openpyxl": openpyxl.__version__},
    "source_archive_checksum_match": True,
    "selection_used_computed_reference": False,
    "input_data_files": len(files), "input_data_bytes": sum(item["bytes"] for item in files.values()),
    "team_count": len(teams), "all_maps_readable": True,
    "metadata_team_sets_match_maps": True,
    "image_metadata_repeated_teams": image_metadata_repeated_teams,
    "input_inventory_matches_manifest": True,
    "input_sources_sha256": hashlib.sha256((package / "sources.json").read_bytes()).hexdigest(),
    "maps": dict(sorted(maps.items())), "scientific_analysis_executed": False,
}
(root / "coordinator-guidance/team-results-verification.json").write_text(json.dumps(report, indent=2) + "\n")
print(f"Prepared {len(teams)} original maps with matching observations; {len(files)} data files, {report['input_data_bytes']} bytes.")
