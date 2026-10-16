# STAMPED assessment: NARPS Hypothesis 1 group analysis

**MUST:** 16 met / 0 partial / 1 unmet / 0 not-checked (17 total). **SHOULD:** 3 met / 1 partial / 4 unmet / 0 not-checked / 1 not-applicable (9 total). **MAY:** 5 met / 0 partial / 0 unmet / 0 not-checked / 0 not-applicable (5 total). A partial MUST does not satisfy that item; there is no combined score.

## What to fix first

1. **Publish this study commit and verify the annex retrieval route from a clean authorized clone** → a researcher must be able to retrieve the exact object, its 54 maps and environment; current remote refs do not expose the target commit and the annex fetch failed → `must/016`.
2. **Add a recurring CI or scheduled reconstitution check** → it would detect drift in the documented run instructions and locked environment → `should/002`, `should/006`.
3. **Run analyses in a disposable environment** → this would reduce dependence on a long-lived Pixi install and improve run isolation → `should/004`, `should/005`.
4. **Archive executable environment artifacts where feasible** → the lock is present, but the built environment itself is not carried with the study → `should/007`.

## What is already good

- The report uses a one-sided participant-level sign-flip test with max-statistic correction over 198,029 voxels; the vmPFC atlas overlay is prespecified and does not shrink the correction family. See [analysis protocol](/Users/johnlee/.local/state/stamped-ai-research-next/preparation-20261015/cold-stamped-op-judge-target/analysis-protocol.md) and [scientific report](/Users/johnlee/.local/state/stamped-ai-research-next/preparation-20261015/cold-stamped-op-judge-target/results/report.md).
- The retained run record links code revision, input hashes, output hashes, package versions, platform and exact Pixi manifest/lock hashes. The code and environment specifications are tracked at the assessed commit: [run provenance](/Users/johnlee/.local/state/stamped-ai-research-next/preparation-20261015/cold-stamped-op-judge-target/logs/20261015T233701Z-provenance.json), [Pixi manifest](/Users/johnlee/.local/state/stamped-ai-research-next/preparation-20261015/cold-stamped-op-judge-target/pixi.toml), [Pixi lock](/Users/johnlee/.local/state/stamped-ai-research-next/preparation-20261015/cold-stamped-op-judge-target/pixi.lock).
- The report makes the cope scaling limits and absent participant variance maps explicit, and gives participant-level and regional uncertainty rather than treating a non-significant result as proof of zero effect: [report](/Users/johnlee/.local/state/stamped-ai-research-next/preparation-20261015/cold-stamped-op-judge-target/results/report.md), [QC and results](/Users/johnlee/.local/state/stamped-ai-research-next/preparation-20261015/cold-stamped-op-judge-target/results/results.json).

