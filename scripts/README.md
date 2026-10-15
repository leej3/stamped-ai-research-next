# Prepared native launches

The coordinator calls `prepare_launch.py` once per fresh worker.
Prerequisites are Python 3.11+, Git, Pixi, Entire and the bundled Codex CLI, plus a working source manifest/lock and an already approved native hooks file.
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
  --prompt /absolute/task.txt --evidence experiments/my-task/launch \
  --condition baseline
```

The default time bound is 240 seconds; use `--seconds` for the authorized task.
Worktrees are created with Git at `<repo-parent>/<repo-name>-worktrees/<branch>`; use a fresh branch for each worker.
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
