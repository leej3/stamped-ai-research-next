# Improve research skills through repeated use

Use the user's selected `studies/study-<chosen-study>.md` to test whether iterative improvements to STAMPED skills improve scientific results and checklist attainment, reduce recurring failures, and reduce variation between research agents.
If no study is selected, ask which brief to use.
The complete effort must itself become a STAMPED research object.

1. Fix the scientific task, common inputs, correctness checks, initial resources, worker model/settings, repetitions and total budget before starting.
   Use three rounds with three independent workers per condition per round unless the user specifies otherwise.
   Use Luna with high reasoning effort for research workers and record its exact identifier.
   A study should normally fit about 45 minutes; review progress around 90 minutes and allow productive work to finish.

2. Launch fresh agents on the same task with and without the current research skills, varying launch order.
   Use the same minimal starting state and common resource guidance for both conditions; treatment agents additionally receive the selected skills.
   Record exact starting and skill revisions for every run.
   Baseline agents must not inherit previous solutions, judgments or skill-development history.

3. Have fresh, independent judges assess each committed research object for scientific correctness and STAMPED evidence separately.
   Freeze the assessment source, runtime, judging prompt, model/settings and replay scope before the first round.
   Give judges the study's scientific checks and the target object, without condition labels or coordinator conclusions.
   Independently judge one randomly selected object per condition per round twice; retain both judgments and distinguish judge disagreement from worker variability.
   Describe residual blinding limits honestly.

4. Between rounds, improve the research skills using observed failures and successful practices.
   Record the evidence motivating each change, then compress or modularize the guidance without inserting study-specific answers.
   Keep the scientific task, baseline conditions and assessor fixed so successive rounds remain comparable.
   If an assessment defect invalidates comparison, document it and resolve the comparison design before continuing.
   Finish with a round using the final skills without further tuning on its results.

Duct logging is requested for scientific execution.
Retain every attempt, input, output, assessment, intervention and execution record with its experiment, including failures and partial results.
Use annex for large artifacts, preserve relevant environment snapshots, and verify independent retrieval and replay.
When reassessing results, state what stays fixed and what changes across data, code, dependencies and host; compare against the scientific checks chosen for that question.

Deliver the improved skills, examples of the frozen assessment, and the complete research object.
Include clear figures of individual outcomes, checklist attainment, recurring failures, costs and variability across rounds.
Keep scientific correctness separate from STAMPED evidence, retain `not-checked`, and do not invent an overall assessor score.
Have a fresh judge assess the complete effort.
Limit conclusions to the chosen study and the exploratory sample; future contributed studies can test transfer.
Poster production follows separately.
