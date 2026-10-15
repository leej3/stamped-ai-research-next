# Launch research workers and judges

Use the prepared native Codex profile and host settings in `~/.config/stamped-ai-research-next/launch.json` (`--host-config` overrides that path).
The settings identify the repository, source environment, CLI, approved hooks, provenance resolver and annex remote; credentials stay with host providers.
The launcher uses Git directly to create a fresh branch/worktree, initializes submodules and annex, and checks hook trust and the effective prompt before execution.

## Research workers

```sh
pixi run launch --branch codex/run-001 --base WORKER_START_REF \
  --prompt studies/study-narps-figure2.md \
  --evidence experiments/run-001/launch --condition baseline
```

Use `--condition skills` for the treatment, with the selected skills pinned in its starting ref.
Both conditions receive the same scientific brief and common resource guidance.
Workers have separate Pixi installations with the initial matched manifest and lock; their requirements may evolve during research.
The coordinator integrates differences as named environments on merge.

The explicit starting ref must contain the common study inputs and operational resources without earlier experiments, judgments or coordinator instructions.
Worktrees share Git objects and refs; this layout is not a security boundary against reading other history.
Automatic `AGENTS.md` loading is disabled for workers and judges, and effective-prompt checks reject injected project instructions.
For the control setting, see [Codex project instruction discovery](https://learn.chatgpt.com/docs/config-file/config-advanced#project-instructions-discovery).

## Independent judges

```sh
pixi run judge --branch codex/judge-001 --base RESULT_COMMIT \
  --study studies/study-narps-figure2.md \
  --evidence experiments/run-001/judgment-01
```

Supply the same frozen scientific brief used for the workers from the coordinator's checkout, independently of the target being judged.
The launcher retains its exact bytes and hash and includes it in the fixed judging prompt.
Judge sessions expose the frozen assessor and conventions; assessment helpers run outside the target in their recorded environment.
They inspect the object's environment through authorized replay without repairing its declarations first.
Reports and execution records stay outside the target under the supplied evidence directory.
Keep duplicate judgments independently and use neutral result identifiers where practical.

## Timing and records

The Pixi tasks select Luna with high reasoning effort; keep any deliberate override fixed across the comparison.
There is no hard cutoff by default (`--seconds 0`).
At 90 minutes, `--review-seconds 5400` emits a review receipt without terminating the worker.
Use a nonzero `--seconds` only for an explicitly bounded run.

The launcher retains the prompt, starting commit, environment identity, hook preparation and native session streams, including stderr.
When duct is requested, capture the launch once and keep its complete records with the run.
`--prepare-only` checks setup and effective skill exposure without executing the task.
`--kind clone --clone-path ABS` prepares an independent checkout; it does not itself remove shared history from the clone.

`pixi run launcher-tests` checks role separation, judging inputs and timing with fixtures.
Prompt previews check instruction exposure; a live judge and scientific replay remain separate checks before scored rounds.
