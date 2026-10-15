# Coordinator-reviewed STAMPED assessment

Exact scientific commit: `466d43f39dc3d40ac64038ff03066b483b6d9457`.
This is a factual/mapping revision of the [original independent assessment](../native/judgment/2026-10-15-assessment.md), not a second independent judge.
The originals are unchanged.

An unattended study-kind assumption follows the supplied NARPS task: a group-level scientific analysis.
No human confirmed that classification in the judge session.

**MUST:** 10 met / 2 partial / 5 unmet / 0 not-checked / 0 not-applicable (17 items).
**SHOULD:** 2 met / 0 partial / 5 unmet / 1 not-checked / 1 not-applicable (9 items).
**MAY:** 4 met / 0 partial / 1 unmet / 0 not-checked / 0 not-applicable (5 items).

Partial does not satisfy a MUST.
There is no overall score.

## What to improve first

1. Preserve a re-executable record linking inputs, code, outputs and the exact used environment (must/006, must/015).
2. Document how to install and invoke Pixi, with an entry point a new reader can follow (must/007, must/017; host requirements where incomplete).
3. Document and exercise environment updates and fresh execution checks (must/014, should/002, should/004, should/006, should/008).

## Strengths

All 54 supplied maps and their metadata are retained; the analysis and report use the declared scientific libraries.
The report gives a runnable analysis command, figures, uncertainty and limits.

## Corrections and scope

- **must/011:** Platforms and packages are declared, but obtaining the Pixi host tool is undocumented.
  The Nilearn MNI display template is bundled, not a network/cache requirement.
- **must/012:** pixi.toml lists packages and platform requirements, but the required Pixi host installation route is missing; no separate MNI template download is needed.

All three original judges were native `gpt-6-luna` sessions with high effort and runtime `codex-cli 0.162.0-alpha.17.2`, verified from launch and native session metadata.
Original claims of unavailable or generic model identity are corrected here without editing the original reports.
This reviewed revision is by the coordinator, `gpt-6-astra` / ultra.

Current exact-SHA fetch succeeds, documented in [the receipt](../current-exact-fetch.json).
The original run03 HTTP422 observation remains in its native evidence; publication happened while judges were running.
Availability now is coordinator-added and earns no original-worker credit.
The original science commit excludes all later capture packaging, atlas retention, assessments and environment snapshots.

[Review ledger](review-ledger.json) records every changed answer.
The original frozen probes are copied byte-for-byte; they were not rerun.

## Per-item checklist

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `input/sources.json`, `results/analysis.py` | All required inputs, code, environment spec, and results are under the checkout root. |
| must/002 | S.1 | met | judgement | `input/data`, `input/sources.json` | All 54 maps and metadata are present under input; external source URLs are provenance only. |
| must/003 | S.1 | met | judgement | `pixi.toml`, `results/analysis.py` | Analysis libraries and git-annex are declared in the tracked Pixi environment. |
| must/004 | T.1,T.3,T.5 | met | probe:tree-clean | `git status --porcelain` | Git tracks code, text, docs and configuration; the assessed commit is clean. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex | `git annex checkpresentkey`, `probe:large-in-annex` | All 54 input maps are annexed; read-only checks found each present on con-hub. |
| must/006 | T.1,T.3,T.5 | unmet | probe:derived-have-records+judgement | `results/run.log`, `pixi.toml` | run.log records execution, but no run record links results to a complete exact environment specification. |
| must/007 | A.1 | unmet | probe:entry-point | `results/report.md#Reproducibility` | report.md gives a command, but no README or Makefile includes installation and usage instructions. |
| must/008 | A.1 | met | probe:entry-point+judgement | `results/report.md#Reproducibility`, `results/analysis.py` | The report directs readers to run results/analysis.py from the project root. |
| must/009 | P.1 | met | probe:no-abs-paths | `results/analysis.py` | The analysis resolves input and output paths relative to its own project root. |
| must/010 | P.1 | met | probe:env-spec-tracked+judgement | `pixi.toml`, `results/analysis.py` | pixi.toml declares the Python and scientific dependencies imported by the analysis. |
| must/011 | P.1 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `pixi.toml` | Platforms and packages are declared, but obtaining the Pixi host tool is undocumented. The Nilearn MNI display template is bundled, not a network/cache requirement. |
| must/012 | P.2 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `results/report.md` | pixi.toml lists packages and platform requirements, but the required Pixi host installation route is missing; no separate MNI template download is needed. |
| must/013 | P.3 | met | probe:env-spec-tracked | `pixi.toml` | The environment specification is tracked at the assessed commit. |
| must/014 | P.3 | unmet | judgement | `pixi.toml`, `git log -- pixi.toml` | No dependency-update or lockfile regeneration process is declared or recorded. |
| must/015 | D.1 | unmet | probe:run-env-linked+judgement | `pixi.toml`, `results/run.log` | The environment is not frozen: dependency ranges are mutable and no lockfile or digest identifies the run environment. |
| must/016 | D.1 | met | judgement | `https://api.github.com/repos/leej3/stamped-ai-research-next/commits/466d43f39dc3d40ac64038ff03066b483b6d9457`, `git annex checkpresentkey` | The target commit is currently retrievable from GitHub and its annexed inputs are present on con-hub; this does not establish who published it. |
| must/017 | D.1 | unmet | judgement | `results/report.md#Reproducibility`, `pixi.toml` | The report gives a Pixi run command but does not explain how to obtain or install Pixi. |
| should/001 | T.2 | met | judgement | `git ls-tree -r HEAD input/data`, `pixi.toml` | Git versions the repository and git-annex stores large input content within the same Git-based object. |
| should/002 | A.2 | unmet | probe:ci-present | `probe:ci-present` | No CI or other recurring workflow checks that the documented procedure still works. |
| should/003 | M.1 | met | probe:modules-separated | `input`, `results`, `pixi.toml` | Inputs, derived results, and environment specification occupy separate directories or files. |
| should/004 | E.1 | not-checked | judgement | `results/run.log` | Replay was outside scope; run.log does not establish a fresh container, VM, batch job, or cloud test. A recorded test in one of these would settle it. |
| should/005 | E.1 | unmet | judgement | `results/report.md#Reproducibility`, `results/analysis.py` | The documented Pixi command reuses an environment; no workflow creates a disposable environment per run. |
| should/006 | D.2 | unmet | probe:ci-present | `probe:ci-present`, `pixi.toml` | No recurring check rebuilds the environment behind these results. |
| should/007 | D.2 | unmet | judgement | `pixi.toml`, `git ls-tree -r HEAD` | The object archives a package specification, not executable environment artifacts or a container image. |
| should/008 | D.2 | unmet | judgement | `pixi.toml`, `git log -- pixi.toml` | No dependency-update process or tracked update instance is present; this repeats must/014 by checklist design. |
| should/009 | M.4 | not-applicable | judgement | `input/sources.json` | N/A: supplied inputs and software are public; no restricted component exists to isolate. |
| may/001 | M.2 | unmet | judgement | `input/data`, `git submodule status` | External source maps are copied into annexed input files, not included or linked as submodules. |
| may/002 | M.2 | met | judgement | `results/report.md` | The report identifies the analysis, fixed inputs, results, quality checks, and reproduction command. |
| may/003 | M.2 | met | judgement | `results/analysis.py`, `pixi.toml` | Inputs, analysis, outputs, and environment are separate; the script connects them through root-relative paths. |
| may/004 | M.2 | met | judgement | `results/analysis.py`, `results/report.md#Reproducibility` | One analysis script composes the included inputs and environment into the results. |
| may/005 | M.2 | met | judgement | `results/report.md` | The report and directory names provide a usable route through the code, inputs, checks, and figures. |

