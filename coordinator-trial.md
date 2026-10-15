# Coordinator preparation trial: NARPS

Date: 2026-10-15  
Scope: coordinator preparation only; no formal research or assessment was run.

## Result and boundaries

The selected first formal study is `studies/narps`, checked out at `6758fe683b447834d29df954b6be6ea07f6b20f1`.
Only that study submodule was initialized.
The skills and assessment submodules remain uninitialized; initialize them before freezing and launching round one.
The study guidance marks the input package ready and records earlier validation of 54 AO86 participant maps (96,387,264 bytes), with common geometry and matching checksums.
Its preparation records also report publication to `con-hub` and independent retrieval.
These are prior, pinned study records, not fresh checks of this checkout or the current host.

The worker question is whether potential monetary gain has a positive parametric effect on vmPFC response in the NARPS equal-indifference group, conditional on the fixed AO86 participant maps.
Use whole-brain corrected inference and justify the vmPFC definition.
The supplied maps are participant effect estimates, not standardized statistics; the upstream analysis is fixed and participant variance maps are absent.
Workers may choose defensible group methods and visualizations.
Prior team answers and preparation pilot outputs stay outside worker inputs.
NARPS is intentionally compact: its guidance reports roughly five-to-six-minute preparation pilots and does not require a minimum compute duration.
Do not lengthen the task to meet a duration target.

No experiment results, iteration records, old Git history, other conversations, or personal memory were consulted.
No worker or judge was launched, no cluster job was submitted, and nothing was published.
A read-only `entire checkpoint explain --commit HEAD --json` after the documentation commit found a local checkpoint with one Codex session and exactly `coordinator-trial.md` in `files_touched`.
This establishes capture for this coordinator edit only.
Live input verification, worker-profile capture, annex write/retrieval, and HPC checks remain unperformed.

## Fixed for the formal comparison

Use the pinned NARPS input and scientific question in all rounds; keep prior answers, coordinator guidance, and pilot material out of worker inputs.
Keep common resources, tools, network access, model/settings, budgets, prompts, and assessment protocol matched across conditions.
Follow the repository defaults unless they are formally resolved before round one:

- Three iterations, three independent workers in each of four conditions per iteration: `baseline`, `discover-general`, `discover-science`, `stamped-explicit` (36 assigned worker runs total).
- Luna, high reasoning effort, with the exact model identifier retained from each launch receipt.
  The repository's `pixi run launch` task explicitly selects Luna/high. The supplied `launch.json` says Astra/ultra; do not override the repository task silently.
  Resolve this discrepancy before the first launch if the host requires Astra/ultra.
- Duct execution capture on each scientific worker run (`--capture-execution`), as required by `prompt.md`.
- Fresh workers with the same committed input package and no coordinator history or previous work.
  Preserve condition assignment separately from observed discovery, use, and failed attempts.
- The assessor source, runtime, judging prompt/settings, and replay scope fixed before the first worker.
  Use the exact assessor pin in `assessment-version.json`; validate its source and environment before judging.
- Judge every committed research object independently.
  Before launching, record a random seed for permuting launch order and randomly preselect one object per condition for a second independent judgment in each round (12 duplicate judgments across three rounds; 48 judgments total).
- Keep scientific adequacy separate from STAMPED item findings; retain `not-checked`, disagreement, individual runs, denominators, effort, operational outcomes, and failures.
  Do not invent an overall score or claim precise variance from three workers per cell.
- Review progress around 90 minutes and allow productive work to finish; use no hard timeout (`--seconds 0`).
  NARPS's short compute time is acceptable.

## May evolve between rounds

Only the pinned reusable skill revision and its internal prompts may be improved between rounds, based on observed results and practices.
Keep study questions, worker inputs, condition definitions, common resources, and assessment fixed.
Record every skill change and whether the next round addresses its motivating issue.
The final round uses the resulting skills without tuning on its results.
Operational changes must be logged; a change to any fixed comparison setting requires a new comparison or a documented resolution before continuing.
Do not generalize conclusions beyond this study and its exploratory sample.

## Open gates and missing decisions

1. **Entire capture:** the current coordinator session produced a local checkpoint for this edit, verified with `entire checkpoint explain --commit HEAD --json`; metadata listed one Codex session and exactly `coordinator-trial.md`.
   This is evidence for coordinator capture, not for the separately prepared worker profile.
   `.codex/hooks.json` can exit successfully when the CLI is absent, so verify one non-scientific worker-profile canary and its local checkpoint/session/file event before formal launches.
   Do not publish the canary.
2. **Annex:** the pinned study records earlier `con-hub` publication and fresh-clone retrieval of its inputs.
   Current-host independent retrieval and a safe write/upload round trip have not been checked.
   The task forbids publication during this trial, so upload readiness remains unresolved.
   Before round one, identify an approved, non-scientific canary object or other authorized write check and verify its independent retrieval.
   Keep credentials in existing providers.
3. **HPC:** no scheduler check or job submission was attempted.
   Working HPC access is an explicit host requirement and remains unresolved.
   A read-only account/queue query would show visibility only; a scheduler round trip would demonstrate more but requires an authorized job submission, which this trial forbids.
   Obtain an approved preflight method or authorization before counting this gate as passed.
