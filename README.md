# Improving STAMPED research skills

This repository is a workshop for improving STAMPED research skills.
It runs scientific studies with and without the evolving skills, evaluates the resulting research objects using a frozen assessment, and uses that evidence to revise the skills.
The question is whether the guidance helps agents do sound science with more thorough, efficient and consistent reproducibility.

Each iteration tests a pinned skill revision on selected studies: run matched agents, assess their work independently, compare outcomes and effort, then improve and compress the reusable guidance.
Study inputs and scientific outputs belong to study submodules; root iteration records connect that work to changes in the skills.

The broader hypothesis concerns both humans and agents; this experiment tests agents.
Repeated baseline runs help distinguish improvements from ordinary variability.
Results from one study do not establish transfer to other studies.

To start a coordinator, give it this repository and a request such as:

> Follow `prompt.md` using `studies/<chosen-study>`.

| Location | Purpose |
| --- | --- |
| `prompt.md` | The research, assessment and skill-improvement loop |
| `AGENTS.md` | Instructions for the coordinator |
| `iterations/<iteration>/` | Skill revisions, linked trials and assessments, comparisons and reasons for changes |
| `studies/<study>/` | A versioned study submodule |
| `studies/<study>/input/` | The scientific prompt and verified data supplied to research workers |
| `studies/<study>/coordinator-guidance/` | Evaluation guidance and reference material for the coordinator and judges |
| `studies/<study>/results/` | Workers' efforts, returned outputs, assessments and execution records |
| `skills/` | Evolving `con/skills`, pinned to [our development branch](https://github.com/con/skills/tree/codex/pr26-stamped-next) |
| `assessment/` | The frozen assessor, identified by `assessment-version.json` |

The products are improved shareable skills, evidence about their impact, and a STAMPED research object documenting the whole workshop.
Figures summarize scientific outcomes, reproducibility, effort and variability.
