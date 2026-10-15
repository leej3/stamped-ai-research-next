# NARPS Hypothesis 1 group analysis

This repository analyzes the supplied 54 AO86 participant gain-effect maps for the NARPS equal-indifference group. It does not rerun preprocessing or participant-level models and does not download time-series scans.

Read the [scientific report](results/report.md) and [analysis protocol](analysis-protocol.md). The report includes the whole-brain corrected result, vmPFC interpretation, figures and limitations.

## Prerequisites and setup

Install Git to clone the repository and install [Pixi](https://pixi.prefix.dev/latest/installation/). This project was run with Pixi 0.81.0. From the repository root, restore the declared environment and lock:

```sh
pixi install --locked
```

The supplied worktree contains the annexed maps. In a clone, retrieve them with `pixi run git annex get input/data` from an accessible annex remote before running the analysis. The environment provides git-annex and the scientific software. The declared Pixi platforms are macOS ARM64 (macOS 14+) and Linux x86-64.

## Run and validate

```sh
pixi run recorded-analysis
pixi run validate
```

`recorded-analysis` runs the group analysis through duct, then writes a run record linking the code revision, `pixi.toml`, `pixi.lock`, input hashes, output hashes and duct summary. Statistical maps, the max-statistic null, summary tables and figures are written under `results/`; command metadata, stdout/stderr, resource samples, summaries and run records are retained under `logs/`. `pixi run validate` independently checks peak statistics and corrected p values with SciPy.

## Update the environment

Add or remove dependencies with `pixi add <package>` or `pixi remove <package>` (see the [Pixi dependency commands](https://pixi.prefix.dev/latest/reference/cli/pixi/add/)). Review and commit `pixi.toml` and `pixi.lock` together. Restore the committed environment with `pixi install --locked` before running analyses.

The source data, hashes, cohort and fixed upstream-model description are in `input/`. The analysis code is in `scripts/`. `pixi.toml` and `pixi.lock` specify the environment.
