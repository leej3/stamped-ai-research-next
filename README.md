# NARPS Hypothesis 1 group analysis

This repository analyzes the supplied 54 AO86 participant gain-effect maps for the NARPS equal-indifference group. It does not rerun preprocessing or participant-level models and does not download time-series scans.

Read the [scientific report](results/report.md) and [analysis protocol](analysis-protocol.md). The report includes the whole-brain corrected result, vmPFC interpretation, figures and limitations.

From the repository root, use the root Pixi environment:

```sh
pixi run analysis
pixi run validate
```

The first command generates statistical maps, the max-statistic permutation null, summary tables and figures under `results/`. The second checks peak statistics and corrected p values independently with SciPy. Recorded duct command metadata, standard output, errors, resource samples and summaries are retained under `logs/`, including failed attempts.

The source data, hashes, cohort and fixed upstream-model description are in `input/`. The analysis code is in `scripts/`. `pixi.toml` and `pixi.lock` specify the environment.
