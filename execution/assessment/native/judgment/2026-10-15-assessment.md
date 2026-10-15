# STAMPED and scientific assessment

Assessed commit: `f711558b2e29c376410e0e622b2f2a992f77bb41` (verified as `HEAD` before assessment). The checkout was clean. The assessment is read-only; all outputs are outside the assessed repository.

## STAMPED verdicts

**MUST:** 8 met / 5 partial / 4 unmet / 0 not-checked (17 items). **SHOULD:** 2 met / 5 unmet / 1 not-checked / 1 not-applicable (9 items). **MAY:** 2 met / 2 partial / 1 unmet (5 items). `partial` does not satisfy a MUST. There is no overall score.

### What to fix first

1. Pin and document the exact Pixi environment, its installation route and update process, and remove the undeclared external manifest override → this study's reported results cannot be tied to the environment a reader can rebuild → must/010–012, must/014–015, must/017, should/008.
2. Add a committed run record that names the code, inputs, outputs and exact environment → readers currently cannot connect the shipped maps, table and figures to the code and dependencies that produced them → must/006.
3. Publish the exact result commit and verify annex content retrieval from that publication → current repository heads are later and do not establish that this exact study snapshot is retrievable → must/016, must/005.
4. Add a root README or Makefile with environment setup and the entry command, plus a fresh-environment check → the result report has a command but does not establish a reproducible install or ongoing workflow test → must/007, should/002, should/004, should/006.
5. State reuse terms for the data and code → the object contains no license declaration → extra item `license-declared`.

### What the object already does well

- It keeps all 54 supplied maps, cohort metadata, provenance metadata, code, results and environment declaration under one root; the maps use annex pointers rather than large Git blobs (`input/`, `results/`, `pixi.toml`, `.gitattributes`).
- The group-analysis code checks source hashes, cohort size/group, image grids and finite values; it uses a common-support mask and participant-level sign-flip maximum-*t* inference (`results/code/group_analysis.py`).
- The report interprets the supplied coefficients cautiously, distinguishes whole-brain from vmPFC evidence, reports limitations, and links the code, summary table and figures (`results/report.md`).

### Per-item checklist

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `input`, `results`, `pixi.toml` | All components sit under the common repository root; inputs, results and environment spec are nested there. |
| must/002 | S.1 | met | judgement | `input/data/sub-001_hypo1_cope.nii.gz`, `input/sources.json` | The supplied maps and metadata are reachable under input/; sources.json records their origins and checksums. |
| must/003 | S.1 | met | judgement | `pixi.toml` | Analysis software dependencies are declared in the root Pixi environment; no external software module is required. |
| must/004 | T.1,T.3,T.5 | met | probe:tree-clean | `git ls-files`, `git status --porcelain` | git tracks 10 text, code and configuration file(s), and `git status` is empty including submodules: the committed state is the whole state. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex+judgement | `.gitattributes`, `input/data/sub-001_hypo1_cope.nii.gz` | The committed attributes and annex pointers content-address the large maps; the probe's untracked config citation is not needed. |
| must/006 | T.1,T.3,T.5 | unmet | probe:derived-have-records+judgement | `results/logs/group_analysis_release.log`, `pixi.toml` | Committed results lack a run record tying them to an exact environment; the release log also shows an external Pixi manifest override. |
| must/007 | A.1 | unmet | probe:entry-point | `git ls-files`, `results/report.md` | No README or Makefile gives installation and usage instructions; the results report is the only usage note. |
| must/008 | A.1 | met | probe:entry-point+judgement | `results/report.md`, `results/code/group_analysis.py` | The report gives the runnable Pixi command and identifies the group-analysis script as its entry point. |
| must/009 | P.1 | met | probe:no-abs-paths | `probe:no-abs-paths` | No host-specific absolute paths in tracked text files. Plus 1 /tmp path(s), portable but writing outside the object. |
| must/010 | P.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:env-spec-tracked | `pixi.toml` | pixi.toml lists dependencies but pins no versions (no lockfile or digest). |
| must/011 | P.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:platform-assumptions+judgement | `pixi.toml`, `results/logs/group_analysis_release.log#L1` | Pixi records target platforms, but the release log reveals an undocumented external PIXI_PROJECT_MANIFEST dependency. |
| must/012 | P.2 | partial ⚠ (a MUST is not satisfied by partial) | probe:platform-assumptions+judgement | `pixi.toml`, `results/report.md` | pixi.toml lists package and platform requirements, but the required Pixi installation/version and host setup are not documented. |
| must/013 | P.3 | met | probe:env-spec-tracked | `pixi.toml` | Tracked: pixi.toml. |
| must/014 | P.3 | unmet | judgement | `pixi.toml`, `results/report.md` | No lockfile or documented dependency-update and lock-regeneration process appears in the committed object. |
| must/015 | D.1 | unmet | probe:run-env-linked+judgement | `pixi.toml`, `git ls-files` | pixi.toml is not an exact environment snapshot: there is no committed lockfile or image digest. |
| must/016 | D.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:env-spec-tracked+judgement | `https://api.github.com/repos/leej3/stamped-ai-research-next/commits/f711558b2e29c376410e0e622b2f2a992f77bb41`, `git ls-remote origin`, `git ls-remote con-hub` | The repository resolves, but its current GitHub head is later and the exact assessed SHA returns 422; this does not show the worker version is retrievable. |
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

### Flagged items

