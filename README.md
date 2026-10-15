# Improving STAMPED research skills

This repository tests whether STAMPED guidance helps research agents answer scientific questions with sound methods and more thorough, efficient and consistent reproducibility.
Fresh agents tackle the same question with and without the skills.
Independent judges assess the science and reproducibility separately; the coordinator uses their findings to improve the research skills between rounds.
STAMPED provides a vocabulary for describing and evaluating these practices.

The broader hypothesis concerns both humans and agents; this experiment tests agents.
Repeated baseline runs help distinguish improvements from ordinary variability.
Results from one study do not establish transfer to other studies.

To start a coordinator, give it this repository and a request such as:

> Follow `prompt.md` using `studies/narps-gain-consistency`.

| Location | Purpose |
| --- | --- |
| `prompt.md` | The research, assessment and skill-improvement loop |
| `AGENTS.md` | Instructions for the coordinator |
| `studies/<study>/` | A versioned study submodule |
| `studies/<study>/input/` | The scientific prompt and verified data supplied to research workers |
| `studies/<study>/reference/` | Evaluation guidance and reference material for the coordinator and judges |
| `studies/<study>/experiments/` | Workers' efforts, returned outputs, assessments and execution records |
| `skills/` | Evolving `con/skills`, pinned to [our development branch](https://github.com/con/skills/tree/codex/pr26-stamped-next) |
| `assessment/` | The frozen assessor, identified by `assessment-version.json` |

The products are improved shareable skills and a complete research record, with figures showing scientific outcomes, reproducibility, costs and limitations.
New study submodules can reuse the same process.
Poster production follows separately.
