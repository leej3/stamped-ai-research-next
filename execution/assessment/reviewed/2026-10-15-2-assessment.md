# Coordinator-reviewed STAMPED assessment

Exact scientific commit: `f711558b2e29c376410e0e622b2f2a992f77bb41`.
This is a factual/mapping revision of the [original independent assessment](../native/judgment/2026-10-15-assessment.md), not a second independent judge.
The originals are unchanged.

An unattended study-kind assumption follows the supplied NARPS task: a group-level scientific analysis.
No human confirmed that classification in the judge session.

**MUST:** 10 met / 3 partial / 4 unmet / 0 not-checked / 0 not-applicable (17 items).
**SHOULD:** 2 met / 0 partial / 5 unmet / 1 not-checked / 1 not-applicable (9 items).
**MAY:** 2 met / 2 partial / 1 unmet / 0 not-checked / 0 not-applicable (5 items).

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

- **must/006:** Committed results lack a run record tying them to an exact environment.
  The logged warning confirms use of the worker-local Pixi manifest.
- **must/010:** pixi.toml includes the analysis imports and Git/annex tooling.
  Exact version locking is a separate question from dependency inclusion.
- **must/011:** Pixi platforms and packages are declared, but obtaining Pixi is undocumented.
  The release log confirms the local manifest; no external-manifest dependency is established.
- **must/012:** pixi.toml lists package and platform requirements, but obtaining Pixi is undocumented.
  The log does not establish any required external manifest.
- **must/016:** The exact scientific commit and its tracked specification are currently retrievable from GitHub.
  This reflects later coordinator publication, not original worker credit.

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
| must/001 | S.1 | met | judgement | `input`, `results`, `pixi.toml` | All components sit under the common repository root; inputs, results and environment spec are nested there. |
| must/002 | S.1 | met | judgement | `input/data/sub-001_hypo1_cope.nii.gz`, `input/sources.json` | The supplied maps and metadata are reachable under input/; sources.json records their origins and checksums. |
| must/003 | S.1 | met | judgement | `pixi.toml` | Analysis software dependencies are declared in the root Pixi environment; no external software module is required. |
| must/004 | T.1,T.3,T.5 | met | probe:tree-clean | `git ls-files`, `git status --porcelain` | git tracks 10 text, code and configuration file(s), and `git status` is empty including submodules: the committed state is the whole state. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex+judgement | `.gitattributes`, `input/data/sub-001_hypo1_cope.nii.gz` | The committed attributes and annex pointers content-address the large maps; the probe's untracked config citation is not needed. |
| must/006 | T.1,T.3,T.5 | unmet | judgement | `results/logs/group_analysis_release.log#L1` | Committed results lack a run record tying them to an exact environment. The logged warning confirms use of the worker-local Pixi manifest. |
| must/007 | A.1 | unmet | probe:entry-point | `git ls-files`, `results/report.md` | No README or Makefile gives installation and usage instructions; the results report is the only usage note. |
| must/008 | A.1 | met | probe:entry-point+judgement | `results/report.md`, `results/code/group_analysis.py` | The report gives the runnable Pixi command and identifies the group-analysis script as its entry point. |
| must/009 | P.1 | met | probe:no-abs-paths | `probe:no-abs-paths` | No host-specific absolute paths in tracked text files. Plus 1 /tmp path(s), portable but writing outside the object. |
| must/010 | P.1 | met | judgement | `pixi.toml` | pixi.toml includes the analysis imports and Git/annex tooling. Exact version locking is a separate question from dependency inclusion. |
| must/011 | P.1 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `results/logs/group_analysis_release.log#L1` | Pixi platforms and packages are declared, but obtaining Pixi is undocumented. The release log confirms the local manifest; no external-manifest dependency is established. |
| must/012 | P.2 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `pixi.toml` | pixi.toml lists package and platform requirements, but obtaining Pixi is undocumented. The log does not establish any required external manifest. |
| must/013 | P.3 | met | probe:env-spec-tracked | `pixi.toml` | Tracked: pixi.toml. |
| must/014 | P.3 | unmet | judgement | `pixi.toml`, `results/report.md` | No lockfile or documented dependency-update and lock-regeneration process appears in the committed object. |
| must/015 | D.1 | unmet | probe:run-env-linked+judgement | `pixi.toml`, `git ls-files` | pixi.toml is not an exact environment snapshot: there is no committed lockfile or image digest. |
| must/016 | D.1 | met | judgement | `/Users/johnlee/.local/state/stamped-ai-research-next/pilots/narps-suitability-20261015-03/assessment/current-exact-fetch.json` | The exact scientific commit and its tracked specification are currently retrievable from GitHub. This reflects later coordinator publication, not original worker credit. |
| must/017 | D.1 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `results/report.md`, `pixi.toml` | The result report gives a Pixi execution command, but omits how to obtain Pixi and the exact environment cannot be rebuilt from a lock. |
| should/001 | T.2 | met | judgement | `git ls-files`, `input/data/sub-001_hypo1_cope.nii.gz` | Git tracks code, text, metadata and annex pointers; the same Git history contains the project components. |
| should/002 | A.2 | unmet | probe:ci-present | `probe:ci-present` | No CI configuration: nothing checks that the instructions still work. |
| should/003 | M.1 | met | probe:modules-separated | `input`, `results`, `pixi.toml` | 3 kinds of component live in distinct places: inputs in input; derived in results; environment in pixi.toml |
| should/004 | E.1 | not-checked | judgement | `/Users/johnlee/.local/state/stamped-ai-research-next/pilots/narps-suitability-20261015-03/assessment/native/judgment/2026-10-15-fresh-rerun.json` | A clean-environment execution was outside the authorized scope; committed logs do not establish a fresh clone or container run. |
| should/005 | E.1 | unmet | judgement | `results/report.md`, `pixi.toml` | The documented pixi run reuses the environment; no workflow creates a disposable environment for each execution. |
| should/006 | D.2 | unmet | probe:ci-present | `probe:ci-present` | No CI configuration: the environment behind the results is never rebuilt. |
| should/007 | D.2 | unmet | judgement | `git ls-files` | No environment image or package archive is stored with the object; only the mutable Pixi dependency declaration is tracked. |
| should/008 | D.2 | unmet | judgement | `pixi.toml`, `results/report.md` | No dependency-update process is documented or tracked; same duplicated requirement as must/014. |
| should/009 | M.4 | not-applicable | judgement | `input/sources.json` | N/A: the object references publicly retrievable data and public package repositories; no restricted component is identified. |
| may/001 | M.2 | unmet | probe:subdatasets-resolvable+judgement | `.gitmodules`, `input/data`, `pixi.toml` | External source maps are annexed files and software is declared in Pixi; neither is linked as a submodule. |
| may/002 | M.2 | partial | judgement | `results/report.md`, `input/` | The input, result and environment directories are apparent and cross-linked in the report, but no document explains module relationships or recombination. |
| may/003 | M.2 | partial | judgement | `results/code/group_analysis.py`, `input/sources.json` | Inputs, code and environment are separated, but the script assumes fixed paths and data structure, so independent replacement is constrained. |
| may/004 | M.2 | met | judgement | `results/report.md` | The report composes the Pixi environment, supplied inputs and analysis script in one documented command. |
| may/005 | M.2 | met | judgement | `results/report.md`, `input/ and results/` | The report links the analysis script, summary table and figures; top-level input/results directories support navigation. |

