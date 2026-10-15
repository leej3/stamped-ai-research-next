#!/usr/bin/env python3
"""Group inference for supplied NARPS AO86 gain-effect maps."""
from __future__ import annotations

import hashlib
import json
import os
import platform
import sys
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
import pandas as pd
import scipy
from scipy import stats, ndimage

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results"
DATA = ROOT / "input" / "data"
N_PERM = int(os.environ.get("N_PERM", "9999"))
SEED = int(os.environ.get("SEED", "20261015"))
CHUNK = 32


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def save_map(data, ref, name, dtype=np.float32):
    img = nib.Nifti1Image(np.asarray(data, dtype=dtype), ref.affine, ref.header)
    img.set_data_dtype(dtype)
    nib.save(img, OUT / name)


def main():
    start = time.time()
    OUT.mkdir(exist_ok=True)
    meta = json.loads((ROOT / "input" / "sources.json").read_text())
    cohort = pd.read_csv(ROOT / "input" / "participants.tsv", sep="\t")
    paths = [DATA / f"{pid}_hypo1_cope.nii.gz" for pid in cohort.participant_id]
    missing = [str(p) for p in paths if not p.is_file()]
    if missing:
        raise FileNotFoundError(f"Missing maps: {missing}")

    imgs = [nib.load(str(p)) for p in paths]
    ref = imgs[0]
    if any(img.shape != ref.shape or not np.allclose(img.affine, ref.affine, atol=1e-5) for img in imgs):
        raise ValueError("Participant maps do not share a common grid and affine")
    raw = np.stack([img.get_fdata(dtype=np.float32) for img in imgs], axis=0)
    finite = np.isfinite(raw).all(axis=0)
    # These unthresholded maps encode voxels outside the acquired brain as zero.
    # The union support includes all observed in-brain coverage without selecting
    # voxels according to the sign or magnitude of the group effect.
    mask = finite & np.any(raw != 0, axis=0)
    if mask.sum() == 0:
        raise ValueError("Empty common-support mask")
    Y = raw[:, mask].astype(np.float64, copy=False)
    n, v = Y.shape
    mean = Y.mean(axis=0)
    sd = Y.std(axis=0, ddof=1)
    se = sd / np.sqrt(n)
    t_obs = np.divide(mean, se, out=np.zeros_like(mean), where=se > 0)
    p_unc = stats.t.sf(t_obs, n - 1)

    # One-sided sign-flip max-T permutation. Under the null, participant effects
    # are symmetric about zero; each permutation flips the whole participant map,
    # preserving its spatial dependence. Max positive t controls FWE over the
    # full analysis mask. Include observed all-positive assignment explicitly.
    rng = np.random.default_rng(SEED)
    denom = np.sqrt(np.maximum((np.sum(Y * Y, axis=0) - n * mean * mean) / (n - 1), 0) / n)
    max_t = np.empty(N_PERM + 1, dtype=np.float64)
    max_t[0] = np.max(t_obs)
    idx = 1
    while idx < N_PERM:
        b = min(CHUNK, N_PERM - idx)
        signs = rng.choice(np.array([-1.0, 1.0]), size=(b, n))
        perm_means = (signs @ Y) / n
        perm_t = np.divide(perm_means, denom[None, :], out=np.zeros_like(perm_means), where=denom[None, :] > 0)
        max_t[idx:idx+b] = np.max(perm_t, axis=1)
        idx += b
    p_fwe = (max_t[:, None] >= t_obs[None, :]).sum(axis=0) / (N_PERM + 1)

    mean_vol = np.zeros(ref.shape, np.float32); mean_vol[mask] = mean
    t_vol = np.zeros(ref.shape, np.float32); t_vol[mask] = t_obs
    p_vol = np.ones(ref.shape, np.float32); p_vol[mask] = p_fwe
    save_map(mean_vol, ref, "group_mean_effect.nii.gz")
    save_map(t_vol, ref, "group_tstat.nii.gz")
    save_map(p_vol, ref, "group_p_fwe_maxT.nii.gz")
    mask_vol = mask.astype(np.uint8)
    save_map(mask_vol, ref, "analysis_mask.nii.gz", np.uint8)

    # vmPFC is operationalized as a preregistered 10-mm MNI sphere centered
    # at (0, 45, -6), a compact medial ventral frontal localization. This ROI is
    # used for localization and descriptive effect summarization only; the
    # decision still requires whole-brain max-T significance in that ROI.
    ijk = np.indices(ref.shape).reshape(3, -1).T
    xyz = nib.affines.apply_affine(ref.affine, ijk)
    roi = (np.linalg.norm(xyz - np.array([0., 45., -6.]), axis=1) <= 10).reshape(ref.shape) & mask
    if not roi.any():
        raise ValueError("No analysis voxels overlap the vmPFC sphere")
    roi_values = raw[:, roi]
    roi_mean_subj = roi_values.mean(axis=1)
    roi_avg = float(roi_values.mean())
    roi_sd = float(roi_mean_subj.std(ddof=1))
    roi_ci = stats.t.interval(0.95, n - 1, loc=roi_avg, scale=roi_sd / np.sqrt(n))
    roi_peak_idx = np.flatnonzero(roi)
    # Robust peak lookup via full-volume index map.
    t_full = np.zeros(ref.shape, dtype=np.float64); t_full[mask] = t_obs
    roi_t_peak = float(np.max(t_full[roi]))
    roi_peak = np.argwhere(roi & (t_full == roi_t_peak))[0]
    roi_peak_p = float(p_vol[tuple(roi_peak)])
    n_roi_vox = int(roi.sum())
    supported = bool(np.any((p_vol <= .05) & roi))
    sig_mask = (p_vol <= .05) & mask
    labels, n_labels = ndimage.label(sig_mask, structure=np.ones((3, 3, 3), dtype=np.uint8))
    cluster_summaries = []
    for lab in range(1, n_labels + 1):
        coords = np.argwhere(labels == lab)
        peak = coords[np.argmax(t_full[tuple(coords.T)])]
        cluster_summaries.append({
            "voxels_26_connected": int(len(coords)),
            "peak_mni_mm": nib.affines.apply_affine(ref.affine, peak).tolist(),
            "peak_t": float(t_full[tuple(peak)]),
            "peak_p_fwe": float(p_vol[tuple(peak)]),
        })
    cluster_summaries.sort(key=lambda c: c["voxels_26_connected"], reverse=True)

    q = np.quantile(max_t, [.5, .95, .99]).tolist()
    qc = {
        "n_participants_expected": int(meta["maps"]), "n_participants_included": n,
        "excluded": [], "map_files": [str(p.relative_to(ROOT)) for p in paths],
        "map_sha256_match_sources": {p.name: sha256(p) == meta["files"][str(p.relative_to(ROOT / "input"))]["sha256"] for p in paths},
        "all_source_checksums_match": all(sha256(p) == meta["files"][str(p.relative_to(ROOT / "input"))]["sha256"] for p in paths),
        "shape": list(ref.shape), "voxel_size_mm": list(map(float, ref.header.get_zooms()[:3])),
        "analysis_mask_voxels": int(mask.sum()), "vmPFC_sphere_voxels_in_mask": n_roi_vox,
        "nonfinite_values": int((~np.isfinite(raw)).sum()), "zero_variance_analysis_voxels": int((sd == 0).sum()),
        "random_sign_flips": N_PERM, "permutation_distribution_including_observed": N_PERM + 1,
        "seed": SEED, "max_t_null_quantiles_50_95_99": q,
        "numpy": np.__version__, "scipy": scipy.__version__, "nibabel": nib.__version__,
        "python": sys.version.split()[0], "platform": platform.platform(),
        "elapsed_seconds": round(time.time() - start, 2),
    }
    (OUT / "quality_checks.json").write_text(json.dumps(qc, indent=2) + "\n")
    summary = {
        "n": n, "whole_brain_mask_voxels": int(mask.sum()), "random_sign_flips": N_PERM,
        "roi_definition_mni_mm": {"center": [0, 45, -6], "radius": 10},
        "roi_voxels": n_roi_vox, "roi_mean_effect": roi_avg,
        "roi_sd_subject_means": roi_sd, "roi_mean_95ci_t": [float(roi_ci[0]), float(roi_ci[1])],
        "roi_peak_mni_mm": nib.affines.apply_affine(ref.affine, roi_peak).tolist(),
        "roi_peak_t": roi_t_peak, "roi_peak_p_fwe_whole_brain": roi_peak_p,
        "roi_any_voxel_p_fwe_le_0.05": supported,
        "whole_brain_significant_voxels_positive": int((p_vol <= .05).sum()),
        "whole_brain_max_t": float(np.max(t_obs)), "whole_brain_max_p_fwe": float(np.min(p_fwe)),
        "whole_brain_peak_mni_mm": nib.affines.apply_affine(ref.affine, np.unravel_index(np.argmax(t_full), ref.shape)).tolist(),
        "positive_fwe_cluster_count_26_connected": int(n_labels),
        "largest_positive_fwe_clusters": cluster_summaries[:10],
        "interpretation": "Effect is the upstream normalized gain-modulator contrast estimate; not BOLD change per currency unit.",
    }
    (OUT / "results.json").write_text(json.dumps(summary, indent=2) + "\n")
    pd.DataFrame({"participant_id": cohort.participant_id, "vmPFC_mean_effect": roi_mean_subj}).to_csv(OUT / "vmPFC_participant_effects.csv", index=False)

    # MNI-coordinate slices use the common-support mask as a neutral backdrop.
    # The 10-mm vmPFC sphere is outlined in each orthogonal panel.
    midx = int(round((0 - ref.affine[0, 3]) / ref.affine[0, 0]))
    midy = int(round((45 - ref.affine[1, 3]) / ref.affine[1, 1]))
    midz = int(round((-6 - ref.affine[2, 3]) / ref.affine[2, 2]))
    farj = int(round((-100 - ref.affine[1, 3]) / ref.affine[1, 1]))
    panels = [
        (mask[midx, :, :].T, mean_vol[midx, :, :].T, (p_vol[midx, :, :].T <= .05),
         [ref.affine[1,3], ref.affine[1,3] + ref.affine[1,1]*(ref.shape[1]-1), ref.affine[2,3], ref.affine[2,3] + ref.affine[2,2]*(ref.shape[2]-1)],
         "Sagittal (x = 0 mm)", "y (mm)", "z (mm)", (45, -6), "yz"),
        (mask[:, midy, :].T, mean_vol[:, midy, :].T, (p_vol[:, midy, :].T <= .05),
         [ref.affine[0,3], ref.affine[0,3] + ref.affine[0,0]*(ref.shape[0]-1), ref.affine[2,3], ref.affine[2,3] + ref.affine[2,2]*(ref.shape[2]-1)],
         "Coronal (y = 45 mm)", "x (mm)", "z (mm)", (0, -6), "xz"),
        (mask[:, :, midz].T, mean_vol[:, :, midz].T, (p_vol[:, :, midz].T <= .05),
         [ref.affine[0,3], ref.affine[0,3] + ref.affine[0,0]*(ref.shape[0]-1), ref.affine[1,3], ref.affine[1,3] + ref.affine[1,1]*(ref.shape[1]-1)],
         "Axial (z = -6 mm)", "x (mm)", "y (mm)", (0, 45), "xy"),
        (mask[:, farj, :].T,
         mean_vol[:, farj, :].T,
         (p_vol[:, farj, :].T <= .05),
         [ref.affine[0,3], ref.affine[0,3] + ref.affine[0,0]*(ref.shape[0]-1), ref.affine[2,3], ref.affine[2,3] + ref.affine[2,2]*(ref.shape[2]-1)],
         "Coronal (y = -100 mm)", "x (mm)", "z (mm)", None, "xz_far"),
    ]
    lim = float(max(abs(np.quantile(mean, .01)), abs(np.quantile(mean, .99))))
    fig, axes = plt.subplots(2, len(panels), figsize=(15, 7), constrained_layout=True)
    for col, (m, e, s, extent, title, xlabel, ylabel, center, plane) in enumerate(panels):
        axes[0,col].imshow(m, origin="lower", extent=extent, cmap="Greys", vmin=0, vmax=2, interpolation="nearest")
        im1 = axes[0,col].imshow(np.ma.masked_where(m == 0, e), origin="lower", extent=extent,
                                cmap="RdBu_r", vmin=-lim, vmax=lim, interpolation="nearest")
        axes[0,col].set_title(title)
        axes[0,col].set_xlabel(xlabel); axes[0,col].set_ylabel(ylabel)
        if center is not None:
            axes[0,col].add_patch(plt.Circle(center, 10, fill=False, color="black", linewidth=1.3))
        axes[1,col].imshow(m, origin="lower", extent=extent, cmap="Greys", vmin=0, vmax=2, interpolation="nearest")
        t_slice = (t_vol[midx,:,:].T if plane == "yz" else (t_vol[:,midy,:].T if plane == "xz" else
                    (t_vol[:,:,midz].T if plane == "xy" else t_vol[:,farj,:].T)))
        im2 = axes[1,col].imshow(np.ma.masked_where(~s, t_slice),
                                origin="lower", extent=extent, cmap="inferno", vmin=0, vmax=max(5, float(np.max(t_obs))), interpolation="nearest")
        if center is not None:
            axes[1,col].add_patch(plt.Circle(center, 10, fill=False, color="cyan", linewidth=1.3))
        axes[1,col].set_xlabel(xlabel); axes[1,col].set_ylabel(ylabel)
    axes[0,0].set_ylabel("Mean effect\n" + panels[0][6]); axes[1,0].set_ylabel("Significant t\n" + panels[0][6])
    fig.colorbar(im1, ax=axes[0,:], shrink=.75, label="Mean upstream contrast estimate")
    fig.colorbar(im2, ax=axes[1,:], shrink=.75, label="t statistic (whole-brain max-T FWE p ≤ .05)")
    fig.suptitle("NARPS AO86 equal-indifference group: gain-effect maps", fontsize=14)
    fig.savefig(OUT / "group_effect_and_fwe.png", dpi=180)
    plt.close(fig)
    print(json.dumps({"qc": qc, "results": summary}, indent=2))


if __name__ == "__main__":
    main()
