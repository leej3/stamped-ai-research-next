# Improving STAMPED research skills

This repository studies whether improving reusable STAMPED skills helps research agents produce sound scientific results and better documented, reproducible research objects.
Fresh agents repeat the same study with and without the skills.
Independent judges assess both scientific results and STAMPED evidence using a frozen assessor; the coordinator uses their findings to improve the research skills between rounds.

We expect improved skills to reduce recurring failures and variation between agents.
Repeated baseline runs provide a reference for ordinary variability; improvements on one study do not establish transfer to other studies.

To start a coordinator, give it this repository and a request such as:

> Follow `prompt.md` using `studies/study-narps-figure2.md`.

| Location | Purpose |
| --- | --- |
| `prompt.md` | The repeated research, assessment and skill-improvement process |
| `studies/study-*.md` | A chosen scientific task, shared inputs, expected results and checks |
| `AGENTS.md` | Instructions for the coordinator working through that process |
| `skills/` | The evolving `con/skills` submodule, currently pinned to [our development branch](https://github.com/con/skills/tree/codex/pr26-stamped-next) |
| `assessment/` | The independently frozen assessor, identified by `assessment-version.json` |
| `experiments/` | Research workers' efforts, with their outputs, assessments and execution records |

The products are improved shareable skills, examples of assessment applied to real studies, and a complete STAMPED research object with figures showing outcomes, costs and limitations.
Poster production is a separate task.
Contributed study briefs can reuse the same process to test whether improvements generalize.
