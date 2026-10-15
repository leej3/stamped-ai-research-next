# STAMPED assessment — NARPS potential-gain study

## Verdict

- **MUST:** 5 met / 7 partial / 5 unmet / 0 not-checked (17)
- **SHOULD:** 0 met / 3 partial / 4 unmet / 1 not-checked / 1 not-applicable (9)
- **MAY:** 3 met / 2 partial / 0 unmet / 0 not-checked / 0 not-applicable (5)

No overall score is assigned.

## What to fix first

1. **Commit the worker’s analysis, result artifacts and a run record together, including the exact environment used** → currently the coordinator’s preservation commit supplies these tracked artifacts, while the worker stop left them untracked and `pixi.toml` modified → closes must/004, must/006, must/013 and should/001.
2. **Correct the sign-flip loop and regenerate the group inference** → it leaves one of 10,000 max-statistic entries uninitialized, compromising the reported whole-brain adjusted p-values and voxel counts → addresses the scientific-method limitation and supports must/006 and must/008.
3. **Publish the exact commit plus retrievable annex payloads, including derived results** → the input maps are independently available, but the Git remote does not serve this commit and the annex payloads could not be fetched → closes must/016.
4. **Document setup, the exact run command and a dependency-lock update procedure; pin the environment** → readers currently have a script and broad package declarations but no reproducible setup route → closes must/007, must/008, must/010–015 and must/017.
5. **Move code out of `results/` and add a recurring clean-environment workflow check** → code and derived outputs are mixed, and no CI tests the workflow → closes should/002–006.

## What the project already does well

- `input/sources.json` identifies each source map with size and SHA256; all 54 NeuroVault files were retrieved and hash-verified independently.
- `results/report.md`, `results/quality_checks.json` and the group figure expose cohort completeness, geometry, coverage, nonfinite/variance checks, model assumptions, effect scaling, and interpretation limits.
- The report distinguishes the hypothesized vmPFC result from posterior whole-brain findings and correctly cautions that lack of support is not proof of a zero effect.

