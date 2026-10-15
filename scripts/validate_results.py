"""Independent numerical checks for the completed NARPS group analysis."""
import json
from pathlib import Path

import nibabel as nib
import numpy as np
import pandas as pd
from scipy.stats import ttest_1samp

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "input"
OUT = ROOT / "results"


def main():
    summary = json.loads((OUT / "results.json").read_text())
    participants = pd.read_csv(INPUT / "participants.tsv", sep="\t")
    arrays = np.stack([
        nib.load(str(INPUT / "data" / f"{pid}_hypo1_cope.nii.gz")).get_fdata(dtype=np.float32)
        for pid in participants.participant_id
    ])
    roi = nib.load(str(OUT / "vmPFC-atlas-mask.nii.gz")).get_fdata() > 0
    mask = nib.load(str(OUT / "whole-brain-mask.nii.gz")).get_fdata() > 0
    tmap = nib.load(str(OUT / "group-t-positive.nii.gz")).get_fdata()
    pmap = nib.load(str(OUT / "group-fwe-p-positive.nii.gz")).get_fdata()
    max_null = np.loadtxt(OUT / "permutation-max-t.tsv", skiprows=1)

    checks = {}
    for name, location in (("global_positive_peak", summary["global_positive_peak"]),
                           ("vmPFC_peak", summary["vmPFC_peak"])):
        ijk = tuple(location["ijk"])
        independent_t = float(ttest_1samp(arrays[(slice(None),) + ijk], 0.0).statistic)
        expected_t = float(location["t"])
        assert np.isclose(independent_t, expected_t, rtol=1e-5, atol=1e-6), (name, independent_t, expected_t)
        p_fwe = float((1 + np.count_nonzero(max_null >= independent_t)) / (len(max_null) + 1))
        stored_p = float(pmap[ijk])
        assert np.isclose(p_fwe, stored_p, atol=1e-8), (name, p_fwe, stored_p)
        checks[name] = {"scipy_t": independent_t, "maxT_fwe_p": p_fwe, "stored_fwe_p": stored_p}

    participant_roi = arrays[:, roi & mask].mean(axis=1)
    roi_mean = float(participant_roi.mean())
    assert np.isclose(roi_mean, summary["vmPFC_mean_across_voxels"], atol=1e-8)
    sig_count = int(((pmap <= .05) & mask).sum())
    assert sig_count == summary["n_whole_brain_fwe_voxels"]
    assert int((((pmap <= .05) & mask & roi).sum())) == summary["n_vmPFC_fwe_voxels"]
    checks["vmPFC_mean"] = roi_mean
    checks["fwe_voxel_count"] = sig_count
    checks["vmPFC_fwe_voxel_count"] = summary["n_vmPFC_fwe_voxels"]
    print(json.dumps({"independent_checks": "passed", "checks": checks}, indent=2))


if __name__ == "__main__":
    main()
