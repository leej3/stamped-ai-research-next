# STAMPED assessment — NARPS group analysis

**Assessed commit:** `510a685426804385a8c80f6347002ee47ce606e9` (verified as `HEAD`; committed tree clean)

**STAMPED verdicts:** MUST: 11 met / 3 partial / 3 unmet / 0 not-checked (17). SHOULD: 2 met / 0 partial / 5 unmet / 1 not-checked / 1 not-applicable (9). MAY: 3 met / 1 partial / 1 unmet / 0 not-checked / 0 not-applicable (5). There is no overall score.

## What to fix first

1. Track a resolved Pixi lock and document its update command and policy → makes the analysis environment reproducible and maintainable → `must/010`, `must/014`, `must/015`, `should/006`, `should/007`, `should/008`.
2. Add a root README with Pixi installation and the documented analysis command → gives a new reader a reliable route into the study → `must/007`, `must/017`.
3. Record the analysis invocation, input commit/checksums, exact environment lock and output paths together → ties the shipped results to the environment that produced them → `must/006`.
4. Add a recurring clean-environment workflow and state whether each run uses a disposable environment → checks that instructions and environment remain usable → `should/002`, `should/004`, `should/005`, `should/006`.
5. State reuse terms for the code and data → lets readers know whether and how the object may be redistributed; this is an extra finding outside the pinned checklist.

## What the project already does well

- It keeps the 54 participant maps, cohort metadata, methods note, code and results beneath one root; the source manifest records each map URL and SHA-256. The current header checks reached all 54 recorded NeuroVault map endpoints; see [remote checks](2026-10-15-remote-check.json).
- Git-annex carries binary content while Git tracks code, documentation and configuration; the committed tree was clean at the assessed commit. The source manifest, script and generated outputs are separated into recognizable locations.
- The scientific report makes the one-sided whole-brain criterion, anatomical proxy, effect-scale limits, exclusions and uncertainty visible. The script and numerical summary are available in [group_analysis.py](/Users/johnlee/.local/share/stamped-ai-research-next/judges/narps-suitability-20261015-01/scripts/group_analysis.py), [results.json](/Users/johnlee/.local/share/stamped-ai-research-next/judges/narps-suitability-20261015-01/results/results.json), and [report.md](/Users/johnlee/.local/share/stamped-ai-research-next/judges/narps-suitability-20261015-01/results/report.md).

## Scientific adequacy and supported findings

**Assessment:** The group analysis is scientifically defensible and adequate for the supplied group-analysis question, conditional on the fixed participant maps and upstream model. This scientific judgment is separate from the STAMPED findings below; no pipeline replay was performed.

The script joins the participant table to all 54 supplied gain-effect maps, verifies manifest checksums, finite values, common shape and affine, and excludes no participants. It uses an unweighted one-sample participant-level *t* model with a positive one-sided test. Its family-wise procedure is Bonferroni over the 198,029-voxel intersection mask, which is conservative and meets the task's whole-brain-correction requirement. The vmPFC operationalization is the Harvard–Oxford cortical atlas's 25% max-probability “Frontal Medial Cortex” label. That is a reproducible independent anatomical proxy, though not a uniquely established functional vmPFC boundary.

The supported result is **no whole-brain-corrected support for a positive effect in that vmPFC proxy**: its participant-level mean is −0.009 upstream units (95% *t* interval −0.040 to 0.022; descriptive one-sided *p* = .723), and no positive FWE-significant voxel overlaps it. Eleven positive voxels passed whole-brain Bonferroni correction elsewhere; their posterior/inferior edge locations are exploratory and do not answer the vmPFC hypothesis. The interval includes small effects of either sign, so this is not evidence of equivalence or a true zero effect.

Interpretation is appropriately limited: the maps are first-level contrast parameter estimates, with a centered and variance-normalized gain regressor, so they are not effects per currency unit. Participant variance maps are absent, preventing explicit first-level precision weighting. The analysis does not compare gain and loss slopes. Its strict nonzero-intersection mask and atlas boundary are defensible choices but could affect sensitivity; no mask/atlas sensitivity analysis or robust group-model comparison is reported. These limits qualify the result without invalidating the primary test.

Evidence: [scientific report](/Users/johnlee/.local/share/stamped-ai-research-next/judges/narps-suitability-20261015-01/results/report.md), [analysis code](/Users/johnlee/.local/share/stamped-ai-research-next/judges/narps-suitability-20261015-01/scripts/group_analysis.py), [fixed upstream methods](/Users/johnlee/.local/share/stamped-ai-research-next/judges/narps-suitability-20261015-01/input/upstream-methods.md), [quality summary](/Users/johnlee/.local/share/stamped-ai-research-next/judges/narps-suitability-20261015-01/results/map_quality.tsv), and [participant ROI estimates](/Users/johnlee/.local/share/stamped-ai-research-next/judges/narps-suitability-20261015-01/results/participant_roi_estimates.tsv).

