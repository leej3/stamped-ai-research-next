# Coordinator-reviewed STAMPED assessment

Exact scientific commit: `510a685426804385a8c80f6347002ee47ce606e9`.
This is a factual/mapping revision of the [original independent assessment](../native/judgment/2026-10-15-assessment.md), not a second independent judge.
The originals are unchanged.

An unattended study-kind assumption follows the supplied NARPS task: a group-level scientific analysis.
No human confirmed that classification in the judge session.

**MUST:** 10 met / 4 partial / 3 unmet / 0 not-checked / 0 not-applicable (17 items).
**SHOULD:** 2 met / 0 partial / 5 unmet / 1 not-checked / 1 not-applicable (9 items).
**MAY:** 3 met / 1 partial / 1 unmet / 0 not-checked / 0 not-applicable (5 items).

Partial does not satisfy a MUST.
There is no overall score.

## What to improve first

1. Retain the exact Harvard–Oxford atlas and labels under the study boundary; the scientific snapshot depends on an external cache (must/001–002).
2. Preserve a re-executable record linking inputs, code, outputs and the exact used environment (must/006, must/015).
3. Document how to install and invoke Pixi, with an entry point a new reader can follow (must/007, must/017; host requirements where incomplete).
4. Document and exercise environment updates and fresh execution checks (must/014, should/002, should/004, should/006, should/008).

## Strengths

All 54 supplied maps and their metadata are retained; the analysis and report use the declared scientific libraries.
The report gives a runnable analysis command, figures, uncertainty and limits.

## Corrections and scope

- **must/001:** Inputs, code and results are rooted here, but the Harvard–Oxford atlas needed for the ROI lives only in an external Nilearn cache.
- **must/002:** The 54 participant maps are under input/, but the task-used Harvard–Oxford atlas and labels are absent from the scientific snapshot.
- **must/010:** pixi.toml includes the analysis imports and Git/annex tooling.
  Exact version locking is a separate question from dependency inclusion.
