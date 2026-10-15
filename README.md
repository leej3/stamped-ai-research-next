# STAMPED research with agents

A study of whether iteratively improved STAMPED skills improve research outcomes and reduce variation between agents.
[prompt.md](prompt.md) directs the development loop; [study.md](study.md) fixes the common MRI task: reproduce NARPS Figure 2.
[AGENTS.md](AGENTS.md) defines the project conventions.
The products are improved skills, assessment examples and a complete STAMPED research object for a later poster.

Add experiments under `experiments/` and dependencies to the root `pixi.toml`.
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

Execution evidence: [native DataLad replay](experiments/datalad-native/README.md), [independent workflow trial](experiments/skill-bundle/blind-001/README.md), and [frozen assessment](experiments/assessment-v1/README.md).

Research workers start from a minimal prepared ref, not this accumulating coordinator checkout.
Three fresh workers per condition run the same task in each of three rounds.
`pixi run judge` dispatches independent judges with a fixed prompt and replay scope, following [issue #2](https://github.com/leej3/stamped-ai-research-next/issues/2).
Selected outputs receive duplicate judgments to measure judge disagreement.

The MRI task supplies evidence for the [demonstration table](https://github.com/con/cierge/issues/52):

| Property | Evidence to collect |
| --- | --- |
| Self-containment | Explicit object boundary; retrievable data, code and outputs through DataLad/annex |
| Tracking | Git revisions, native DataLad run records, module-local duct logs and session capture |
| Actionability | Named Pixi tasks for execution, verification and figures |
| Modularity | Independently pinned data, container and skill components |
| Portability | Pinned MRI container, preferably ReproNim/Apptainer, with a demonstrated replay |
| Ephemerality | Fresh worker context and clean execution; record Slurm jobs if used |
| Distributability | Published Git state and annex payloads verified by independent retrieval |

This map-analysis task does not exercise raw-data BIDS App preprocessing or MechaBABS.
NIDM/PROV export is also untested; these are coverage limits, not demonstrated features.
Source metadata and the publication's analysis revision have been verified; payload retrieval, the execution-image pin and a timed scientific rehearsal remain to be completed before scored rounds.