## Per-item checklist

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `git ls-tree`, `input/sources.json` | All committed files sit beneath the study root; inputs, code and results are root-relative. |
| must/002 | S.1 | met | judgement | `input/data`, `input/sources.json` | The 54 maps and cohort metadata are inside input/; sources.json links back to their retrievable origins. |
| must/003 | S.1 | met | judgement | `pixi.toml#L5-L27`, `scripts/group_analysis.py#L5-L10` | Python packages imported by the group script are declared in the tracked Pixi environment. |
| must/004 | T.1,T.3,T.5 | met | probe:tree-clean | `git ls-files`, `git status --porcelain` | Git tracks code, text and configuration; the requested commit has a clean working tree. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex | `git ls-tree -r -l HEAD`, `.datalad/config` | Git-annex carries the binary content; the probe found 55 annex pointers and no oversized Git binary. |
| must/006 | T.1,T.3,T.5 | unmet | probe:derived-have-records | `results/figures/roi_participants.png`, `results/figures/whole_brain_fwe.png`, `results/figures/whole_brain_t.png`, `results/logs/failed_attempts.md`, `results/logs/group_analysis.log`, `results/map_quality.tsv`, `results/maps/group_mean_gain_effect.nii.gz`, `results/maps/group_p_fwe_bonferroni.nii.gz`, `results/maps/group_p_positive.nii.gz`, `results/maps/group_t_fwe05.nii.gz` | Derived results have no run record or tracked workflow linking them to the exact environment used. |
| must/007 | A.1 | unmet | probe:entry-point | `git ls-tree` | The commit has no README with install/use instructions or Makefile; the report is not either required entry document. |
| must/008 | A.1 | met | probe:entry-point+judgement | `results/report.md#Reproducibility`, `scripts/group_analysis.py#L1-L16` | The report gives a runnable Pixi command for scripts/group_analysis.py, a clear analysis starting point. |
| must/009 | P.1 | met | probe:no-abs-paths | `probe:no-abs-paths` | The probe found no host-specific absolute paths in tracked text files. |
| must/010 | P.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:env-spec-tracked+judgement | `probe:env-spec-tracked` | pixi.toml declares dependencies, but wildcard versions and the ignored, absent pixi.lock do not fix them. |
| must/011 | P.1 | met | judgement | `pixi.toml#L1-L4`, `results/report.md#Reproducibility`, `probe:platform-assumptions` | Pixi declares supported platforms; the report documents Pixi execution and network-fetched atlas/template inputs. |
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

- `must/008` (`probe-overridden`): the entry-point probe missed the script because it did not identify it through the README/Makefile route; the report documents `pixi run python scripts/group_analysis.py` and the script is present.
- `must/014` and `should/008` (`upstream-duplicate`): these checklist items ask the same environment-update question, so the same unmet judgment is repeated intentionally.
- `must/015` (`mapping-questioned`, `probe-overridden`): `run-env-linked` only established that no run record named an environment; the item asks whether an exact environment specification is available. Pixi declarations exist, but the missing lock makes the answer partial.
- `should/002` (`mapping-questioned`): no CI configuration does not by itself rule out manual checks; inspection found no recurring test route, and the lone analysis log is not regular testing.
- `should/006` (`mapping-questioned`): no CI configuration alone does not establish whether exact environments are reconstituted; the missing lock and absence of any recurring reconstitution check support unmet.

## Additional finding outside the checklist

The probe found no `LICENSE`, `LICENSES/`, `REUSE.toml` or dataset `License` field in the 78 tracked paths. Reuse terms are unstated; this is recorded as `license-declared` in the response JSON, not folded into a checklist item.

## Not checked

- `should/004`: fresh-environment pipeline replay was not checked. The coordinator runner's `fresh-rerun` action executes the scientific entry point; the user excluded that replay from this scope. The [replay record](2026-10-15-replay-record.json) records the reason and what would settle it.

No other checklist item is not-checked. The header-only NeuroVault checks and exact-commit GitHub fetch establish current availability only; they do not establish what the worker supplied or published at an earlier time. See [remote checks](2026-10-15-remote-check.json).

## Goals and kind

**Assumption, not human-confirmed:** the object is a study whose goal is to test the positive gain-effect hypothesis in vmPFC for the NARPS equal-indifference group using the supplied 54 participant maps. This follows the retained task brief and `input/study-task.md`. The primary kind is **study**, so the assessment emphasizes the link between inputs, computation and reported results, as well as environment portability and retrieval.

## Checklist URL and record

The [checklist application URL](2026-10-15-url.txt) is generated from the validated response. Its encode/decode roundtrip reproduced the same URL; the decoder omits assessor metadata and evidence because the application payload stores only checklist responses. See [roundtrip JSON](2026-10-15-url-roundtrip.json).

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, commit `af259bad237fa57b856417db8dba45a1b283a527`), on commit `510a685426804385a8c80f6347002ee47ce606e9`, 2026-10-15. Harness: OpenAI Codex API; runtime build unavailable. Model identity was not exposed to this session. Recorded assessor environment: source commit `d867c1d04bbb58b3b0f64122ebd5f76bd8e5a7ca`, environment commit `3552d5003a2485b6405805236d5c54e7ed42f097`; see [assessor runtime record](2026-10-15-assessor-runtime.json). The exact remote commit is currently retrievable, but that does not date its publication to the worker's contribution.

Probe output: [2026-10-15-probes.json](2026-10-15-probes.json). Canonical per-item answers and evidence: [2026-10-15-response.json](2026-10-15-response.json).
