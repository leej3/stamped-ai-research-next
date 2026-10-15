#!/usr/bin/env python3
"""Group analysis of NARPS AO86 equal-indifference gain-effect maps.

Primary inference: one-sample t at each voxel for positive mean cope, calibrated
with random sign-flip max-t permutation (one-sided; 9,999 draws; seed 20261015).
No upstream preprocessing or first-level modeling is performed here.
"""
from __future__ import annotations
import hashlib, json, os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/narps-mpl")
import numpy as np
import pandas as pd
import nibabel as nib
from scipy import stats
import matplotlib.pyplot as plt
from nilearn import plotting

ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / "input"
OUT = ROOT / "results"
SEED = 20261015
N_PERM = int(os.environ.get("NARPS_PERMUTATIONS", "9999"))
BATCH = 128
VM_PFC = dict(x=(-15, 15), y=(25, 65), z=(-25, 5))

participants = pd.read_csv(INPUT / "participants.tsv", sep="\t")
source = json.loads((INPUT / "sources.json").read_text())
assert len(participants) == 54 and participants.participant_id.is_unique
assert set(participants.group) == {"equalIndifference"}
files = source["files"]
assert len([k for k in files if k.endswith(".nii.gz")]) == 54

imgs, data, qc = [], [], []
ref = None
for row in participants.itertuples(index=False):
    rel = f"data/{row.participant_id}_hypo1_cope.nii.gz"
    meta = files[rel]
    path = INPUT / rel
    raw = path.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    if sha != meta["sha256"]:
        raise ValueError(f"SHA256 mismatch: {rel}")
    img = nib.load(str(path))
    if ref is None:
        ref = img
    if img.shape != ref.shape or not np.allclose(img.affine, ref.affine, atol=1e-5):
        raise ValueError(f"Grid mismatch: {rel}")
    vol = img.get_fdata(dtype=np.float32)
    if not np.isfinite(vol).all():
        raise ValueError(f"Nonfinite voxels: {rel}")
    imgs.append(img)
    data.append(vol)
    nonzero = vol != 0
    qc.append({"participant_id": row.participant_id, "age": row.age, "gender": row.gender,
               "sha256_ok": True, "n_nonzero_voxels": int(nonzero.sum()),
               "whole_grid_mean_including_zeros": float(vol.mean()),
               "nonzero_mean": float(vol[nonzero].mean()),
               "nonzero_sd": float(vol[nonzero].std()),
               "nonzero_min": float(vol[nonzero].min()), "nonzero_max": float(vol[nonzero].max())})
X = np.stack(data, axis=0)
# Exact common support avoids treating uncovered voxels as zero-valued measurements.
mask = np.all(X != 0, axis=0)
if mask.sum() < 10000:
    raise ValueError("Unexpectedly small common-support mask")
Y = X[:, mask].astype(np.float64)
n, v = Y.shape

# Primary group model: intercept-only one-sample t test of participant effects.
mean = Y.mean(axis=0)
sd = Y.std(axis=0, ddof=1)
t_obs = mean / (sd / np.sqrt(n))
p_unc = stats.t.sf(t_obs, df=n-1)

# One-sided max-t sign-flip test. Sign changes are applied at participant level,
# retaining each participant's spatial dependence and controlling FWER over voxels.
rng = np.random.default_rng(SEED)
max_t = np.empty(N_PERM, dtype=np.float32)
Y32 = Y.astype(np.float32)
sq = np.sum(Y32 * Y32, axis=0)
for start in range(0, N_PERM, BATCH):
    stop = min(start + BATCH, N_PERM)
    signs = rng.choice(np.array([-1.0, 1.0], dtype=np.float32), size=(stop-start, n)).astype(np.float32)
    sums = signs @ Y32
    # Studentized signed means, using invariant sum of squares.
    numer = sums / n
    var = np.maximum((sq[None, :] - sums * sums / n) / (n-1), 1e-20)
    t_perm = numer / np.sqrt(var / n)
    max_t[start:stop] = np.max(t_perm, axis=1)
    del signs, sums, numer, var, t_perm
# Sort permutation maxima, then calculate exceedances by binary search without
# allocating an N_PERM × voxel array.
sorted_max_t = np.sort(max_t)
exceed = N_PERM - np.searchsorted(sorted_max_t, t_obs, side="left")
p_fwe = (1 + exceed) / (N_PERM + 1)

# ROI is a broad, coordinate-defined anatomical localization (MNI); inference
# remains whole-brain. ROI result is reported only with whole-brain FWE p.
ijk = np.indices(ref.shape).reshape(3, -1).T
xyz = nib.affines.apply_affine(ref.affine, ijk)
roi_grid = ((xyz[:,0] >= VM_PFC['x'][0]) & (xyz[:,0] <= VM_PFC['x'][1]) &
            (xyz[:,1] >= VM_PFC['y'][0]) & (xyz[:,1] <= VM_PFC['y'][1]) &
            (xyz[:,2] >= VM_PFC['z'][0]) & (xyz[:,2] <= VM_PFC['z'][1])).reshape(ref.shape)
