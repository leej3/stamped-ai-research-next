# Launch research workers and judges

The native launcher uses host settings from `~/.config/stamped-ai-research-next/launch.json`; `--host-config` selects another file.
These identify the CLI, source environment, approved hooks, provenance resolver and annex remote.
Credentials stay with host providers.
Use [resource readiness checks](READINESS.md) for the requirements supplied by this user; retain their result before launching research.

## Research workers

Initialize only the selected study, leaving its experiment submodules absent:

```sh
pixi run git submodule update --init -- studies/CHOSEN_STUDY
```

```sh
pixi run launch --study studies/CHOSEN_STUDY \
  --base COORDINATOR_COMMIT --branch codex/run-001 \
  --evidence /path/to/run-evidence/run-001/launch \
  --condition baseline
```

Select `baseline`, `discover-general`, `discover-science` or `stamped-explicit` with `--condition`.
The legacy `skills` value retains the earlier explicit treatment for existing records.
Add `--capture-execution` when duct logging is requested, including runs explicitly following the workshop prompt.
The explicit coordinator revision selects the study and skill gitlinks and common Pixi manifest.
Its `conditions.json` supplies the exact added instruction, retained with its hash in the worker's input receipt.
A study marked unavailable in its pinned `coordinator-guidance/readiness.json` stops before worker creation and reports the missing prerequisite.
The launcher copies only committed study inputs and shared environment declarations into a parentless, independent repository.
It records source revisions, blob identities and annex keys without importing coordinator or study history.
Baseline and discovery repositories start without supplied research skill files; explicit STAMPED repositories install the pinned skills submodule without its optional evaluation fixtures.

All conditions receive the same scientific prompt and common resources.
Discovery conditions ask agents to search for and install skills; availability alone is not discovery or evidence of use.
Retain unsuccessful attempts and distinguish assigned condition from observed behavior, including spontaneous discovery in baseline runs.
Each launch uses a separate native profile; task-local skill installations must not change another run's catalog.
Use retained transcripts and installed artifacts to establish searches, choices, source revisions, loading and application; an installed file alone does not establish use.
Coordinator-only Pixi tasks are removed from the worker manifest.
Workers can add dependencies and actionable tasks; each experiment retains its own root manifest.
Keep the evidence directory outside the worker checkout.
`--clone-path ABS` chooses its location; research launches reject `--kind worktree` because it would share excluded Git objects.

## Independent judges

```sh
pixi run judge --repo /absolute/path/to/worker-repository \
  --base RESULT_COMMIT --branch codex/judge-001 \
  --study studies/CHOSEN_STUDY \
  --reference studies/CHOSEN_STUDY/coordinator-guidance/judging.md \
  --evidence /path/to/run-evidence/run-001/judgment-01
```

Use the same study revision and evaluation guidance for matched judgments.
The launcher retains the scientific prompt and optional reference guidance with their hashes, independently of the submitted object.
Judges use the coordinator's frozen assessor and runtime outside the target; the target need not contain assessment tools.
A separate host profile makes the frozen judging skills discoverable without adding files to the assessed checkout.
The clone retains the result commit and its annex metadata, without other trial branches.
They inspect and replay the object's declared environment without repairing it first.
Keep duplicate judgments independently and use neutral result identifiers where practical.

## Retaining experiments

Preserve the exact scientific `RESULT_COMMIT` used for judging.
After research and judging, add launch and judging receipts to the experiment repository in a later commit that records that result identity.
Publish its branch and annex payloads, then register the final commit as `results/<run>` in the study's `.gitmodules` and Git index.
Registration does not require a checkout:

```sh
mkdir -p studies/CHOSEN_STUDY/results/run-001
pixi run git -C studies/CHOSEN_STUDY config -f .gitmodules submodule.results/run-001.path results/run-001
pixi run git -C studies/CHOSEN_STUDY config -f .gitmodules submodule.results/run-001.url PUBLISHED_REPOSITORY_URL
pixi run git -C studies/CHOSEN_STUDY update-index --add --cacheinfo 160000,PUBLISHED_COMMIT,results/run-001
pixi run git -C studies/CHOSEN_STUDY add .gitmodules
```

Commit and publish the study before updating its coordinator gitlink.
Initialize individual experiments when inspecting or replaying them; leave other experiments absent.
Fetch annex content separately as needed.

## Timing and checks

Pixi tasks select Luna with high reasoning effort; keep deliberate overrides fixed across the comparison.
There is no hard cutoff by default (`--seconds 0`).
At 90 minutes, `--review-seconds 5400` emits a review receipt without terminating useful work.
A nonzero `--seconds` requests an explicit limit.

The launcher retains prompts, source identities, hook preparation and native session streams, including stderr.
`--prepare-only` checks setup and effective skill exposure without executing the task.
Automatic `AGENTS.md` loading is disabled for workers and judges; effective-prompt checks reject injected project instructions.
See [Codex project instruction discovery](https://learn.chatgpt.com/docs/config-file/config-advanced#project-instructions-discovery).

`pixi run launcher-tests` checks input isolation, role separation, judging inputs, timing and response-helper forwarding with fixtures.
These checks do not establish scientific validity, workload timing or live judge performance.