- **must/005 (`probe-overridden`):** the probe cited a local `.datalad/config` not tracked in the committed inventory; the verdict rests on committed `.gitattributes` and annex pointer evidence.
- **must/008 (`probe-overridden`):** the entry-point probe missed the script under `results/code/`; the report gives its Pixi command, satisfying the broader starting-point property.
- **must/011–012 (`probe-overridden`):** the command scan could not assess the documented host route; the platform declaration and release log show an external `PIXI_PROJECT_MANIFEST` assumption.
- **must/015 (`probe-overridden`):** the probe had no run record to inspect; the committed environment specification itself has no lockfile or image digest.
- **must/016 (`mapping-questioned`):** the probe measured whether a Git remote resolved, not whether the exact assessed commit and its specification were retrievable. Current refs are later; the exact GitHub commit lookup returned 422.
- **must/014 and should/008 (`upstream-duplicate`):** these checklist items ask the same update-process question; both use the same evidence.
- **may/001 (`probe-overridden`):** the probe left it unchecked because there are no submodules; inspection shows external inputs and software exist but are embedded/declared rather than linked as submodules.

### Not checked

- **should/004:** a clean-environment rerun was outside the authorized scope. The replay record is [2026-10-15-fresh-rerun.json](2026-10-15-fresh-rerun.json); it records no clone, execution or output comparison. A separately authorized fresh-clone run from this exact commit would settle it once that commit is retrievable.

## Scientific adequacy and reported findings

**Assessment:** The committed analysis is scientifically responsive to the supplied group-level question and uses a defensible positive-direction, whole-brain familywise-error procedure. Its conclusion is limited to the supplied AO86 participant gain-effect maps and their fixed upstream model. The report's numerical results are assessed as reported artifacts; I did not execute or independently recompute them.

The code asserts 54 unique equal-indifference participants and checks each input checksum, common shape/affine and finite voxel values. It fits an intercept-only one-sample model to the common nonzero support (198,029 voxels), then uses 9,999 participant-level sign flips and a whole-brain maximum-*t* distribution. This preserves within-person spatial dependence and addresses the task's whole-brain correction requirement. The broad MNI coordinate box is specified in code and used to locate vmPFC evidence without small-volume correction; this is a transparent operationalization, though less anatomically specific than a validated atlas mask.

The committed summary reports no positive whole-brain-corrected vmPFC voxel: the box-average participant effect is −0.0029 cope (95% CI −0.0225 to 0.0168), and the strongest voxel in the box has FWE *p* = .937. It reports 24 corrected positive voxels elsewhere, with a whole-brain maximum at [−26, −102, −3.6] and FWE *p* = .0007; that does not support the vmPFC hypothesis. These reported results are in `results/tables/group_summary.json` and described in `results/report.md`.

The interpretation correctly says that the upstream gain regressor was mean-centered and variance-normalized: these coefficients are not slopes per currency unit or direct causal effects of changing monetary amounts. Gain and loss were modeled separately; participant variance maps are absent; the unweighted group analysis therefore cannot account for first-level precision. The report acknowledges the sign-flip symmetry assumption, the common-support mask, the approximate vmPFC localization, and fixed upstream choices that cannot be audited from these maps. A lack of corrected vmPFC evidence is not evidence of equivalence or proof of no gain coding.

**Blinding limitation:** the task and metadata identify the analysis cohort, so assessor blinding to cohort identity was unavailable. I did not infer or report any treatment assignment, and cohort identifiers were not used as STAMPED grading evidence.

## Scope, assumptions and retrieval checks

**Unattended assumption:** the supplied task establishes a computational research study answering a group-level fMRI hypothesis; I classify the object as a **study**. No human was attached to confirm this assumption.

The frozen skill and pinned conventions were read; `vendor_checklist.py --check` confirmed checklist 0.3.1 against its lock. The coordinator-supplied runner check reported source commit `d867c1d04bbb58b3b0f64122ebd5f76bd8e5a7ca`, environment commit `3552d5003a2485b6405805236d5c54e7ed42f097`, and `pixi.lock` SHA-256 `f8fff1394fbeaa2ab1c4993fceb0dd6463fe0c08c81fcda397f3e752a72c4249`. The runner's `probes` action was run against the absolute target path with remote checks enabled; it found no linked modules. Its `validate` action accepted all 31 checklist answers. The pinned encoder produced the [checklist URL](2026-10-15-url.txt), and decoding it round-tripped all 31 app answers and reasons.

Current retrieval checks found the GitHub repository and the CON Hub repository reachable, but their advertised heads are `87f38a710e57e1546091601c5382b9123a173914` and `441946a0d2687fb227f179b94cfacc843fff2348`. The GitHub API returned HTTP 422 for the exact assessed SHA. These current remote states do not establish what the worker published earlier, and subsequent coordinator publication is not attributed to this result commit. A HEAD request returned HTTP 200 for one recorded NeuroVault map URL and for the pinned cohort-table URL; this is a sample availability check, not verification of every annex object or all 54 source URLs. Details are in [2026-10-15-retrieval-checks.txt](2026-10-15-retrieval-checks.txt).

No scientific rerun was authorized or attempted. Existing result files were treated as artifacts to inspect, not as replay evidence. No project files were modified, and no source declaration was installed or repaired.

## Checklist URL and provenance

[Open the filled STAMPED checklist](2026-10-15-url.txt). The canonical per-item record is [2026-10-15-response.json](2026-10-15-response.json); raw probe output is [2026-10-15-probes.json](2026-10-15-probes.json), and the replay record is [2026-10-15-fresh-rerun.json](2026-10-15-fresh-rerun.json).

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, `af259ba`), on `git@github.com:leej3/stamped-ai-research-next.git` at commit `f711558b2e29c376410e0e622b2f2a992f77bb41`, 2026-10-15, Codex / model identifier unavailable from harness. Probe output: `2026-10-15-probes.json`.