roi = roi_grid[mask]
roi_peak_i = int(np.argmax(np.where(roi, t_obs, -np.inf))) if roi.any() else None
roi_t = float(t_obs[roi_peak_i]) if roi_peak_i is not None else float("nan")
roi_mean = float(mean[roi].mean()) if roi.any() else float("nan")
roi_subject = Y[:, roi].mean(axis=1) if roi.any() else np.full(n, np.nan)
roi_ci = stats.t.interval(.95, df=n-1, loc=float(np.mean(roi_subject)),
                          scale=float(stats.sem(roi_subject))) if roi.any() else (np.nan, np.nan)
roi_peak_xyz = xyz[mask.reshape(-1)][roi_peak_i].tolist() if roi_peak_i is not None else None

# Unthresholded and FWE-thresholded image outputs.
def unmask(values, fill=0):
    a = np.full(ref.shape, fill, dtype=np.float32)
    a[mask] = np.asarray(values, dtype=np.float32)
    return a

def save_img(values, name):
    out = nib.Nifti1Image(unmask(values), ref.affine, ref.header)
    out.set_data_dtype(np.float32)
    nib.save(out, OUT / "maps" / name)

save_img(mean, "group_mean_cope.nii.gz")
save_img(t_obs, "group_t_positive.nii.gz")
save_img(p_fwe, "group_p_fwe_positive.nii.gz")
save_img(np.where(p_fwe <= .05, t_obs, 0), "group_t_fwe05_positive.nii.gz")

pd.DataFrame(qc).to_csv(OUT / "tables" / "participant_qc.csv", index=False)
# Per-voxel table is intentionally compact, and includes all inferential quantities.
summary = {"n": n, "mask_voxels": int(v), "mask_fraction_of_grid": float(mask.mean()),
          "df": n-1, "permutations": N_PERM, "seed": SEED,
          "mean_cope_brain": float(mean.mean()), "median_cope_brain": float(np.median(mean)),
          "positive_fraction_brain": float(np.mean(mean > 0)),
          "max_t_whole_brain": float(t_obs.max()),
          "max_t_xyz_mni_mm": xyz[mask.reshape(-1)][int(np.argmax(t_obs))].tolist(),
          "max_t_p_uncorrected": float(p_unc[int(np.argmax(t_obs))]),
          "max_t_p_fwe_positive": float(p_fwe.max() if False else p_fwe[int(np.argmax(t_obs))]),
          "voxel_count_p_fwe_le_05": int((p_fwe <= .05).sum()),
          "vmPFC_box_mni_mm": VM_PFC, "vmPFC_box_voxels": int(roi.sum()),
          "vmPFC_box_mean_of_voxel_means": roi_mean, "vmPFC_max_t": roi_t,
          "vmPFC_mean_participant_box_average": float(np.mean(roi_subject)),
          "vmPFC_mean_participant_box_average_ci95": [float(roi_ci[0]), float(roi_ci[1])],
          "vmPFC_peak_xyz_mni_mm": roi_peak_xyz,
          "vmPFC_peak_p_fwe_positive": float(p_fwe[roi_peak_i]) if roi_peak_i is not None else None,
          "vmPFC_fwe_voxels_positive": int(np.sum((p_fwe <= .05) & roi)),
          "vmPFC_hypothesis_supported": bool(np.any((p_fwe <= .05) & roi)),
          "whole_brain_any_positive_fwe_voxels": int(np.sum(p_fwe <= .05))}
(OUT / "tables" / "group_summary.json").write_text(json.dumps(summary, indent=2) + "\n")

# Figure 1: participant-level average effect within the anatomical vmPFC box.
fig, ax = plt.subplots(figsize=(8.2, 4.8), constrained_layout=True)
ax.hist(roi_subject, bins=12, color="#4c78a8", edgecolor="white")
ax.axvline(0, color="black", lw=1, ls="--")
ax.set(xlabel="Participant mean gain-effect estimate (cope; vmPFC box average)", ylabel="Participants",
       title="vmPFC box: participant-level gain-effect estimates")
fig.savefig(OUT / "figures" / "participant_effects.png", dpi=180)
plt.close(fig)

# Figure 2: whole-brain corrected evidence, with anatomically located vmPFC box peak.
stat_img = nib.Nifti1Image(unmask(np.where(p_fwe <= .05, t_obs, 0)), ref.affine, ref.header)
display = plotting.plot_stat_map(stat_img, bg_img=None, display_mode="ortho",
    cut_coords=tuple(summary["max_t_xyz_mni_mm"]), threshold=0, cmap="cold_hot", colorbar=True,
    title="Positive gain effect: voxelwise max-t FWE p ≤ .05")
display.savefig(OUT / "figures" / "whole_brain_fwe.png", dpi=180)
plt.close("all")

# Figure 3: unthresholded t-map around the vmPFC box, to show estimation pattern;
# this is explicitly descriptive and not inferential support.
all_t = nib.Nifti1Image(unmask(t_obs), ref.affine, ref.header)
display = plotting.plot_stat_map(all_t, bg_img=None, display_mode="ortho",
    cut_coords=(0, 42, -10), threshold=None, cmap="cold_hot", colorbar=True,
    title="Unthresholded positive gain-effect t map (descriptive)")
display.savefig(OUT / "figures" / "whole_brain_unthresholded.png", dpi=180)
plt.close("all")

print(json.dumps(summary, indent=2))