## Per-item checklist

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `git ls-files` | The input, code, environment and results are nested under the repository root. |
| must/002 | S.1 | met | probe:subdatasets-resolvable+judgement | `input/data`, `input/sources.json` | The maps are annexed under input/data; cohort and source manifest are inside input/. |
| must/003 | S.1 | met | judgement | `pixi.toml` | pixi.toml declares the Python and imported analysis packages inside the project. |
| must/004 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:tree-clean+judgement | `/Users/johnlee/.local/state/stamped-ai-research-next/preparation-20261015/cold-retry-evidence/worker-01/judgment-01/worker-end-state.json`, `git status --porcelain` | At worker stop, pixi.toml was modified and analysis/results/logs were untracked; coordinator later committed retained artifacts. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex | `probe:large-in-annex`, `2026-10-15-retrieval-check.json` | Large participant maps use git-annex pointers; all 54 source maps also retrieved with matching SHA256. |
| must/006 | T.1,T.3,T.5 | unmet | probe:run-env-linked+judgement | `probe:run-env-linked`, `git ls-files logs` | No run record linking the shipped results to an exact environment is tracked in the assessed commit. |
| must/007 | A.1 | unmet | probe:entry-point | `probe:entry-point` | No README.md or Makefile gives installation and use instructions. |
| must/008 | A.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:entry-point+judgement | `results/report.md`, `probe:entry-point` | results/analyze.py is named as the analysis code, but no documented command or complete reproduction route is provided. |
| must/009 | P.1 | met | probe:no-abs-paths | `probe:no-abs-paths` | Tracked scripts use repository-relative paths; the path probe found no host-specific absolute paths. |
| must/010 | P.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:env-spec-tracked+judgement | `pixi.toml` | pixi.toml lists imported packages, but wildcard versions and no lockfile leave dependency resolution unpinned. |
| must/011 | P.1 | unmet | judgement | `pixi.toml`, `results/report.md` | The environment lists OS targets, but installation/runtime host requirements and annex access assumptions are not documented. |
| must/012 | P.2 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `pixi.toml`, `results/report.md` | pixi.toml lists Python and packages, but does not give a complete system-requirements or setup list. |
| must/013 | P.3 | partial ⚠ (a MUST is not satisfied by partial) | probe:env-spec-tracked+judgement | `pixi.toml`, `/Users/johnlee/.local/state/stamped-ai-research-next/preparation-20261015/cold-retry-evidence/worker-01/judgment-01/worker-end-state.json` | pixi.toml is tracked in the retained commit, but it was modified and uncommitted at worker stop. |
| must/014 | P.3 | unmet | judgement | `pixi.toml`, `git log --oneline` | No runnable process for updating dependency specifications is documented. |
| must/015 | D.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:run-env-linked+judgement | `pixi.toml` | pixi.toml is present but unpinned; no lockfile or published environment artifact fixes exact package versions. |
| must/016 | D.1 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `2026-10-15-retrieval-check.json`, `git fetch --depth`, `2026-10-15-fresh-rerun.json` | A researcher can retrieve all 54 inputs from NeuroVault; the exact Git commit and annexed results were not independently retrievable. |
| must/017 | D.1 | unmet | judgement | `results/report.md`, `pixi.toml` | The report names a script but does not document how to obtain or use the environment for reproduction. |
| should/001 | T.2 | partial | judgement | `worker-end-state.json`, `input/data` | Git and annex cover inputs, but worker analysis code and results were untracked at stop; coordinator later recorded them. |
| should/002 | A.2 | unmet | probe:ci-present | `probe:ci-present` | No CI or other committed recurring check tests the documented workflow. |
| should/003 | M.1 | partial | probe:modules-separated+judgement | `input, pixi.toml and results`, `results/analyze.py` | Inputs, environment and derived results have separate paths, but the analysis code is stored inside results/. |
| should/004 | E.1 | not-checked | judgement | `2026-10-15-fresh-rerun.json` | The fresh-clone attempt could not fetch annex payloads, so it never executed the pipeline; an accessible clone is needed. |
| should/005 | E.1 | unmet | judgement | `results/quality_checks.json`, `pixi.toml` | The delivered runs used a host Python environment; no container, clean-VM or disposable-environment mechanism is specified. |
| should/006 | D.2 | unmet | probe:ci-present | `probe:ci-present` | There is no CI or recorded clean rebuild testing that recreates the exact environment. |
| should/007 | D.2 | partial | judgement | `pixi.toml` | pixi.toml is retained, but no lockfile or archived environment artifact is provided. |
| should/008 | D.2 | unmet | judgement | `pixi.toml` | No process for updating dependency specifications is documented; this duplicates must/014. |
| should/009 | M.4 | not-applicable | judgement | `input/sources.json` | N/A: the supplied data and listed dependencies are public; no restricted component is present. |
| may/001 | M.2 | met | probe:subdatasets-resolvable+judgement | `input/data`, `pixi.toml` | External maps are included through annex pointers and software is declared in pixi.toml. |
| may/002 | M.2 | met | judgement | `results/report.md` | The report describes the inputs, analysis code and outputs and how they relate. |
| may/003 | M.2 | partial | judgement | `results/analyze.py`, `input, results, pixi.toml` | Input, environment and output paths are separable, but code shares the results directory and no tests protect independent updates. |
| may/004 | M.2 | partial | judgement | `results/analyze.py`, `results/report.md` | analyze.py reads input/ and writes results/, but no explicit module-composition or orchestration procedure is documented. |
| may/005 | M.2 | met | judgement | `results/report.md` | The report's reproducibility-files section helps readers identify code and key outputs. |

## Flagged items

- **must/002, may/001 — mapping-questioned:** `subdatasets-resolvable` only checked for Git submodules/subdatasets; it missed the annexed inputs and source manifest inside the project boundary. The verdict reflects those contents and their recorded routes.
- **must/004 — probe-overridden:** `tree-clean` measures the coordinator-preserved commit. The worker-stop receipt shows modified `pixi.toml` and untracked analysis, result and log files; coordinator preservation does not count as worker tracking.
- **must/006 — probe-overridden:** the probe found no tracked run records and left the item unchecked. The assessed commit contains derived outputs but no tracked run record linking them to an exact environment, so the item is unmet.
- **must/008 — probe-overridden:** the probe found no README/Makefile instructions. `results/report.md` names `results/analyze.py`, which is a starting script, but no command or complete reproduction route is documented; partial is the better fit.
- **must/013 — probe-overridden:** `pixi.toml` is tracked by the retained commit, but the receipt records it as modified at worker stop.
- **must/015 — probe-overridden:** the probe found no environment-linked run record; inspection also shows `pixi.toml` uses unpinned versions and there is no `pixi.lock`, so exact reconstruction is only partial.
- **should/003 — probe-overridden:** the path probe sees separate `input/`, `results/` and `pixi.toml`, but `results/analyze.py` puts code beside derived outputs.

## Not checked

- **should/004:** the authorized fresh-clone attempt could not fetch annex content and stopped before the entrypoint ran. A successful fresh run from a clone with the declared inputs would settle whether the pipeline runs in an isolated environment. It ran on the same host as this assessment; it does not establish cross-host portability.

## Scientific adequacy and findings (separate from STAMPED)

