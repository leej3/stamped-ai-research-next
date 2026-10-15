#!/usr/bin/env python3
"""Group analysis of NARPS equal-indifference potential-gain effect maps.

Primary inference: one-sample, positive-direction t test with participant-level
sign flips and whole-brain max-t familywise-error correction. This is group
analysis only; supplied first-level effect maps are treated as fixed inputs.
"""
from pathlib import Path
import hashlib, json, sys
import importlib.metadata

import nibabel as nib
import numpy as np
import pandas as pd
from scipy import stats
from scipy.ndimage import gaussian_filter
import matplotlib.pyplot as plt
from nilearn import plotting, datasets
from nilearn.image import resample_to_img

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results"
OUT.mkdir(exist_ok=True)
SEED = 20261015
N_PERM = 10000
ROI_CENTER = (0.0, 40.0, -10.0)  # a priori ventromedial prefrontal location, MNI mm
ROI_RADIUS = 15.0

participants = pd.read_csv(ROOT / "input/participants.tsv", sep="\t")
sources = json.loads((ROOT / "input/sources.json").read_text())
assert len(participants) == 54 and participants.participant_id.is_unique
files = [ROOT / "input/data" / f"{pid}_hypo1_cope.nii.gz" for pid in participants.participant_id]
images, data, qc = [], [], []
reference = None
for pid, path in zip(participants.participant_id, files):
    img = nib.load(path)
    arr = img.get_fdata(dtype=np.float32)
    if reference is None:
        reference = img
    same = arr.shape == reference.shape and np.allclose(img.affine, reference.affine, atol=1e-4)
    finite = np.isfinite(arr)
    nz = finite & (arr != 0)
    actual_sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
    expected_sha256 = sources["files"][f"data/{path.name}"]["sha256"]
    if actual_sha256 != expected_sha256:
        raise ValueError(f"Source SHA256 mismatch: {pid}")
    qc.append({"participant_id": pid, "shape": list(arr.shape), "same_geometry": bool(same),
               "finite_fraction": float(finite.mean()), "nonzero_fraction": float(nz.mean()),
               "mean_nonzero": float(np.mean(arr[nz])) if nz.any() else np.nan,
               "sd_nonzero": float(np.std(arr[nz])) if nz.any() else np.nan,
               "min_nonzero": float(np.min(arr[nz])) if nz.any() else np.nan,
               "max_nonzero": float(np.max(arr[nz])) if nz.any() else np.nan,
               "sha256": actual_sha256, "source_sha256_match": True})
    if not same or not finite.all():
        raise ValueError(f"Invalid map geometry or nonfinite values: {pid}")
    data.append(arr)
    images.append(img)
pd.DataFrame(qc).to_csv(OUT / "quality_checks.tsv", sep="\t", index=False)
Xall = np.stack(data, axis=0)
# Common coverage, established without reference to effect direction/magnitude.
coverage = np.mean(Xall != 0, axis=0)
mask = coverage >= 0.90
if mask.sum() < 10000:
    raise ValueError(f"Unexpectedly small analysis mask: {mask.sum()}")
X = Xall[:, mask].astype(np.float64)
n, v = X.shape

# Primary estimate and classical one-sample t field.
mean = X.mean(axis=0)
sd = X.std(axis=0, ddof=1)
t_obs = mean / (sd / np.sqrt(n))
df = n - 1
p_unc = stats.t.sf(t_obs, df)

# Monte Carlo sign-flip max-t. Include the observed sign configuration in the
# reference distribution; add-one p-values avoid zero estimates.
rng = np.random.default_rng(SEED)
signs = rng.choice(np.array([-1.0, 1.0]), size=(N_PERM, n))
signs[0, :] = 1.0
max_t = np.empty(N_PERM, dtype=np.float64)
sum_sq = np.sum(X * X, axis=0)
chunk = 12000
for start in range(0, v, chunk):
    stop = min(start + chunk, v)
    block = X[:, start:stop]
    sums = signs @ block
    var_num = np.maximum(sum_sq[start:stop][None, :] - sums * sums / n, 1e-12)
    t_perm = sums * np.sqrt((n - 1) / (n * var_num))
    max_t = np.maximum(max_t, np.max(t_perm, axis=1)) if start else np.max(t_perm, axis=1)
    print(f"permutation voxels {stop}/{v}", file=sys.stderr)