## Flagged items

- `stamped-checklist:must/005`: probe-overridden — The committed attributes and annex pointers content-address the large maps; the probe's untracked config citation is not needed.
- `stamped-checklist:must/006`: coordinator-reviewed, probe-overridden — Committed results lack a run record tying them to an exact environment.
  The logged warning confirms use of the worker-local Pixi manifest.
- `stamped-checklist:must/008`: probe-overridden — The report gives the runnable Pixi command and identifies the group-analysis script as its entry point.
- `stamped-checklist:must/010`: coordinator-reviewed, mapping-questioned, probe-overridden — pixi.toml includes the analysis imports and Git/annex tooling.
  Exact version locking is a separate question from dependency inclusion.
- `stamped-checklist:must/011`: coordinator-reviewed, probe-overridden — Pixi platforms and packages are declared, but obtaining Pixi is undocumented.
  The release log confirms the local manifest; no external-manifest dependency is established.
- `stamped-checklist:must/012`: coordinator-reviewed, probe-overridden — pixi.toml lists package and platform requirements, but obtaining Pixi is undocumented.
  The log does not establish any required external manifest.
- `stamped-checklist:must/014`: upstream-duplicate — No lockfile or documented dependency-update and lock-regeneration process appears in the committed object.
- `stamped-checklist:must/015`: probe-overridden — pixi.toml is not an exact environment snapshot: there is no committed lockfile or image digest.
- `stamped-checklist:must/016`: coordinator-reviewed, probe-overridden — The exact scientific commit and its tracked specification are currently retrievable from GitHub.
  This reflects later coordinator publication, not original worker credit.
- `stamped-checklist:should/008`: upstream-duplicate — No dependency-update process is documented or tracked; same duplicated requirement as must/014.
- `stamped-checklist:may/001`: probe-overridden — External source maps are annexed files and software is declared in Pixi; neither is linked as a submodule.

## Not checked

Fresh scientific replay remains **not-checked**.
A separately authorized fresh execution and output comparison would settle it; current retrieval alone does not.

## Scientific review, separate from STAMPED

The original scientific assessment is retained as a descriptive reading of code and reported artifacts, not independent numerical validation.
No scientific rerun was performed.
Different masks, vmPFC definitions and corrections across pilots mean their shared lack of corrected vmPFC support is not independent validation.

## Checklist and provenance

[Filled checklist URL](2026-10-15-2-url.txt) · [Canonical response](2026-10-15-2-response.json) · [Unchanged original probes](2026-10-15-2-probes.json).

Produced using assess-alignment-with-stamped-principles 0.1.0 and stamped-conventions 0.1.0, checklist 0.3.1 (schema af259ba), source d867c1d04bbb58b3b0f64122ebd5f76bd8e5a7ca and runtime 3552d5003a2485b6405805236d5c54e7ed42f097; object git@github.com:leej3/stamped-ai-research-next.git at f711558b2e29c376410e0e622b2f2a992f77bb41; 2026-10-15; Codex Desktop 26.1007.71326 / codex-cli 0.162.0-alpha.17.2 / gpt-6-astra (ultra).