- **must/011:** Pixi declares supported platforms; the report identifies Pixi execution and the downloaded Harvard–Oxford atlas.
  The MNI display template is bundled with Nilearn.

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
| must/001 | S.1 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `scripts/group_analysis.py` | Inputs, code and results are rooted here, but the Harvard–Oxford atlas needed for the ROI lives only in an external Nilearn cache. |
| must/002 | S.1 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `scripts/group_analysis.py` | The 54 participant maps are under input/, but the task-used Harvard–Oxford atlas and labels are absent from the scientific snapshot. |
| must/003 | S.1 | met | judgement | `pixi.toml#L5-L27`, `scripts/group_analysis.py#L5-L10` | Python packages imported by the group script are declared in the tracked Pixi environment. |
| must/004 | T.1,T.3,T.5 | met | probe:tree-clean | `git ls-files`, `git status --porcelain` | Git tracks code, text and configuration; the requested commit has a clean working tree. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex | `git ls-tree -r -l HEAD`, `.datalad/config` | Git-annex carries the binary content; the probe found 55 annex pointers and no oversized Git binary. |
| must/006 | T.1,T.3,T.5 | unmet | probe:derived-have-records | `results/figures/roi_participants.png`, `results/figures/whole_brain_fwe.png`, `results/figures/whole_brain_t.png`, `results/logs/failed_attempts.md`, `results/logs/group_analysis.log`, `results/map_quality.tsv`, `results/maps/group_mean_gain_effect.nii.gz`, `results/maps/group_p_fwe_bonferroni.nii.gz`, `results/maps/group_p_positive.nii.gz`, `results/maps/group_t_fwe05.nii.gz` | Derived results have no run record or tracked workflow linking them to the exact environment used. |
| must/007 | A.1 | unmet | probe:entry-point | `git ls-tree` | The commit has no README with install/use instructions or Makefile; the report is not either required entry document. |
| must/008 | A.1 | met | probe:entry-point+judgement | `results/report.md#Reproducibility`, `scripts/group_analysis.py#L1-L16` | The report gives a runnable Pixi command for scripts/group_analysis.py, a clear analysis starting point. |
| must/009 | P.1 | met | probe:no-abs-paths | `probe:no-abs-paths` | The probe found no host-specific absolute paths in tracked text files. |
| must/010 | P.1 | met | judgement | `pixi.toml` | pixi.toml includes the analysis imports and Git/annex tooling. Exact version locking is a separate question from dependency inclusion. |
| must/011 | P.1 | met | judgement | `results/report.md` | Pixi declares supported platforms; the report identifies Pixi execution and the downloaded Harvard–Oxford atlas. The MNI display template is bundled with Nilearn. |
| must/012 | P.2 | met | judgement | `pixi.toml#L1-L27`, `probe:platform-assumptions` | The Pixi specification lists platform targets and the analysis package dependencies needed by the script. |
| must/013 | P.3 | met | probe:env-spec-tracked | `pixi.toml` | pixi.toml is committed alongside the analysis script and supplied data. |
| must/014 | P.3 | unmet | judgement | `pixi.toml`, `.gitignore` | No dependency update or lock regeneration process is documented; pixi.lock is ignored and absent. |
| must/015 | D.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:run-env-linked+judgement | `pixi.toml#L7-L27`, `.gitignore` | A Pixi dependency spec exists, but absent lock pins prevent exact environment reconstruction; no run record identifies the used environment. |
| must/016 | D.1 | met | probe:env-spec-tracked+judgement | `/Users/johnlee/.local/state/stamped-ai-research-next/pilots/narps-suitability-20261015-01/assessment/native/judgment/2026-10-15-remote-check.json` | The current GitHub remote retrieves the assessed commit and its tracked environment spec; this shows current access, not worker-era publication. |
| must/017 | D.1 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `results/report.md#Reproducibility`, `pixi.toml` | The report gives the Pixi run command and package versions, but does not explain how to install Pixi or obtain a pinned environment. |
| should/001 | T.2 | met | probe:tree-clean+probe:large-in-annex+judgement | `.datalad/config`, `probe:tree-clean` | Code, metadata and annexed binary inputs share Git versioning; git-annex stores large content. |
| should/002 | A.2 | unmet | probe:ci-present+judgement | `probe:ci-present`, `results/logs/group_analysis.log` | No CI or test workflow is tracked; a single analysis log does not show regular testing of the instructions. |
| should/003 | M.1 | met | probe:modules-separated | `input`, `scripts`, `results`, `pixi.toml` | Inputs, analysis code, results and environment are separated into distinct directories/files. |
| should/004 | E.1 | not-checked | judgement | `/Users/johnlee/.local/state/stamped-ai-research-next/pilots/narps-suitability-20261015-01/assessment/native/judgment/2026-10-15-replay-record.json` | Fresh-environment replay was outside scope; a permitted replay would establish whether the pipeline works in a clean environment. |
| should/005 | E.1 | unmet | judgement | `results/report.md#Reproducibility`, `git ls-tree` | The documented Pixi command reuses a project environment; no per-run container, batch job or clean-VM workflow is defined. |
| should/006 | D.2 | unmet | probe:ci-present+judgement | `pixi.toml`, `.gitignore`, `probe:ci-present` | No locked environment or recurring reconstitution check is present; CI absence alone is not decisive, but no alternative test is recorded. |
| should/007 | D.2 | unmet | judgement | `pixi.toml`, `git ls-tree` | Only a dependency declaration is archived; no lock snapshot, container image or packaged environment is present. |
| should/008 | D.2 | unmet | judgement | `pixi.toml`, `.gitignore` | No dependency update/regeneration process is documented or tracked. |
| should/009 | M.4 | not-applicable | judgement | `/Users/johnlee/.local/state/stamped-ai-research-next/pilots/narps-suitability-20261015-01/assessment/native/judgment/2026-10-15-remote-check.json`, `input/sources.json` | N/A: supplied maps are publicly retrievable and the object identifies no access-restricted data or software. |
| may/001 | M.2 | unmet | probe:subdatasets-resolvable+judgement | `input/sources.json`, `probe:subdatasets-resolvable` | External source maps and software are not linked as submodules; maps are included in the root and packages use Pixi. |
| may/002 | M.2 | met | judgement | `results/report.md#Reproducibility` | The report explains the input/code/result relationship and links the key files and output groups. |
| may/003 | M.2 | partial | judgement | `probe:modules-separated`, `scripts/group_analysis.py#L12-L21` | Folders separate components, but no independently pinned module interfaces protect updates; the script couples manifest, paths and output layout. |
| may/004 | M.2 | met | judgement | `results/report.md#Reproducibility`, `scripts/group_analysis.py#L12-L21` | The documented Pixi command composes the environment, input maps and group script into results. |
| may/005 | M.2 | met | judgement | `results/report.md#Reproducibility` | The report provides relative links to provenance, methods, script and key result files for navigation. |