p_fwe = np.empty(v, dtype=np.float64)
for start in range(0, v, chunk):
    stop = min(start + chunk, v)
    p_fwe[start:stop] = (1 + np.sum(max_t[:, None] >= t_obs[None, start:stop], axis=0)) / (N_PERM + 1)
max_t_cut = float(np.quantile(max_t, 0.95, method="higher"))

# Reconstruct image fields, retaining NaN outside the analysis mask for clarity.
def image_from_values(values, name):
    arr = np.full(mask.shape, np.nan, dtype=np.float32)
    arr[mask] = values.astype(np.float32)
    img = nib.Nifti1Image(arr, reference.affine, reference.header)
    nib.save(img, OUT / name)
    return img

t_img = image_from_values(t_obs, "group_t_unthresholded.nii.gz")
mean_img = image_from_values(mean, "group_mean_effect.nii.gz")
pfwe_img = image_from_values(p_fwe, "group_p_fwe.nii.gz")
sig_vals = np.where(p_fwe < 0.05, t_obs, np.nan)
sig_img = image_from_values(sig_vals, "group_t_fwe05.nii.gz")

# A priori spherical vmPFC summary, centered in medial OFC/vmPFC. Define the
# anatomical region in MNI coordinates, independently of the observed maps.
ijk = np.indices(reference.shape).reshape(3, -1).T
coords = nib.affines.apply_affine(reference.affine, ijk)
roi_full = np.sum((coords - np.asarray(ROI_CENTER)) ** 2, axis=1).reshape(reference.shape) <= ROI_RADIUS**2
roi = roi_full & mask
if roi.sum() == 0:
    raise ValueError("ROI has no voxels in common coverage")
roi_ids = np.where(roi.ravel())[0]
Xroi = Xall.reshape(n, -1)[:, roi_ids].astype(np.float64)
roi_person = Xroi.mean(axis=1)
roi_mean = float(roi_person.mean())
roi_sd = float(roi_person.std(ddof=1))
roi_se = roi_sd / np.sqrt(n)
roi_t = roi_mean / roi_se
roi_p = float(stats.t.sf(roi_t, n - 1))
roi_ci = stats.t.ppf(0.975, n - 1) * roi_se
roi_signs = rng.choice(np.array([-1.0, 1.0]), size=(N_PERM, n))
roi_sums = roi_signs @ roi_person
roi_sum_sq = float(np.sum(roi_person**2))
roi_null = roi_sums * np.sqrt((n - 1) / (n * np.maximum(roi_sum_sq - (roi_sums**2 / n), 1e-12)))
roi_p_perm = float((1 + np.sum(roi_null >= roi_t)) / (N_PERM + 1))

# Whole brain peak and vmPFC peak report.
peak_idx = int(np.nanargmax(t_obs))
peak_xyz = nib.affines.apply_affine(reference.affine, np.argwhere(mask)[peak_idx]).tolist()
roi_masked = mask.ravel()[roi_ids]
roi_positions = np.flatnonzero(mask)[np.isin(np.flatnonzero(mask), roi_ids)]
roi_local = np.flatnonzero(np.isin(np.flatnonzero(mask), roi_ids))
if len(roi_local):
    roi_peak_local = roi_local[np.argmax(t_obs[roi_local])]
    roi_peak_xyz = nib.affines.apply_affine(reference.affine, np.argwhere(mask)[roi_peak_local]).tolist()
    roi_peak_t = float(t_obs[roi_peak_local])
    roi_peak_pfwe = float(p_fwe[roi_peak_local])
