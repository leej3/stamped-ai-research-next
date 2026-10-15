#!/usr/bin/env python
"""Group analysis of supplied NARPS AO86 gain cope maps."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import nibabel as nib
import numpy as np
import pandas as pd
from nilearn import datasets, plotting, image
from scipy import stats
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "input"
OUT = ROOT / "results"
SEED = 20261015
N_PERM = 9999


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_maps():
    participants = pd.read_csv(INPUT / "participants.tsv", sep="\t")
    sources = json.loads((INPUT / "sources.json").read_text())
    if len(participants) != 54 or participants.participant_id.duplicated().any():
        raise ValueError("Expected 54 unique cohort rows")
    expected_ids = {v["participant_id"] for k, v in sources["files"].items()
                    if k.endswith("_cope.nii.gz")}
    if set(participants.participant_id) != expected_ids or len(expected_ids) != 54:
        raise ValueError("Participant metadata and source map IDs do not match exactly")
    paths = [INPUT / "data" / f"{pid}_hypo1_cope.nii.gz"
             for pid in participants.participant_id]
    images = [nib.load(str(path)) for path in paths]
    ref = images[0]
    shape, affine = ref.shape, ref.affine
    arrays = []
    file_qc = []
    for pid, path, img in zip(participants.participant_id, paths, images):
        if img.shape != shape or not np.allclose(img.affine, affine, atol=1e-5):
            raise ValueError(f"Spatial geometry mismatch for {pid}")
        x = img.get_fdata(dtype=np.float32)
        finite = np.isfinite(x)
        if not finite.all():
            raise ValueError(f"Nonfinite voxel values in {pid}")
        if not np.any(x != 0):
            raise ValueError(f"All-zero image for {pid}")
        actual_sha = sha256(path)
        expected_meta = sources["files"][f"data/{path.name}"]
        if path.stat().st_size != expected_meta["bytes"] or actual_sha != expected_meta["sha256"]:
            raise ValueError(f"Source checksum/size mismatch for {pid}")
        arrays.append(x)
        file_qc.append({"participant_id": pid, "sha256": actual_sha,
                        "shape": list(shape), "finite_voxels": int(finite.sum()),
                        "nonzero_voxels": int(np.count_nonzero(x)),
                        "mean_nonzero": float(x[x != 0].mean()),
                        "sd_nonzero": float(x[x != 0].std(ddof=1))})
    return participants, sources, paths, images, np.stack(arrays), file_qc


def save_json(obj, path: Path):
    path.write_text(json.dumps(obj, indent=2, sort_keys=True,
                               default=lambda value: value.item() if isinstance(value, np.generic) else value) + "\n")


def vmPFC_atlas_mask(reference):
    atlas_copy = OUT / "harvard_oxford_cort_maxprob_thr25_2mm.nii.gz"
    labels_copy = OUT / "harvard_oxford_cort_maxprob_thr25_2mm_labels.json"
    if atlas_copy.exists() and labels_copy.exists():
        atlas_img = nib.load(str(atlas_copy))
        labels = json.loads(labels_copy.read_text())
    else:
        atlas = datasets.fetch_atlas_harvard_oxford(
            "cort-maxprob-thr25-2mm", data_dir=str(OUT / "atlas-cache"))
        atlas_img = atlas.maps if hasattr(atlas.maps, "get_fdata") else nib.load(atlas.maps)
        labels = list(atlas.labels)
    wanted = {"Frontal Medial Cortex", "Subcallosal Cortex"}
    absent = wanted.difference(labels)
    if absent:
        raise ValueError(f"Atlas is missing predefined vmPFC labels: {sorted(absent)}")
    resampled = image.resample_to_img(atlas_img, reference, interpolation="nearest")
    atlas_values = resampled.get_fdata().astype(int)
    ids = [labels.index(label) for label in wanted]
    mask = np.isin(atlas_values, ids)
    OUT.mkdir(parents=True, exist_ok=True)
    if not atlas_copy.exists():
        nib.save(atlas_img, str(atlas_copy))
    if not labels_copy.exists():
        labels_copy.write_text(json.dumps(labels, indent=2) + "\n")
    return mask, sorted(wanted), labels, atlas_copy


def group_test(arrays, reference, n_perm=N_PERM, seed=SEED):
    # The shared nonzero support is the whole-brain family. The atlas does not
    # restrict this family and cannot affect the corrected p values.
    mask = np.isfinite(arrays).all(axis=0) & np.all(arrays != 0, axis=0)
    n = arrays.shape[0]
    y = arrays[:, mask].astype(np.float64, copy=False)
    if y.shape[1] < 1000:
        raise ValueError(f"Unexpectedly small common whole-brain mask: {y.shape[1]}")
    sum_y = y.sum(axis=0)
    sumsq = np.square(y).sum(axis=0)
    denom = np.sqrt(np.maximum(n * sumsq - sum_y * sum_y, 0.0))
    observed = sum_y * np.sqrt(n - 1) / denom
    observed[denom == 0] = 0.0
    rng = np.random.default_rng(seed)
    max_null = np.empty(n_perm, dtype=np.float64)
    # Sign flips are at the independent participant level. Batch matrix
    # multiplication bounds memory use while evaluating every in-mask voxel.
    batch_size = 32
    for start in range(0, n_perm, batch_size):
        stop = min(start + batch_size, n_perm)
        signs = rng.choice(np.array([-1.0, 1.0]), size=(stop - start, n))
        sums = signs @ y
        perm_denom = np.sqrt(np.maximum(n * sumsq[None, :] - sums * sums, 0.0))
        t_perm = sums * np.sqrt(n - 1) / perm_denom
        t_perm[perm_denom == 0] = 0.0
        max_null[start:stop] = t_perm.max(axis=1)
    fwe = (1 + (max_null[:, None] >= observed[None, :]).sum(axis=0)) / (n_perm + 1)
    mean = np.zeros(mask.shape, dtype=np.float32)
    tmap = np.zeros(mask.shape, dtype=np.float32)
    pmap = np.ones(mask.shape, dtype=np.float32)
    mean[mask] = y.mean(axis=0).astype(np.float32)
    tmap[mask] = observed.astype(np.float32)
    pmap[mask] = fwe.astype(np.float32)
    return mask, mean, tmap, pmap, max_null, observed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot", action="store_true", help="integrity/QC pilot only")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    participants, sources, paths, imgs, arrays, file_qc = read_maps()
    mask = np.isfinite(arrays).all(axis=0) & np.all(arrays != 0, axis=0)
    if args.pilot:
        roi_mask, roi_labels, _, atlas_path = vmPFC_atlas_mask(imgs[0])
        pilot = {"n_participants": len(participants), "participants": participants.participant_id.tolist(),
                 "shape": list(arrays.shape[1:]), "affine": imgs[0].affine.tolist(),
                 "common_nonzero_mask_voxels": int(mask.sum()),
                 "common_mask_volume_mm3": float(mask.sum() * abs(np.linalg.det(imgs[0].affine[:3, :3]))),
                 "vmPFC_atlas_labels": roi_labels, "vmPFC_atlas_intersection_voxels": int((roi_mask & mask).sum()),
                 "vmPFC_atlas_sha256": sha256(atlas_path),
                 "map_qc": file_qc}
        save_json(pilot, OUT / "pilot-qc.json")
        print(json.dumps({k: v for k, v in pilot.items() if k != "map_qc"}, indent=2))
        return

    roi_mask, roi_labels, atlas_labels, atlas_path = vmPFC_atlas_mask(imgs[0])
    template_path = OUT / "mni152_template_2mm.nii.gz"
    if not template_path.exists():
        nib.save(datasets.load_mni152_template(resolution=2), str(template_path))
    template_hash = sha256(template_path)
    mask, mean, tmap, pmap, max_null, observed = group_test(arrays, imgs[0])
    voxel_volume = abs(np.linalg.det(imgs[0].affine[:3, :3]))
    n = len(participants)
    roi = roi_mask & mask
    if not roi.any():
        raise ValueError("Predefined vmPFC ROI has no voxels in the group mask")
    roi_values = arrays[:, roi].mean(axis=1)
    roi_mean = float(roi_values.mean())
    roi_sem = float(stats.sem(roi_values))
    roi_ci = stats.t.interval(0.95, df=n - 1, loc=roi_mean, scale=roi_sem)
    # Participant bootstrap is a descriptive uncertainty check for the ROI mean.
    boot_rng = np.random.default_rng(SEED + 1)
    boot_idx = boot_rng.integers(0, n, size=(20000, n))
    boot_means = roi_values[boot_idx].mean(axis=1)
    boot_ci = np.quantile(boot_means, [0.025, 0.975]).tolist()
    brain_sig = (pmap <= 0.05) & mask & (tmap > 0)
    roi_sig = brain_sig & roi_mask
    affine = imgs[0].affine
    np.savetxt(OUT / "permutation-max-t.tsv", max_null, fmt="%.9g", header="maximum_positive_t")
    components, n_components = ndimage.label(brain_sig, structure=np.ones((3, 3, 3), dtype=np.uint8))
    clusters = []
    for component_id in range(1, n_components + 1):
        ijk = np.argwhere(components == component_id)
        peak_idx = tuple(ijk[np.argmax(tmap[components == component_id])])
        clusters.append({"voxels": int(len(ijk)), "volume_mm3": float(len(ijk) * voxel_volume),
                         "peak_mni_mm": [float(v) for v in nib.affines.apply_affine(affine, peak_idx)],
                         "peak_t": float(tmap[peak_idx]), "peak_fwe_p": float(pmap[peak_idx])})
    clusters.sort(key=lambda item: (-item["voxels"], -item["peak_t"]))
    def save_map(data, name):
        nib.save(nib.Nifti1Image(data, affine, imgs[0].header), str(OUT / name))
    save_map(mean, "group-mean.nii.gz")
    save_map(tmap, "group-t.nii.gz")
    save_map(pmap, "group-fwe-p-positive.nii.gz")
    save_map(mask.astype(np.uint8), "whole-brain-mask.nii.gz")
    save_map(roi_mask.astype(np.uint8), "vmPFC-atlas-mask.nii.gz")
    peak = None
    if brain_sig.any():
        coords = np.argwhere(brain_sig)
        peak_idx = tuple(coords[np.argmax(tmap[brain_sig])])
        peak = {"ijk": list(peak_idx), "mni_mm": nib.affines.apply_affine(affine, peak_idx).tolist(),
                "t": float(tmap[peak_idx]), "fwe_p": float(pmap[peak_idx]),
                "in_predefined_vmPFC": bool(roi_mask[peak_idx])}
    # ROI peak summary and whole-brain result are distinct outputs.
    roi_t = tmap[roi]
    roi_p = pmap[roi]
    roi_peak_flat = int(np.argmax(roi_t))
    roi_idx = tuple(np.argwhere(roi)[roi_peak_flat])
    summary = {
        "analysis": "one-sample positive t; participant sign-flips; max-t whole-brain FWE",
        "n_participants": n, "n_excluded": 0, "permutations": N_PERM, "seed": SEED,
        "alpha": 0.05, "one_sided": True,
        "shape": list(mask.shape), "voxel_volume_mm3": voxel_volume,
        "whole_brain_mask_voxels": int(mask.sum()), "whole_brain_mask_volume_mm3": float(mask.sum() * voxel_volume),
        "vmPFC_definition": "Harvard-Oxford cortical max-probability atlas threshold 25%; union of Frontal Medial Cortex and Subcallosal Cortex",
        "vmPFC_atlas_labels": roi_labels, "vmPFC_atlas_sha256": sha256(atlas_path),
        "display_template": "Nilearn MNI152 2-mm template; used for visualization only",
        "display_template_sha256": template_hash,
        "vmPFC_intersection_voxels": int(roi.sum()),
        "vmPFC_mean_across_voxels": roi_mean,
        "vmPFC_mean_t_CI95": [float(v) for v in roi_ci],
        "vmPFC_participant_bootstrap_CI95": [float(v) for v in boot_ci],
        "vmPFC_participant_values": [{"participant_id": pid, "mean_cope": float(v)}
                                     for pid, v in zip(participants.participant_id, roi_values)],
        "vmPFC_peak": {"ijk": list(roi_idx), "mni_mm": nib.affines.apply_affine(affine, roi_idx).tolist(),
                       "t": float(tmap[roi_idx]), "fwe_p": float(pmap[roi_idx])},
        "n_whole_brain_fwe_voxels": int(brain_sig.sum()),
        "positive_fwe_clusters_26_neighbor_descriptive": clusters,
        "n_vmPFC_fwe_voxels": int(roi_sig.sum()), "global_positive_peak": peak,
        "max_null_t_95pct": float(np.quantile(max_null, .95)),
        "max_null_t_99pct": float(np.quantile(max_null, .99)),
        "map_qc": file_qc,
        "notes": ["Effect estimates are not currency-unit slopes or standardized test statistics.",
                  "No participant-level variance maps are supplied; equal-weight cope model used.",
                  "Common nonzero support defines the whole-brain family."]
    }
    save_json(summary, OUT / "results.json")
    pd.DataFrame({"participant_id": participants.participant_id, "mean_vmPFC_cope": roi_values}).to_csv(
        OUT / "vmPFC-participant-values.tsv", sep="\t", index=False)

    # Separate the corrected whole-brain discovery map from the uncorrected
    # vmPFC localization view; never imply that the latter is confirmatory.
    sig_img = nib.Nifti1Image(np.where(brain_sig, tmap, 0).astype(np.float32), affine, imgs[0].header)
    display = plotting.plot_stat_map(sig_img, bg_img=str(template_path), display_mode="z",
                                     cut_coords=[-20, -10, 0, 10, 20],
                                     title="Positive whole-brain findings\n(max-T FWE p ≤ .05)",
                                     threshold=0.01, cmap="cold_hot", colorbar=True,
                                     output_file=str(OUT / "whole-brain-fwe-slices.png"))
    display.close()
    vm_t = np.where(roi_mask & mask, tmap, 0).astype(np.float32)
    vm_title = ("Predefined vmPFC ROI: uncorrected t statistics (both signs)\n"
                f"No vmPFC voxel survived whole-brain FWE; peak FWE p={float(roi_p.min()):.3f}")
    display = plotting.plot_stat_map(nib.Nifti1Image(vm_t, affine, imgs[0].header), bg_img=str(template_path),
                                     display_mode="z", cut_coords=[-20, -10, 0, 10, 20],
                                     title=vm_title, threshold=0.01, cmap="cold_hot", colorbar=True,
                                     output_file=str(OUT / "vmPFC-unthresholded-slices.png"))
    display.close()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7.2, 4.2), constrained_layout=True)
    jitter = np.random.default_rng(SEED).normal(0, 0.045, size=n)
    ax.scatter(jitter, roi_values, s=26, alpha=.72, color="#345995", edgecolor="white", linewidth=.4)
    ax.axhline(0, color="#555555", linewidth=1, linestyle="--")
    ax.errorbar([0], [roi_mean], yerr=[[roi_mean - roi_ci[0]], [roi_ci[1] - roi_mean]],
                fmt="D", color="#c0392b", markersize=7, capsize=5, label="Mean and t-based 95% CI")
    ax.set(xlim=(-.35, .35), xticks=[], ylabel="Mean participant cope in vmPFC atlas ROI",
           title="Participant variation in predefined vmPFC ROI")
    ax.legend(frameon=False, loc="best")
    fig.savefig(OUT / "vmPFC-participant-distribution.png", dpi=180)
    plt.close(fig)
    print(json.dumps({k: v for k, v in summary.items() if k not in {"map_qc", "vmPFC_participant_values"}},
                     indent=2, default=lambda value: value.item() if isinstance(value, np.generic) else value))


if __name__ == "__main__":
    main()