## Flagged items

- `stamped-checklist:must/001`: coordinator-reviewed, probe-overridden — Inputs, code and results are rooted here, but the Harvard–Oxford atlas needed for the ROI lives only in an external Nilearn cache.
- `stamped-checklist:must/002`: coordinator-reviewed, probe-overridden — The 54 participant maps are under input/, but the task-used Harvard–Oxford atlas and labels are absent from the scientific snapshot.
- `stamped-checklist:must/008`: probe-overridden — The report gives a runnable Pixi command for scripts/group_analysis.py, a clear analysis starting point.
- `stamped-checklist:must/010`: coordinator-reviewed, mapping-questioned, probe-overridden — pixi.toml includes the analysis imports and Git/annex tooling.
  Exact version locking is a separate question from dependency inclusion.
- `stamped-checklist:must/011`: coordinator-reviewed, probe-overridden — Pixi declares supported platforms; the report identifies Pixi execution and the downloaded Harvard–Oxford atlas.
  The MNI display template is bundled with Nilearn.
- `stamped-checklist:must/014`: upstream-duplicate — No dependency update or lock regeneration process is documented; pixi.lock is ignored and absent.
- `stamped-checklist:must/015`: mapping-questioned, probe-overridden — A Pixi dependency spec exists, but absent lock pins prevent exact environment reconstruction; no run record identifies the used environment.
- `stamped-checklist:should/002`: mapping-questioned — No CI or test workflow is tracked; a single analysis log does not show regular testing of the instructions.
- `stamped-checklist:should/006`: mapping-questioned — No locked environment or recurring reconstitution check is present; CI absence alone is not decisive, but no alternative test is recorded.
- `stamped-checklist:should/008`: upstream-duplicate — No dependency update/regeneration process is documented or tracked.

## Not checked

Fresh scientific replay remains **not-checked**.
A separately authorized fresh execution and output comparison would settle it; current retrieval alone does not.

## Scientific review, separate from STAMPED

The original scientific assessment is retained as a descriptive reading of code and reported artifacts, not independent numerical validation.
No scientific rerun was performed.
Different masks, vmPFC definitions and corrections across pilots mean their shared lack of corrected vmPFC support is not independent validation.

## Checklist and provenance

[Filled checklist URL](2026-10-15-2-url.txt) · [Canonical response](2026-10-15-2-response.json) · [Unchanged original probes](2026-10-15-2-probes.json).

Produced using assess-alignment-with-stamped-principles 0.1.0 and stamped-conventions 0.1.0, checklist 0.3.1 (schema af259ba), source d867c1d04bbb58b3b0f64122ebd5f76bd8e5a7ca and runtime 3552d5003a2485b6405805236d5c54e7ed42f097; object git@github.com:leej3/stamped-ai-research-next.git at 510a685426804385a8c80f6347002ee47ce606e9; 2026-10-15; Codex Desktop 26.1007.71326 / codex-cli 0.162.0-alpha.17.2 / gpt-6-astra (ultra).