else:
    roi_peak_xyz, roi_peak_t, roi_peak_pfwe = None, None, None

summary = {
    "n_participants": n, "excluded": [], "analysis_voxels": int(v),
    "coverage_rule": "nonzero effect estimate in >=90% of participants",
    "permutations": N_PERM, "seed": SEED, "df": df,
    "software": {name: importlib.metadata.version(name) for name in ["numpy", "scipy", "nibabel", "nilearn"]},
    "max_t_fwe_0.05_cutoff": max_t_cut,
    "whole_brain_positive_peak": {"t": float(t_obs[peak_idx]), "p_fwe": float(p_fwe[peak_idx]), "xyz_mni_mm": peak_xyz},
    "whole_brain_significant_voxels_p_fwe_lt_0.05": int(np.sum(p_fwe < 0.05)),
    "vmPFC_roi": {"definition": f"sphere radius {ROI_RADIUS:g} mm centered at MNI {ROI_CENTER}; common-coverage voxels",
                  "n_voxels": int(roi.sum()), "participant_mean_effect_mean": roi_mean,
                  "participant_mean_effect_sd": roi_sd, "ci95": [roi_mean-roi_ci, roi_mean+roi_ci],
                  "one_sample_t": roi_t, "df": df, "p_one_sided_parametric": roi_p,
                  "p_one_sided_signflip": roi_p_perm,
                  "highest_voxel_t": roi_peak_t, "highest_voxel_p_fwe": roi_peak_pfwe,
                  "highest_voxel_xyz_mni_mm": roi_peak_xyz},
    "map_semantics": "group mean and t summarize supplied first-level gain-modulator coefficients; they are not BOLD change per currency unit or standardized z statistics",
}
(OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
pd.DataFrame({"participant_id": participants.participant_id, "vmPFC_mean_effect": roi_person}).to_csv(OUT / "vmPFC_participant_effects.tsv", sep="\t", index=False)

# Figures
plt.figure(figsize=(8, 4.5))
plt.hist(roi_person, bins=14, color="#3b78a3", edgecolor="white")
plt.axvline(0, color="black", linewidth=1)
plt.axvline(roi_mean, color="#bd3c2c", linewidth=2, label=f"Mean = {roi_mean:.3g}")
plt.xlabel("Participant mean gain-effect estimate in vmPFC sphere")
plt.ylabel("Participants")
plt.title("Equal-indifference group (n=54): vmPFC effect estimates")
plt.legend(frameon=False)
plt.tight_layout()
plt.savefig(OUT / "vmPFC_effect_distribution.png", dpi=180)
plt.close()

display = plotting.plot_stat_map(t_img, bg_img=datasets.load_mni152_template(resolution=2),
    display_mode="ortho", cut_coords=tuple(peak_xyz), threshold=max_t_cut,
    title="Gain effect: whole-brain max-t FWE p < .05 (peak slices)", cmap="cold_hot", colorbar=True)
display.savefig(OUT / "group_t_fwe_map.png", dpi=180)
display.close()

plt.figure(figsize=(7, 4.5))
plt.hist(max_t, bins=45, color="#a9bdca", edgecolor="white")
plt.axvline(max_t_cut, color="#bd3c2c", linewidth=2, label=f"95th percentile = {max_t_cut:.2f}")
plt.axvline(float(t_obs[peak_idx]), color="#263b4a", linestyle="--", label=f"Observed peak t = {t_obs[peak_idx]:.2f}")
plt.xlabel("Maximum positive t across the whole analysis mask")
plt.ylabel("Sign-flip permutations")
plt.title("Whole-brain familywise null distribution")
plt.legend(frameon=False)
plt.tight_layout()
plt.savefig(OUT / "max_t_permutation_null.png", dpi=180)
plt.close()
print(json.dumps(summary, indent=2))