## Flagged items

- `stamped-checklist:must/006`: mapping-questioned — run.log records execution, but no run record links results to a complete exact environment specification.
- `stamped-checklist:must/008`: probe-overridden — The report directs readers to run results/analysis.py from the project root.
- `stamped-checklist:must/010`: probe-overridden — pixi.toml declares the Python and scientific dependencies imported by the analysis.
- `stamped-checklist:must/011`: coordinator-reviewed, probe-overridden — Platforms and packages are declared, but obtaining the Pixi host tool is undocumented.
  The Nilearn MNI display template is bundled, not a network/cache requirement.
- `stamped-checklist:must/012`: coordinator-reviewed, probe-overridden — pixi.toml lists packages and platform requirements, but the required Pixi host installation route is missing; no separate MNI template download is needed.
- `stamped-checklist:must/014`: upstream-duplicate — No dependency-update or lockfile regeneration process is declared or recorded.
- `stamped-checklist:must/015`: probe-overridden — The environment is not frozen: dependency ranges are mutable and no lockfile or digest identifies the run environment.
- `stamped-checklist:should/008`: upstream-duplicate — No dependency-update process or tracked update instance is present; this repeats must/014 by checklist design.

## Not checked

Fresh scientific replay remains **not-checked**.
A separately authorized fresh execution and output comparison would settle it; current retrieval alone does not.

## Scientific review, separate from STAMPED

Separate scientific review: the >=90% coverage mask retains voxels with up to five zero-valued observations.
Code then uses every subject in X.mean/std with n=54 while reporting zeros as absent coverage.
This mismatch may affect effects, standard errors and permutation inference; the independent judge missed it.
No numerical result was repaired or rerun.
The original broad scientific endorsement must be read with this caveat.

## Checklist and provenance

[Filled checklist URL](2026-10-15-2-url.txt) · [Canonical response](2026-10-15-2-response.json) · [Unchanged original probes](2026-10-15-2-probes.json).

Produced using assess-alignment-with-stamped-principles 0.1.0 and stamped-conventions 0.1.0, checklist 0.3.1 (schema af259ba), source d867c1d04bbb58b3b0f64122ebd5f76bd8e5a7ca and runtime 3552d5003a2485b6405805236d5c54e7ed42f097; object git@github.com:leej3/stamped-ai-research-next.git at 466d43f39dc3d40ac64038ff03066b483b6d9457; 2026-10-15; Codex Desktop 26.1007.71326 / codex-cli 0.162.0-alpha.17.2 / gpt-6-astra (ultra).
