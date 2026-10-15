# Final repository boundary

Build `leej3/stamped-in-practice` from the latest tested, committed tree in `/Users/johnlee/.local/share/wt-utils/worktrees/776c/stamped-ai-research-next`.
The observed candidate on 2026-10-15 is `4a0795d3d357691cb8a536f566bf2059f7759b21`; the formal native profile fix and end-to-end preparation check are still pending.
Select the final source SHA after those pass.
The primary checkout and its local `main` are stale.

Use a shallow checkout as the source, then make one parentless initial commit with the source repository and exact source SHA in its provenance.
Preserve source history in `stamped-ai-research-next`.

## Carry

- `AGENTS.md`, `README.md`, `prompt.md`, `judge-prompt.md`, `comparison-plan.md`, `conditions.json`, `assessment-version.json`, and `pixi.toml`.
- `scripts/` and `tests/`, including the final native capture verification fix.
- `.gitignore`, `.gitattributes`, `.gitmodules`, `.pre-commit-config.yaml`, `.agents/skills/` relative links, `.codex/hooks.json`, `.entire/.gitignore`, and `.datalad/.gitattributes`.
- `assets/workbench.png`, which the README displays.
- These three gitlinks and their declared source URLs:

| Path | Commit | Source |
| --- | --- | --- |
| `skills` | `0208f82504f15b82b7582f34143ab889dd52c68d` | `https://github.com/con/skills.git` |
| `assessment` | `0208f82504f15b82b7582f34143ab889dd52c68d` | `https://github.com/con/skills.git` |
| `studies/narps` | `6758fe683b447834d29df954b6be6ea07f6b20f1` | `https://github.com/leej3/stamped-ai-research-next.git` |

NARPS remains the first formal study.
Keep its existing study branch/source; initialize only selected input and assessment dependencies.
Do not recursively initialize historical results or optional `evals`, or bulk-retrieve annex data.
The study gitlink retains historical preparation by identity without copying its payloads into the new root or judge inputs.
Judges receive only the chosen rubric, reference, and explicitly declared guidance dependencies.

## Leave in the source repository

Exclude all existing root `iterations/` records, including the preparation seal and failed trials.
Create a new formal registration and requirements file after choosing the final root.
Exclude `.git`, `.pixi`, working `pixi.lock`, `.local`, host profiles, credentials, generated hooks, local Entire settings, and captured sessions.
Create a new DataLad dataset identity instead of copying the source `.datalad/config` UUID.

## Required bindings before commands can work

1. Configure the new origin/push URL as `git@github.com:leej3/stamped-in-practice.git`; worker seeding requires an SSH GitHub push remote.
   Prepare a new explicit host launch configuration, or `~/.config/stamped-in-practice/launch.json`.
   Its checkpoint destination, environment manifest, profile and annex routes must be intentionally selected; the old host configuration is not a portable project file.
2. Keep the assessor pin's `environment_repository` pointing to `https://github.com/leej3/stamped-ai-research-next.git`.
   It supplies runtime commit `3552d5003a2485b6405805236d5c54e7ed42f097` and its pinned manifest/lock hashes.
   `assessment-check` retrieves this missing object from that explicit repository, independent of the new origin.
   Run it before sealing, which reads the runtime object locally.
   The selected skills, study, runtime and required annex keys must remain remotely readable; this inspection did not test remote retrieval.
3. Preserve or deliberately update the Pixi workspace name before producing the final common starting-environment snapshot.
   Any manifest edit requires a matching lock/snapshot.
   Keep that snapshot as a separate immutable record, and regenerate readiness and the formal procedure seal against the new coordinator commit.
   The source preparation seal cannot survive the parentless history boundary.

The remaining implementation blocker is the reported native profile digest failure when checkout preparation adds approved project trust.
After its fix, the final source still needs the end-to-end preparation check.
No scientific results were inspected and no research was run for this boundary review.
