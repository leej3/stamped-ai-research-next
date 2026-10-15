# Coordinator instructions

Follow `prompt.md` with the study brief selected by the user.
Use these rules to organize the run; give research workers their study task and common resource guidance without the coordinator's development history.

- Prepare one common starting state for matched workers, with the study inputs, execution resources and installed submodules.
  Use fresh contexts and separate worktrees; exclude earlier workers' results and judgments from their starting files.
  Shared Git objects and refs can expose other work, so separate directories alone do not establish blinding.
- Let research workers populate `experiments/<run>/` with their efforts.
  Keep each run's assessments, complete requested duct records and environment references beside its outputs; retain failed attempts.
  Keep reusable guidance in skills and study specifications in `studies/`.
  Worktree paths are host infrastructure, not archived experiment directories.
- Each experiment owns its Pixi environment and may evolve its worktree's root `pixi.toml`.
  Add missing dependencies with `pixi add`; reuse established scientific software.
  On merge, preserve differing requirements as named environments and select them explicitly in experiment tasks.
- Keep working `pixi.lock` files ignored.
  Preserve the exact final validated lock on `codex/env-<task>-<run>`, one commit above the final task commit; publish that snapshot without merging it into main.
- Use `pixi run launch` with an explicit clean starting ref and `pixi run judge` with an exact result commit; see [launch commands](scripts/README.md).
  Judges work in fresh sessions using the pinned `assessment/` source and runtime, a fixed prompt and the same replay scope.
  The coordinator compares their findings and does not supply grades to them.
- Keep `skills/` pinned to the tested commit on our clearly named `con/skills` development branch; change it only between rounds.
  Improve and compress the skills from observed problems and useful practices; keep study answers out of generic guidance.
  Keep the assessor fixed throughout the comparison.
- Retain code, inputs, results and execution evidence; use annex for large artifacts and verify independent retrieval.
  Keep requested duct command metadata, stdout/stderr, resource data and summaries in the run they document; MechaBABS uses its native records.
  Credentials remain with host providers; do not publish credentials or restricted human data.
- Use Conventional Commits and freshly resolved provenance trailers for authored commits.
  Preserve native DataLad subjects and run records, appending attribution without rewriting them.
  Run Snapper on authored prose.
