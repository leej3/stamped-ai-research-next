# Working rules

- Add experiment files under `experiments/<name>/`; merge useful changes into the project.
  Worktree checkout paths are host infrastructure, not archived experiment directories.
- Use the root Pixi environment.
  Add missing dependencies with `pixi add`; prefer established scientific libraries and tools over custom implementations.
- Keep `pixi.lock` out of task history.
  Preserve the exact final validated lock on `codex/env-<task>-<run>` with one extra commit off the final task commit; publish the snapshot without merging it into main.
- Give concurrent writers separate prepared worktrees and installed submodules.
  Read selected skills from this checkout, not mutable external copies.
- Duct logging is requested for substantive runs in this study.
  Keep complete command, stream, resource and summary records beside the experiment outputs; retain failures.
  Use annex for large artifacts; verify payload retrieval.
  MechaBABS keeps its native records.
- Credentials stay in host providers.
  Ordinary research logs are intended output; never publish credentials or restricted human data.
- Use Conventional Commits for authored messages and freshly resolved commit-provenance trailers.
  Preserve native DataLad subjects and run records; append attribution without rewriting them.
  Run Snapper on prose.
- Grade with the pinned `assessment/` skill and `pixi run assessment-*` helpers.
  Keep its source and runtime fixed while iterating the workflows in `skills/`.
- Adapt reusable skills when a recurring tool problem is demonstrated.
  Keep skill entrypoints concise, route substantial conditional detail to references, and verify behavior after compression.

Launch workers with `pixi run launch`.
