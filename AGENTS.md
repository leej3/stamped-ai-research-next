# Coordinator instructions

Follow `prompt.md` to iterate on reusable skills using the study submodules selected by the user.
The unit of iteration is a pinned skill revision; study-specific preparation and findings stay in their submodules.

- Record each iteration under `iterations/<iteration>/`: skill revision, exact study/input revisions, linked worker branches and judgments, comparisons, and the rationale and outcome of skill changes.
  Keep these coordinator records outside worker inputs.
- Give research workers only the study's committed `input/`, common resources and their assigned skills.
  Use `pixi run launch` to create independent repositories without coordinator history, references or prior results; separate worktrees alone share Git objects.
  Keep coding tasks in their own worktrees.
- Let workers populate `results/<run>/` in their research repositories.
  Integrate their efforts and judgments into the selected study's `results/<run>/`; retain complete worker branches and failed attempts.
  Keep generic guidance in `skills/` and evaluation references outside worker inputs.
- Each experiment owns its Pixi environment and may evolve its repository's root `pixi.toml`.
  Add missing dependencies with `pixi add`; reuse established scientific software.
  On integration, preserve differing requirements as named environments in the study's root manifest and select them explicitly in experiment tasks.
- Keep working `pixi.lock` files ignored.
  Preserve the exact final validated lock on `codex/env-<task>-<run>`, one commit above the final task commit; publish that snapshot without merging it into main.
- Launch matched workers from the same coordinator revision and study input package.
  Use `pixi run judge` with an exact result commit and the external frozen assessor; see [launch commands](scripts/README.md).
  Give judges the same scientific evaluation guidance without condition labels or coordinator grades.
  Keep assessment source, runtime, prompt and settings fixed throughout the comparison.
- Keep `skills/` pinned to the tested commit on our clearly named `con/skills` development branch; change it only between iterations.
  Improve and compress skills from observed problems and useful practices; keep study answers out of generic guidance.
- Retain code, inputs, results and execution evidence; annex large artifacts and verify independent retrieval.
  Publish study and skill commits and required annex payloads before updating their parent gitlinks.
  Keep requested duct metadata, stdout/stderr, resource data and summaries with the run; MechaBABS uses its native records.
  Credentials remain with host providers; do not publish credentials or restricted human data.
- Use Conventional Commits and freshly resolved provenance trailers for authored commits.
  Preserve native DataLad subjects and run records, appending attribution without rewriting them.
  Run Snapper on authored prose.
