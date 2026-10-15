# PR26 alignment and implementation strategy

This is an engineering integration record, not a scientific trial or evidence of skill efficacy.
The workshop develops reusable STAMPED study skills by testing pinned revisions on scientific questions and having fresh agents apply a separately frozen assessor.
The initial demonstration should address the original scientific hypothesis behind NARPS Figure 2; reproducing that figure or matching an archived analysis is not the worker's objective.

## Intended products

- An evidence-linked demonstration of the frozen assessment/checklist on completed studies.
- A versioned, increasingly useful and modular collection of STAMPED study skills.
- A complete STAMPED research object covering this development process.

John will create the poster independently from the results; poster production is outside this repository's scope.
Scientific correctness, STAMPED evidence, failures, cost and uncertainty remain distinct.
Improving treatment performance and reducing its variability are hypotheses; baseline scores need not stay constant, and all attempts must remain visible.

## Shared implementation

Rebase our contributions onto Yarik's `stamped-skills-impl` and its pinned `stamped-evals` revision, preserving upstream history.
Use new publication branches rather than rewriting branches used by other active chats or frozen records.
Keep the checklist, verdict vocabulary, probes, executable templates, scientific oracles and evaluation fixtures shared.
Retain our native DataLad replay fixes, completed-response validation, exact environment identities and optional Pixi, ReproNim and Entire support.
Project-specific worker launching and iteration orchestration remain in this workshop.

The original contribution histories remain available; `sources.json` records source pins and the rebased mapping.
Merge-only changes to the original integration commit are retained explicitly, including the independent workflow evidence link and evals pointer.
Historical run prompts, reports and validation claims describe their original snapshots; rebasing does not make them tests of this candidate.

## Resolutions

| Difference | Resolution | Effect on the objective |
|---|---|---|
| Independently fixed absent-tool crash | Keep upstream exception handling and both relevant tests | Host inspection remains usable without DataLad |
| Rewritten creation instructions versus new publication text | Keep the concise workflow and route to upstream explicit-refspec guidance | Retains history/content publication without prescribing a stack |
| Diverged evals submodule | Rebase its contributions first; point working skills at the combined revision | Preserves upstream tests and our evidence-boundary checks |
| Changing working assessor code versus fixed measurement | Keep `assessment/` and its source/environment pins unchanged | Prevents moving the grading criteria during skill development |
| Common infrastructure versus treatment guidance | Provide equal capabilities; baseline must not receive research skills, references or prior outputs | Measures the declared guidance rather than extra tool access |
| Upstream four-arm evaluation versus workshop two-arm evaluation | Reuse tasks/checks where suitable; record condition definitions and do not pool unlike treatments | Keeps findings interpretable |
| Experimental environment changes | Retain deliberate data/code/environment/host selection and exact identities | Supports both replay and explicitly requested reassessment |

## Coordinator interface

The executable study-development strategy lives in the root [prompt.md](../../prompt.md) and [coordinator instructions](../../AGENTS.md), owned by the coordinating chat.
This integration preserves their independent input-only research workers, repeated matched conditions, external frozen judging, retained failures and changes only between iterations.
The treatment revision must name the complete tested skills tree, including its evals gitlink; an updated working assessor in that tree must not replace the separately pinned judge.
Keep scientific correctness, item-level STAMPED evidence and costs separate, and retain the distinction between development on repeated tasks and transfer to new studies.

## Decisions reserved for John

- Do not change the frozen assessor or selectively rescore outcomes to improve the treatment's apparent performance.
  A demonstrated grading defect requires an explicit version decision and comparable reassessment of affected objects.
- Escalate changes to the scientific question, cohort, treatment boundary, study budget, or interpretation of the baseline.
  Routine text conflicts and equivalent tool repairs can be resolved within the recorded objective.

One upstream probe limitation remains under review: annex location metadata is not a successful recipient retrieval, and an unavailable annex check can currently fall through to a positive publication verdict.
The working branch retains the upstream implementation in this rebase; do not promote it into the frozen assessor without resolving and testing that evidence boundary.
The existing requirement to review probe findings and verify actual retrieval still applies.

## Tracking concurrent work

The chat [Follow prompt.md instructions](codex://threads/01a13c60-1063-7be3-8eab-fb5df54cb12b) owns PR3/PR5, coordinator instructions, launch isolation and study integration. This integration owns the skills/evals rebase and the record here.
John clarified that NARPS data feasibility and scientific-scope decisions belong to the other chat; they do not gate this integration.
The shared interfaces are the skills/evals gitlinks, treatment discovery and baseline absence, and frozen assessor identity.
No study content or launcher architecture is changed here.
John authorized direct coordination between those chats on 2026-10-15.
No scientific rounds or live judging are launched by this integration.

At integration milestones, read the linked chat's fresh status and refetch PR26, its evals gitlink and our contribution branches.
Record observed source changes in `sources.json` before adopting them.
Do not move a treatment revision within an active comparison or change the frozen assessor as part of an upstream refresh.
This is task-scoped tracking; no background schedule is installed.

## Validation

The combined source passed 117 ordinary tests, 26 evaluation cases and all 18 scripted mutants, with no false unmet/partial finding among the clean fixture's 17 answered items. The ordinary pass skipped 26 separately executed evaluation cases and two no-DataLad checks; both fallback checks then passed with a restricted PATH. Structural validation checked 27 skills with no errors and ten pre-existing warnings. The current parent passed 19 launcher tests, and the frozen assessor source/environment check passed.

A fresh independent agent followed the hashed skill snapshot in a planning-only publication/replay handoff.
It preserved the frozen assessor, explicit destination branches, recipient retrieval and genuine regeneration boundaries.
The exact prompt, response and classified friction are retained here; snapshot hashes match the integrated skills.
This did not execute science, prove remote delivery or measure skill efficacy.

See `sources.json`, `skill-validation.log`, `no-datalad-validation.log` and `blind-review.json` for exact identities, commands and scope.