**Scientific adequacy: qualified.** The retained analysis gives a defensible operational definition of vmPFC (a 10-mm sphere centered at MNI [0, 45, -6]), includes all 54 supplied participants, checks common image geometry and map quality, uses a one-sided participant-level sign-flip max-T procedure over the whole support mask, and explains the assumptions and limitations of the upstream normalized gain-modulator estimates. These choices appropriately address the supplied group-analysis task in principle.

The primary conclusion is **no support for a positive gain effect in the defined vmPFC sphere under whole-brain correction**. The report gives an ROI peak t=1.33, adjusted p=0.9999, and a descriptive ROI mean of -0.010 (95% t interval -0.039 to 0.018); those values do not support the hypothesized increase and do not establish a true zero effect. It reports 160 corrected positive voxels at posterior locations outside the target region.

However, `results/analyze.py` allocates `N_PERM + 1` max-statistic entries, sets index 0 to the observed statistic, and loops only while `idx < N_PERM`. With `N_PERM=9999`, the loop fills only through index 9998, leaving the final entry uninitialized while the code uses the full array for FWE p-values and quantiles. Thus the exact corrected p-values, reported whole-brain significant voxel count and null quantiles are not reliable as written. The reported vmPFC statistic is far below a plausible whole-brain threshold, so the negative support conclusion remains credible but qualified; the precise correction and map should be regenerated after fixing the defect.

Other limits are accurately described: these are unthresholded participant contrast estimates rather than standardized statistics; the upstream gain modulator was normalized and cannot be read as BOLD change per currency unit; gain and loss were modeled separately; participant variance maps and the upstream time-series pipeline are absent. The supplied report says there were no exclusions. The task’s stated cohort and group label are used as given; no treatment assignment was inferred or reported.

## Retrieval and replay record

**Access check.** Intended recipient: a researcher using the object’s declared authorized routes. The input route in `input/sources.json` is direct HTTPS retrieval from NeuroVault; all 54 maps (96,387,264 bytes) were fetched from this assessment host and matched their recorded byte counts and SHA256 hashes. The Git remote `https://github.com/leej3/stamped-ai-research-next.git` responded, but `git fetch --depth=1` of the assessed commit returned `not our ref`; the declared `con-hub` annex route did not provide content to the runner’s fresh clone. Required coverage is the complete object: code, environment, metadata, 54 inputs, and derived results. Only the input-map component was independently verified from its recorded route. Host scope is this assessment host; this does not establish access from another host or anonymous-access requirements. See [retrieval check](2026-10-15-retrieval-check.json) and [fresh replay record](2026-10-15-fresh-rerun.json).

**Replay.** One authorized attempt used a separate clone of the exact local result commit, explicit entry `python results/analyze.py` (the report names this script but does not provide the command), output comparisons, and the supplied limits. DataLad cloning succeeded, but fetching annex payloads failed (`file not available`), so the entrypoint did not run and no reproduction conclusion can be drawn. Shipped output comparisons also lacked valid baselines for unavailable annexed files. The retained clone/workdir and exact tool record are under the output directory.

**Worker attribution.** The external worker-end-state receipt is SHA256 `750089284731769071ca85fe379a7934341cfde0c9f17b166e8bca0cbb921ddf`; it records worker HEAD `b775bd5baba9e59ba5a9167d53215f4925818788`, exit code 0, a modified `pixi.toml`, and untracked `results/` and `logs/` artifacts at stop. The retained scientific files match the receipt inventory: all 40 regular-file hashes and 54 input annex symlink targets checked matched. The current assessment commit `1b95e0986da9f298eed2b16f73b48a703fe3b1fd` was added afterward by the coordinator and earns no worker tracking credit. See [worker inventory comparison](2026-10-15-worker-inventory-check.json).

## Goals, kind and assumptions

The goal is the one in `input/study-task.md`: test a positive parametric gain effect in vmPFC for the supplied equal-indifference cohort using group analysis of the fixed 54 participant maps, with whole-brain correction. This is a **study** because the product is a scientific answer derived from data and computation. No human was attached to confirm that interpretation; this is the explicit assessment assumption. Study emphasis falls on tracked results and inputs, reproducible execution, portability and access.

## Checklist link and stamp

- [Open the completed checklist](2026-10-15-url.txt)
- Response JSON: [2026-10-15-response.json](2026-10-15-response.json)
- Probe output: [2026-10-15-probes.json](2026-10-15-probes.json)

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, `af259ba`), on the retained repository at commit `1b95e0986da9f298eed2b16f73b48a703fe3b1fd`, 2026-10-15, Codex (API)/GPT-6 (exact model ID unavailable). Scope: committed-state inspection, remote retrieval checks, and one authorized same-host fresh-clone attempt; worker versioning and publication practices attributed from the separately hashed stop receipt. Probe output: `2026-10-15-probes.json`.
