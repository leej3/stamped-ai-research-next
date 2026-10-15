# STAMPED assessment — 2026-10-15

**MUST:** 10 met / 1 partial / 6 unmet / 0 not-checked (17). **SHOULD:** 2 met / 0 partial / 5 unmet / 1 not-checked / 1 not-applicable (9). **MAY:** 4 met / 0 partial / 1 unmet / 0 not-checked / 0 not-applicable (5). No overall score is assigned.

Scope: exact committed state `466d43f39dc3d40ac64038ff03066b483b6d9457`; checkout was clean. The retained `input/study-task.md` SHA-256 matches the supplied brief (`e92bf2e0c0db4cc49688cce9f9dfff8a236fc4ec151c09961719f49f31310cc8`). Inspection and current remote retrieval checks only. No source changes. The supplied scientific task defines a group-analysis study, so `study` is the unattended kind assumption; no human confirmation was available. The target contains participant identifiers and cohort metadata, so assessor blinding to cohort labels was limited. No assignment inference was made. Later remote availability does not establish who supplied that publication or what was retrievable earlier.

## What to fix first

1. Freeze the analysis environment and link its exact snapshot from a run record → results cannot currently be tied to the mutable package specification (`must/006`, `must/015`).
2. Declare how the environment is updated and record that process in version history → dependency changes otherwise undermine reliable reuse (`must/014`, `should/008`; duplicate checklist item).
3. Add clear Pixi installation and system requirements, including the nilearn template retrieval or a bundled/pinned template → the documented command has unlisted host and network prerequisites (`must/007`, `must/011`, `must/012`, `must/017`).
4. Add a recurring clean-environment workflow that rebuilds the pinned environment and checks the analysis → the current single run log does not establish a maintained reproduction route (`should/002`, `should/006`).

## What the project already does well

- The 54 participant maps and metadata are inside the object; all 54 annex keys currently check present on `con-hub`. The source manifest records source URLs and hashes ([input/sources.json](/Users/johnlee/.local/share/stamped-ai-research-next/judges/narps-suitability-20261015-02/input/sources.json); probe and remote-check evidence below).
- The analysis checks identifiers, geometry, finite values and source hashes, reports no exclusions, and uses a directional whole-brain max-*t* permutation correction ([results/analysis.py](/Users/johnlee/.local/share/stamped-ai-research-next/judges/narps-suitability-20261015-02/results/analysis.py), [results/quality_checks.tsv](/Users/johnlee/.local/share/stamped-ai-research-next/judges/narps-suitability-20261015-02/results/quality_checks.tsv)).
- The scientific report explains effect-map scaling, missing participant variance maps, permutation assumptions and why lack of vmPFC support is not proof of no effect ([results/report.md](/Users/johnlee/.local/share/stamped-ai-research-next/judges/narps-suitability-20261015-02/results/report.md)).

## Checklist responses

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
| must/011 | P.1 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `pixi.toml`, `results/analysis.py` | Pixi platforms are specified, but Pixi installation and network or cache needs for the nilearn template are undocumented. |
| must/012 | P.2 | unmet | judgement | `pixi.toml`, `results/analysis.py` | No requirements list names the Pixi host tool or the template retrieval needed for a clean figure run. |
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

- `must/006` — the probe treats missing provenance as no run record, but `results/run.log` is present. The item still fails: that log does not identify the complete frozen environment used. The probe measured a replayable record, while the checklist asks for the exact environment in provenance (`mapping-questioned`).
- `must/008` — the entry-point probe missed the script because it did not find a README or Makefile. The documented command names `results/analysis.py`, which satisfies the clear-starting-point item (`probe-overridden`).
- `must/010` — the environment probe focused on version pinning. `pixi.toml` does declare the dependencies imported by the group analysis, so inclusion is met; absent exact pins are assessed under `must/015` (`probe-overridden`).
- `must/015` — the probe left this unchecked because no run environment was linked. The tracked Pixi spec is identifiable but mutable and has no lockfile or digest, so exact replication is unmet (`probe-overridden`).
- `must/014` and `should/008` — these are word-for-word duplicate checklist questions; both answers use the same evidence (`upstream-duplicate`).

## Not checked

- `should/004`: no clean-container, VM, batch-job or cloud test was established. A recorded test in one of those environments would settle it.
- Scientific fresh replay: not authorized and not executed. The replay record is [2026-10-15-fresh-rerun.json](2026-10-15-fresh-rerun.json). `fresh-rerun --help` confirms that the action clones and runs the entry point; no outputs were reused as replay evidence.

## Goals and kind

The supplied brief asks whether the group-level gain-effect estimate increases in vmPFC for the equal-indifference cohort, using 54 fixed participant maps and whole-brain-corrected inference. This is a computational **study**; that kind is an unattended assumption based on the brief. All seven STAMPED principles apply, with particular attention to provenance, input boundaries, environment portability and reuse of the derived analysis.

## Scientific adequacy and supported findings

The group analysis is scientifically adequate for the supplied group-stage question, conditional on the fixed first-level maps. It includes all 54 supplied participants and reports geometry, finite-value and checksum checks with no exclusions. It tests a one-sample positive group effect and uses participant sign flips with whole-brain positive max-*t* familywise correction, as required. The vmPFC target is an explicit 15 mm sphere centered at MNI (0, 40, −10), specified independently of the observed effects; it supplements rather than replaces corrected whole-brain inference (`results/analysis.py`, `results/summary.json`).

The supplied results do **not support** the predicted positive vmPFC response: the sphere mean was −0.00275 (95% CI −0.0242 to 0.0187), and the one-sided sign-flip *p* was .607. A positive whole-brain corrected cluster was found (24 voxels; peak *t*(53)=6.62, max-*t* FWE *p*=.0008), but its peak at MNI (−26, −102, −3.6) is posterior and outside vmPFC. That finding does not support the vmPFC hypothesis (`results/summary.json`, `results/group_t_fwe_map.png`).

These coefficients are effects of an upstream mean-centered, variance-normalized gain regressor, not BOLD change per currency unit. Gain and loss were modeled separately, so the maps do not estimate a direct gain-versus-loss contrast despite the unequal ranges. The group test weights participants equally because participant variance maps were unavailable. Sign-flip inference assumes exchangeable participant effects and a symmetric null; 10,000 Monte Carlo permutations give finite precision. The vmPFC interval permits small positive and negative effects, and a different anatomical boundary could change the regional summary. Thus, lack of corrected vmPFC support is not evidence that no gain-related response exists; it means this conditional analysis did not provide the specified corrected evidence (`input/upstream-methods.md`, `results/report.md`).

## Checklist URL and provenance

The [checklist application URL](2026-10-15-url.txt) was generated from the validated response. Its decode roundtrip preserved all 31 ids, application values and reasons.

Response JSON: [2026-10-15-response.json](2026-10-15-response.json). Probe output: [2026-10-15-probes.json](2026-10-15-probes.json). Runtime pin: [2026-10-15-runtime.json](2026-10-15-runtime.json). Replay record: [2026-10-15-fresh-rerun.json](2026-10-15-fresh-rerun.json).

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, `af259ba`), on the committed object at `466d43f39dc3d40ac64038ff03066b483b6d9457`, 2026-10-15, OpenAI Codex API / GPT-6. Probe output: [2026-10-15-probes.json](2026-10-15-probes.json). Runtime pin: [2026-10-15-runtime.json](2026-10-15-runtime.json).
