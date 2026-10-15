# Prepared native launches

The coordinator calls `prepare_launch.py` once per fresh worker.
Prerequisites are Python 3.11+, Git, wt-utils, Pixi, Entire and the bundled Codex CLI, plus a working source manifest/lock and an already approved native hooks file.
Credentials remain with the existing host providers.

One-time host defaults live outside the project at `~/.config/stamped-ai-research-next/launch.json` (override with `--host-config`).
The JSON keys are `repo`, `env_manifest`, `approved_hooks`, `trust_sync`, `resolver`, `checkpoint_repo`, `cli`, `codex_home`, `model`, `effort`, `annex_remote`, `annex_git_url` and `annex_url`.
Paths are absolute.
The resolver is the approved fresh per-turn provenance command; the trust helper must reject changed hooks and explicit denials.
For this project, `checkpoint_repo` is `leej3/stamped-ai-research-next`, remote name is `con-hub`, Git URL is `https://hub.centerforopenneuroscience.org/leej3/stamped-ai-research-next.git` and annex URL is `annex+https://hub.centerforopenneuroscience.org:443/git-annex-p2phttp`.
No tokens or credential contents belong in this file or project.

Create an isolated profile once with `create_public_profile.py --profile ABS --source-home ABS --approved-hooks ABS --receipt ABS`.
It references the existing host auth file through a symlink without reading it, copies only already approved source-hook records, and excludes discovered host skills.
The launcher additionally audits effective prompt visibility before executing.
Both study conditions share this profile; only the declared STAMPED entrypoints differ.
Common project resource skills remain available.

```sh
pixi run launch --branch codex/my-task \
  --base WORKER_START_REF \
  --prompt /absolute/task.txt --evidence experiments/my-task/launch \
  --condition baseline
```

Launch tasks explicitly select `gpt-6-luna` with high effort; record any deliberate override and keep it fixed across the comparison.
There is no hard cutoff by default (`--seconds 0`).
At 90 minutes, `--review-seconds 5400` emits `review.json` for the supervisor without stopping productive work.
An explicit nonzero `--seconds` remains available for bounded setup probes.
The worker gets its own locked Pixi environment and initialized annex remote; setup does not download all artifacts.
`--prepare-only` verifies effective skill exposure and stops before native execution.
A new clone additionally needs `--kind clone --clone-path ABS`.
Unknown hook changes or mismatched manifests, locks or remotes stop setup.

`prepare_checkout.py --provenance-only` installs only the fresh commit hook in an existing replay fixture.
It requires `--checkout`, `--resolver`, and a new `--receipt` path.
DataLad run commits retain their native `[DATALAD RUNCMD]` subject and record, with fresh provenance appended.
Ordinary authored commits use Conventional Commits; native `datalad rerun` needs no adapter for new runs.

Git hooks prefer `scripts/commit_provenance_hook.py` from the current checkout, falling back to the stable checkout that installed them.
After integrating these scripts, rerun preparation from the stable main checkout so fallback paths do not depend on a temporary implementation worktree.
Hook trust does not automatically follow branches, clones or paths: native preparation and a real capture check are required before work.
Bulk checkpoint pushing remains disabled; review and publish exact refs separately.

The stable root's seven byte-identical native hooks were trusted separately in both the normal Desktop profile and the isolated worker profile.
A fresh Desktop coordinator session can therefore load those approvals; an existing session must not be assumed to reload them.
Normal Desktop global instructions are unchanged.
Only isolated worker launches were tested for the clean public prompt boundary.
Capture checks and publication remain distinct operations.

## Independent judges

```sh
pixi run judge --branch codex/judge-001 --base RESULT_COMMIT \
  --evidence experiments/judgments/001
```

The coordinator resolves the target to a commit and renders `judge-prompt.md`; only that commit varies in the template.
Do not pass an arm label or custom prompt.
Use neutral result refs where practical and document residual identifiers that reveal condition.
Each invocation starts a fresh session and advertises only the frozen assessor and conventions from the STAMPED bundle, plus common resource guidance.
Assessment source checks use the coordinator's pin, and assessment helpers run outside the target in their recorded environment.
The target's environment is evaluated through replay, without changing its dependency declarations or lock before inspection.
Reports are written outside the target to `native/judgment/` beside `prompt.txt`, `events.jsonl`, `stderr.txt`, `launch.json` and `result.json`.
Preserve duplicate judgments independently; never select the more favorable result.

`pixi run launcher-tests` exercises role separation, pin failures and timing with fake subprocesses; it does not demonstrate a real judge session.
Before scored rounds, verify one real judge capture and its complete assessment outputs.

## Worker visibility

Prepare a minimal starting ref containing the common task, data pointers and execution resources; update only treatment skill pins between rounds.
An explicit `--base` prevents accidentally choosing the accumulating default branch, but does not itself prove isolation.
Worktrees share repository objects/refs, and a container can still expose other runs through mounted Git directories.
For stronger separation, the existing YOLO worker-container approach can mount a single-branch clone, inputs and narrowly scoped host services with separate writable session state.
Verify that layout before adopting it; containerized scientific software alone does not isolate the research agent.
