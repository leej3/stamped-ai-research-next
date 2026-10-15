# STAMPED research with agents

A prepared repository for comparing research agents with and without STAMPED guidance.
[prompt.md](prompt.md) defines the study; [AGENTS.md](AGENTS.md) defines the project conventions.

Add experiments under `experiments/`; each owns its Pixi environment and evolves its worktree's root `pixi.toml` as needed.
The coordinator preserves requirements that differ from the default as named environments on merge.
Concurrent agents use prepared external worktrees with installed submodules.
Git stores source and metadata; git-annex stores larger artifacts and execution records on [CON Hub](https://hub.centerforopenneuroscience.org/leej3/stamped-ai-research-next).

Run `pixi task list` for available commands.
`pixi run launch --help` describes worker launches; [host configuration](scripts/README.md) supplies the existing machine-specific paths.
Working locks stay ignored; preserve the exact validated lock on a separate snapshot commit above the final task commit.

`skills/` blends [PR26](https://github.com/con/skills/pull/26) with lessons from the first trial on [our own branch](https://github.com/con/skills/tree/codex/pr26-stamped-next).
The core STAMPED workflows are tool-neutral.
Project-specific environment guidance is in [pixi-with-stamped](skills/skills/pixi-with-stamped/SKILL.md).
[assessment-version.json](assessment-version.json) pins the assessor and its environment independently.
`pixi run assessment-check` verifies both; `assessment-probes` collects a draft and `assessment-validate` checks the completed response.

Execution trials and their complete records are retained under `experiments/`.
They establish the tested execution routes, not scientific or skill efficacy.

Execution evidence: [DataLad reassessment and replay](experiments/datalad-native/README.md), [independent workflow trial](experiments/skill-bundle/blind-001/README.md), and [frozen assessment](experiments/assessment-v1/README.md).