## Per-item assessment

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `README.md`, `.gitmodules` | All study inputs, code, environment, results and run logs are under one root; the skills dependency is a pinned submodule. |
| must/002 | S.1 | met | probe:subdatasets-resolvable | `.gitmodules`, `input/sources.json` | The skills submodule URL resolves; study maps are under input/data as annex content. |
| must/003 | S.1 | met | judgement | `pixi.toml`, `README.md` | Scientific packages, git-annex and duct are in the Pixi environment; README documents Git and Pixi setup. |
| must/004 | T.1,T.3,T.5 | met | probe:tree-clean | `git status --porcelain`, `/Users/johnlee/.local/state/stamped-ai-research-next/preparation-20261015/cold-stamped-op-evidence/judgment-01/worker-end-state.json` | Git tracks code, text and configuration; the worker-stop receipt records this exact commit with a clean tree. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex | `input/data`, `.datalad/config` | Git-annex tracks the 54 participant maps and other large content; no oversized binary blobs are in Git. |
| must/006 | T.1,T.3,T.5 | met | probe:derived-have-records+judgement | `logs/20261015T233701Z-provenance.json`, `scripts/write_run_record.py` | The final run record hashes code, Pixi manifest/lock, inputs and 14 outputs; the path probe missed this linked record. |
| must/007 | A.1 | met | probe:entry-point | `README.md` | README gives locked Pixi installation, annex retrieval and run instructions. |
| must/008 | A.1 | met | probe:entry-point | `README.md`, `scripts/run_recorded_analysis.sh` | The README identifies pixi run recorded-analysis and the tracked run wrapper as the starting point. |
| must/009 | P.1 | met | probe:no-abs-paths | `probe:no-abs-paths` | The probe found no host-specific absolute paths in tracked text. |
| must/010 | P.1 | met | probe:env-spec-tracked+judgement | `pixi.toml`, `scripts/analyze.py`, `scripts/run_recorded_analysis.sh` | Imports and invoked tools are declared in Pixi, including neuroimaging packages, Git-annex and duct; no missing runtime dependency was found. |
| must/011 | P.1 | met | judgement | `README.md` | README states macOS 14+ ARM64 and Linux x86-64; the documented route names Git, Pixi and annex retrieval. |
| must/012 | P.2 | met | judgement | `README.md`, `pixi.toml` | README lists Git, Pixi, supported platforms and the locked environment installation. |
| must/013 | P.3 | met | probe:env-spec-tracked+judgement | `pixi.toml`, `pixi.lock` | pixi.toml and pixi.lock are tracked at the assessed commit; an uninitialized skills submodule does not hold the analysis environment. |
| must/014 | P.3 | met | judgement | `README.md`, `git log -- pixi.toml pixi.lock` | README gives pixi add/remove and requires reviewing and committing manifest plus lock; history shows dependency changes and tracked lock updates. |
| must/015 | D.1 | met | judgement | `pixi.lock`, `logs/20261015T233701Z-provenance.json` | The object carries the committed Pixi lock and run-specific manifest/lock hashes, enabling an exact environment attempt. |
| must/016 | D.1 | unmet | probe:env-spec-tracked+judgement | `2026-10-16-remote-check.txt`, `2026-10-16-fresh-rerun.json`, `README.md` | The authorized hub route exposes no ref for this commit; a fresh clone cannot retrieve its 54 required participant maps from the annex remote. |
| must/017 | D.1 | met | judgement | `README.md` | README explains Pixi installation, locked environment restoration, input retrieval and both analysis and validation commands. |
| should/001 | T.2 | met | judgement | `.gitmodules`, `input/data` | Git tracks project text, code and environment; git-annex handles large files and the skills module is a Git submodule. |
| should/002 | A.2 | unmet | probe:ci-present | `probe:ci-present`, `README.md` | No CI workflow or recurring test route was found to check that README instructions remain accurate. |
| should/003 | M.1 | met | probe:modules-separated | `input/, scripts/, results/, pixi.toml, pixi.lock` | Inputs, analysis code, results and environment files occupy distinct named project areas. |
| should/004 | E.1 | unmet | judgement | `2026-10-16-fresh-rerun.json`, `logs/replay-compare-final-20261015-stdout` | No clean VM, container or cloud run is recorded; the authorized fresh clone stopped when 54 maps could not be retrieved. |
| should/005 | E.1 | unmet | judgement | `README.md`, `pixi.toml` | The README runs analyses in a persistent Pixi project environment; no disposable environment is spawned for each run. |
| should/006 | D.2 | partial | probe:ci-present+judgement | `logs/replay-compare-final-20261015-stdout`, `probe:ci-present` | One same-host replay tested the lock once, but no recurring exact-environment CI or periodic reconstitution test is recorded. |
| should/007 | D.2 | unmet | judgement | `pixi.toml; pixi.lock` | The lock and manifest are archived, but executable environment artifacts or binaries are not stored with the object. |
| should/008 | D.2 | met | judgement | `README.md`, `git log -- pixi.toml pixi.lock` | Same documented update procedure and history as must/014: Pixi changes are reviewed and committed with the lock. |
| should/009 | M.4 | not-applicable | judgement | `input/sources.json` | N/A: all supplied maps and software components are public; there is no restricted component to isolate. |
| may/001 | M.2 | met | probe:subdatasets-resolvable | `.gitmodules`, `input/data` | The pinned skills dependency is a resolvable Git submodule; participant maps are separately linked by git-annex. |
| may/002 | M.2 | met | judgement | `README.md` | README describes the inputs, code, results and environment areas and how to run the analysis. |
| may/003 | M.2 | met | judgement | `input/, scripts/, results/, pixi.toml, pixi.lock` | Code, source inputs, result outputs and environment specs can be updated independently in their named areas. |
| may/004 | M.2 | met | judgement | `README.md`, `pixi.toml` | README composes annex retrieval, locked Pixi setup and the recorded-analysis task into a reproducible sequence. |
| may/005 | M.2 | met | judgement | `README.md` | README names component locations and the commands for restoring inputs, running analysis and validating results. |

## Flagged items

