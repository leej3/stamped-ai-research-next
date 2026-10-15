"""Check group-analysis cost and deterministic replay, outside worker inputs."""
import argparse
import hashlib
import json
import platform
import resource
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import nibabel as nib
import nilearn
import numpy as np
import pandas as pd
import psutil
import scipy
from nilearn.glm import threshold_stats_img
from nilearn.glm.second_level import SecondLevelModel
from nilearn.masking import compute_multi_background_mask
from nilearn.plotting import plot_glass_brain
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("coordinator-guidance/rehearsal"))
    parser.add_argument("--compare", type=Path)
    args = parser.parse_args()
    started = time.monotonic()
    output = ROOT / args.output
    output.mkdir(parents=True, exist_ok=True)
    source = ROOT / "input/sources.json"
    manifest = json.loads(source.read_text())
    maps = [ROOT / "input" / name for name in manifest["files"] if name.endswith(".nii.gz")]
    assert len(maps) == 54
    for path in maps:
        with path.open("rb") as stream:
            expected = manifest["files"][str(path.relative_to(ROOT / "input"))]["sha256"]
            assert hashlib.file_digest(stream, "sha256").hexdigest() == expected
    stages = {"verify_input": time.monotonic() - started}
    tick = time.monotonic()
    with threadpool_limits(limits=2):
        mask = compute_multi_background_mask(maps, threshold=1.0, n_jobs=1)
        voxels = int(np.count_nonzero(mask.get_fdata()))
        assert voxels > 10000, f"Unexpectedly small mask: {voxels}"
        stages["mask"] = time.monotonic() - tick
        tick = time.monotonic()
        design = pd.DataFrame({"intercept": np.ones(len(maps))})
        model = SecondLevelModel(mask_img=mask, n_jobs=1).fit(maps, design_matrix=design)
        results = model.compute_contrast(second_level_contrast="intercept", output_type="all")
        corrected, threshold = threshold_stats_img(results["z_score"], mask_img=mask,
                                                    alpha=0.05, height_control="bonferroni",
                                                    two_sided=False)
        stages["group_model_and_correction"] = time.monotonic() - tick
    tick = time.monotonic()
    images = {"mask.nii.gz": mask, "group-effect.nii.gz": results["effect_size"],
              "group-z.nii.gz": results["z_score"], "group-corrected-z.nii.gz": corrected}
    for name, image in images.items():
        assert np.isfinite(image.get_fdata()).all()
        path = output / name
        if path.exists():
            prior_image = nib.load(path)
            assert np.array_equal(image.get_fdata(), prior_image.get_fdata()), f"Choose a new output directory: {path} differs"
            assert np.array_equal(image.affine, prior_image.affine)
        else:
            nib.save(image, path)
    plot = plot_glass_brain(results["z_score"], threshold=None, plot_abs=False,
                           colorbar=True, title="Group-analysis readiness rehearsal")
    with tempfile.TemporaryDirectory(prefix="narps-figure-") as temporary:
        temporary_figure = Path(temporary) / "group-map.png"
        plot.savefig(temporary_figure)
        figure_bytes = temporary_figure.read_bytes()
    figure = output / "group-map.png"
    if figure.exists():
        assert figure.read_bytes() == figure_bytes, "Choose a new output directory for a changed figure"
    else:
        figure.write_bytes(figure_bytes)
    plot.close()
    stages["save_and_plot"] = time.monotonic() - tick
    agreement = None
    if args.compare:
        previous = ROOT / args.compare
        prior = json.loads((previous / "report.json").read_text())
        assert prior["input_manifest_sha256"] == hashlib.sha256(source.read_bytes()).hexdigest()
        agreement = {}
        for name, image in images.items():
            a, b = image.get_fdata(), nib.load(previous / name).get_fdata()
            agreement[name] = {"exact_array_match": bool(np.array_equal(a, b)),
                               "max_absolute_difference": float(np.max(np.abs(a - b)))}
        assert all(x["exact_array_match"] for x in agreement.values()), agreement
    usage = resource.getrusage(resource.RUSAGE_SELF)
    elapsed = time.monotonic() - started
    report = {
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "command": ["pixi", "run", "rehearse", *sys.argv[1:]],
        "scope": "Computational readiness and repeated numerical execution only; no independent worker or judge trial and no anatomical decision about Hypothesis 1.",
        "input_manifest_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "upstream_processing_fixed": True, "participant_maps": len(maps),
        "method": "Intercept-only OLS on participant effects, intersection background mask, one-sided voxelwise Bonferroni correction at alpha 0.05.",
        "method_role": "Rehearsal only; workers choose their own defensible methods.",
        "mask_voxels": voxels, "corrected_z_threshold": float(threshold),
        "elapsed_seconds": elapsed, "stages_seconds": stages,
        "peak_rss_bytes": usage.ru_maxrss * (1 if sys.platform == "darwin" else 1024),
        "cpu_user_seconds": usage.ru_utime, "cpu_system_seconds": usage.ru_stime,
        "blas_threads": 2, "workers": 1,
        "host": {"system": platform.system(), "machine": platform.machine(),
                 "physical_cores": psutil.cpu_count(logical=False)},
        "versions": {"python": platform.python_version(), "nilearn": nilearn.__version__,
                     "nibabel": nib.__version__, "numpy": np.__version__,
                     "scipy": scipy.__version__, "pandas": pd.__version__,
                     "matplotlib": matplotlib.__version__},
        "replay_agreement": agreement,
    }
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"54-participant rehearsal: {elapsed:.1f}s, peak RSS {report['peak_rss_bytes'] / 1e6:.0f} MB; replay={agreement is not None}.")


if __name__ == "__main__":
    main()
