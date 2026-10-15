# Launch research workers and judges

The native launcher uses host settings from `~/.config/stamped-ai-research-next/launch.json`; `--host-config` selects another file.
These identify the CLI, source environment, approved hooks, provenance resolver and annex remote.
Credentials stay with host providers.

## Research workers

```sh
pixi run launch --study studies/narps-gain-consistency \
  --base COORDINATOR_COMMIT --branch codex/run-001 \
  --evidence studies/narps-gain-consistency/experiments/run-001/launch \
  --condition baseline
```

Use `--condition skills` for the treatment.
The explicit coordinator revision selects the study and skill gitlinks and common Pixi manifest.
The launcher copies only committed study inputs and shared environment declarations into a parentless, independent repository.
It records source revisions, blob identities and annex keys without importing coordinator or study history.
Baseline repositories contain no research skill files; treatment repositories install the pinned skills submodule.

Both conditions receive the same scientific prompt and common resources.
Coordinator-only Pixi tasks are removed from the worker manifest.
Workers can add dependencies and actionable tasks; the coordinator integrates differing requirements as named environments in the study.
Keep the evidence directory outside the worker checkout.
`--clone-path ABS` chooses its location; research launches reject `--kind worktree` because it would share excluded Git objects.

## Independent judges

```sh
pixi run judge --repo /absolute/path/to/worker-repository \
  --base RESULT_COMMIT --branch codex/judge-001 \
  --study studies/narps-gain-consistency \
  --reference studies/narps-gain-consistency/reference/judging.md \
  --evidence studies/narps-gain-consistency/experiments/run-001/judgment-01
```

Use the same study revision and evaluation guidance for matched judgments.
The launcher retains the scientific prompt and optional reference guidance with their hashes, independently of the submitted object.
Judges use the coordinator's frozen assessor and runtime outside the target; the target need not contain assessment tools.
A separate host profile makes the frozen judging skills discoverable without adding files to the assessed checkout.
The clone retains the result commit and its annex metadata, without other trial branches.
They inspect and replay the object's declared environment without repairing it first.
Keep duplicate judgments independently and use neutral result identifiers where practical.

## Timing and checks

Pixi tasks select Luna with high reasoning effort; keep deliberate overrides fixed across the comparison.
There is no hard cutoff by default (`--seconds 0`).
At 90 minutes, `--review-seconds 5400` emits a review receipt without terminating useful work.
A nonzero `--seconds` requests an explicit limit.

The launcher retains prompts, source identities, hook preparation and native session streams, including stderr.
`--prepare-only` checks setup and effective skill exposure without executing the task.
Automatic `AGENTS.md` loading is disabled for workers and judges; effective-prompt checks reject injected project instructions.
See [Codex project instruction discovery](https://learn.chatgpt.com/docs/config-file/config-advanced#project-instructions-discovery).

`pixi run launcher-tests` checks input isolation, role separation, judging inputs and timing with fixtures.
These checks do not establish scientific validity, workload timing or live judge performance.