- `must/006` — overridden: the derived-file probe did not detect the tracked run record that hashes the outputs and exact environment.
- `must/010` — overridden: the environment probe found a pinned but uninitialized skills submodule; the analysis runtime dependencies and invoked tools are declared in Pixi.
- `must/013` — overridden: an uninitialized skills submodule does not change that the analysis manifest and lock are tracked in this commit.
- `must/014` and `should/008` — duplicate checklist wording; both use the same update instructions and environment history.
- `must/016` — overridden using retrieval evidence: the hub exposes no ref for the target commit, and a fresh clone could not retrieve its 54 map inputs.
- `should/006` — overridden: the CI probe found no workflow, while a single same-host replay is recorded; one run is not regular testing.

## Not checked

No checklist item remains `not-checked`. The authorized fresh-clone replay did not complete: the clone retained 16 result candidates, but `git annex get` failed for all 54 participant maps. The separate runner record is [fresh-rerun.json](2026-10-16-fresh-rerun.json). Existing output files were not used as proof of a replay.

## Goals and kind

**Assumption, not confirmed with a human:** this is a study whose product is a group-level answer to the supplied NARPS Hypothesis 1 question. That goal comes from the coordinator-supplied scientific brief and the repository's README/protocol. The kind is **study**, so the assessment emphasizes tracked provenance and inputs, the actionable analysis route, portability and retrievability.

## Scientific adequacy (separate from STAMPED)

**Classification: supported** for the report's conclusion that these supplied data do not provide whole-brain-corrected evidence of a positive vmPFC response. The report tested the 54 supplied participants with a positive one-sample *t* statistic, 9,999 participant-level sign flips and a maximum-*t* null over the full common-support mask. None of 1,422 predefined vmPFC voxels survived whole-brain FWE correction; the best vmPFC voxel had *t*=4.19 and FWE *p*=.782. The regional cope mean was 0.0027, with both the *t*-based and participant-bootstrap 95% intervals spanning zero. The 24 corrected positive voxels were outside vmPFC.

The conclusion is lack of evidence at this sample size and resolution, not evidence that vmPFC response is exactly zero. The method is defensible conditional on the supplied first-level maps: it preserves the whole-brain correction requirement, defines vmPFC anatomically in advance, checks cohort/map identity, geometry and finite values, excludes no participant, and reports uncertainty. Sign-flip inference assumes exchangeability and a symmetric zero-centered null. The upstream gain modulator was mean-centered and variance-normalized; the supplied copes are not monetary-unit slopes or raw BOLD change. Participant variance maps are absent, so precision-weighted mixed-effects inference is unavailable. These limitations are stated in [the report](/Users/johnlee/.local/state/stamped-ai-research-next/preparation-20261015/cold-stamped-op-judge-target/results/report.md) and [protocol](/Users/johnlee/.local/state/stamped-ai-research-next/preparation-20261015/cold-stamped-op-judge-target/analysis-protocol.md).

## Worker state and access attribution

The [external worker-stop receipt](/Users/johnlee/.local/state/stamped-ai-research-next/preparation-20261015/cold-stamped-op-evidence/judgment-01/worker-end-state.json) records a successful exit, the requested HEAD `8b5bcdaa999289a47f066ba829511d450301c573`, and an empty worktree/index. That supports worker credit for committing and tracking the delivered files; later coordinator preservation does not add credit. At assessment time the hub URL exposed the parent repository's `main` and `git-annex` refs, not the requested study commit ([remote check](2026-10-16-remote-check.txt)). A clone made from the local target path retained 16 result candidates but could not retrieve any of the 54 participant maps; this local-path clone is not evidence of remote delivery. For access, the intended recipient is a researcher using the authorized Git plus annex route; anonymous access was not required. Required coverage is the exact study commit, locked environment, all 54 input maps, and the outputs/logs needed to inspect and reproduce the report. The tested host was macOS 27 ARM64 in an authorized local context; this does not establish access from another host. No required artifacts were verified through the hub route, so `must/016` is `unmet`.

## Checklist link and stamp

The [checklist app URL](2026-10-16-url.txt) opens these answers. The validated canonical record is [response JSON](2026-10-16-response.json); the raw probe output is [probes JSON](2026-10-16-probes.json).

Produced 2026-10-16 by `assess-alignment-with-stamped-principles` 0.1.0 and `stamped-conventions` 0.1.0, checklist 0.3.1, using Codex API / GPT-6 (exact deployment unavailable). The pinned assessor runtime is recorded in [runtime check](2026-10-16-runtime-check.txt): source commit `0208f82504f15b82b7582f34143ab889dd52c68d`, environment commit `3552d5003a2485b6405805236d5c54e7ed42f097`. Target commit: `8b5bcdaa999289a47f066ba829511d450301c573`.