4. **Readiness configuration:** `~/.config/stamped-ai-research-next/readiness.json` is missing.
   Create it outside the repository with user-approved checks for `entire-capture`, `annex-upload`, `annex-independent-retrieval`, and `hpc-access`.
   The repository's readiness runner executes only those configured commands and retains their receipts; a missing check is unmet, not passed.
   Keep host paths, commands, and credentials out of the repository and receipts.
5. **Current study checkout:** the pinned study guidance says its inputs were verified, but `pixi run verify-input` was not run in this checkout.
   Verify all input files before launch; retrieve missing annex content only from the configured remote and then rerun verification.
6. **Host paths and settings:** `launch.json` selects the Codex CLI, source manifest, hook config, trust sync, provenance resolver, public checkpoint repository, `con-hub` annex endpoints, and a Codex profile.
   Its `repo`, manifest, hooks, and trust-sync paths refer to `/Users/johnlee/code/CON/stamped-ai-research-next`, while this trial checkout is elsewhere.
   The launcher intentionally uses the current checkout as `repo`, but the other configured paths still need to resolve to the intended trusted files and skill revision.
   Do not copy credentials into worker evidence.
   Confirm the effective runtime and profile before the formal freeze.
7. **Round record:** before round one, create the iteration record and requirements file, record the exact coordinator/study/skills/assessor commits, common settings, budget, random seed, launch-order permutation, and duplicate-judgment selections.
   No seed or duplicate sample is invented here.

## First-round execution plan

These are the commands to run after the open gates are resolved.
Keep evidence outside worker checkouts, use fresh run IDs/directories, and stop if any readiness item is unmet.

### 1. Initialize and verify pinned inputs/resources

```sh
git submodule update --init -- studies/narps skills assessment
git -C studies/narps rev-parse HEAD
git -C skills rev-parse HEAD
git -C assessment rev-parse HEAD
(cd studies/narps && pixi run verify-input)
pixi run assessment-check
```

Check the study revision against `6758fe683b447834d29df954b6be6ea07f6b20f1`, skills against the coordinator gitlink `fdf31feecb4ee37a8487188447d61c006b11099f`, and assessor against `assessment-version.json` (`d867c1d04bbb58b3b0f64122ebd5f76bd8e5a7ca`).
Resolve and record any mismatch before continuing.
If input verification fails because annex content is absent, retrieve it using the study's configured annex remote, then rerun verification; do not change the committed input manifest.

### 2. Run configured readiness checks

Create the iteration's requirements JSON from the four user-specified capabilities, with each source attributed to the user prompt.
Configure host-specific check commands in `~/.config/stamped-ai-research-next/readiness.json`; do not put command paths, secrets, or host configuration in Git.
Then run:

```sh
pixi run readiness \
  --requirements iterations/narps-r1/requirements.json \
  --host-config ~/.config/stamped-ai-research-next/readiness.json \
  --evidence /path/outside/repository/narps-r1/readiness-001
```

Read `result.json` and resolve every unmet requirement.
The annex write check must be an approved non-scientific canary.
Do not submit an HPC job under this trial's restrictions; until an authorized method establishes the requested access, leave `hpc-access` unmet.
A readiness pass is only as strong as the configured checks.

### 3. Freeze the comparison and launch 12 workers

Commit the round record before launching.
It must pin the exact coordinator revision, study/input package, skills, assessment, run budget, task/common prompts, model/settings, tools/network, random seed, launch order, duplicate-judgment sample, and review policy.
Use the recorded seed to vary condition order across the 12 launches.
Example command for one assigned worker (repeat for each of three workers per condition, following the recorded order):

```sh
pixi run launch --study studies/narps \
  --base <FROZEN_COORDINATOR_COMMIT> \
  --branch codex/narps-r1-baseline-01 \
  --evidence /path/outside/repository/narps-r1/baseline-01/launch \
  --condition baseline --seconds 0 --review-seconds 5400 \
  --capture-execution
```

Use unique `codex/` branches and evidence directories for every worker.
Change only the branch, evidence path, and assigned condition per run.
The pinned condition prompts in `conditions.json` govern the four assignments.

### 4. Judge and retain

For each worker's exact result commit, launch a fresh independent judge with the same pinned study guidance and assessor.
Use a neutral result ID where practical.
Example:

```sh
pixi run judge --repo <ABSOLUTE_WORKER_REPOSITORY> \
  --base <EXACT_RESULT_COMMIT> --branch codex/narps-r1-judge-01 \
  --study studies/narps \
  --reference studies/narps/coordinator-guidance/judging.md \
  --evidence /path/outside/repository/narps-r1/result-01/judgment-01
```

Run the second independent judgment only for the preselected object in each condition.
Preserve both judgments and report disagreement.
Retain execution and judging receipts after the judged scientific commit, without changing that result identity.
Independently verify annex retrieval and replay evidence for each research object.
Only after formal work, authorized publication, and verification, register each final experiment commit as a submodule under the selected study's `results/<run>` path and update the coordinator gitlink.

## What this trial actually established

The top-level instructions, NARPS task and evaluation guidance, comparison plan, condition prompts, readiness/launcher instructions, pinned study metadata, selected host launcher JSON, and required workflow scripts were inspected. `studies/narps` was initialized at the recorded commit. The host launch configuration file exists; the readiness configuration does not. A local coordinator checkpoint was verified after committing this note, but the worker-profile capture canary, live readiness probe, current input verification, annex upload/retrieval check, scheduler check, worker run, judge run, scientific analysis, publication, and result registration were not performed.
