# Improve research skills through repeated use

Use the selected study submodule to test whether STAMPED guidance helps research agents answer a scientific question with sound methods and more thorough, efficient and consistent reproducibility.
Iterate on the skills using evidence from their use.
If no study is selected, ask which one to use.
The complete effort must itself become a STAMPED research object.

1. Fix the scientific question, worker input package, evaluation criteria, common resources, model/settings, repetitions and total budget before starting.
   The study's `input/prompt.md` asks the question and defines its scope; workers choose defensible methods, software, figures and reproducibility practices.
   Keep reference answers and evaluation guidance in `reference/`, outside worker inputs.
   Use three rounds with three independent workers per condition per round unless the user specifies otherwise.
   Use Luna with high reasoning effort and record its exact identifier.
   Aim for a task that fits about 45 minutes; review progress around 90 minutes and allow productive work to finish.

2. Launch fresh agents on the same task with and without the current research skills, varying launch order.
   Both conditions receive the same committed input package and common resources; treatment agents additionally receive the selected skills.
   Record exact input, environment and skill revisions for every run.
   Neither condition receives previous solutions, judgments or coordinator history.
   Baseline agents also receive no research skill files.

3. Have fresh, independent judges assess each committed research object for scientific validity and STAMPED evidence separately.
   Freeze the assessor source, runtime, judging prompt, model/settings and replay scope before the first round.
   Supply the target object and scientific evaluation guidance without condition labels or coordinator conclusions.
   Evaluate the reasoning, evidence, limitations and reproducibility of the chosen approach; defensible alternative methods need not match a published solution.
   Independently judge one randomly selected object per condition per round twice; retain both judgments and distinguish judge disagreement from worker variability.
   Describe residual blinding limits honestly.

4. Between rounds, improve research skills using observed failures and successful practices.
   Record the evidence motivating each change, then compress or modularize guidance without inserting study-specific answers.
   Keep the question, inputs, baseline conditions and assessor fixed so successive rounds remain comparable.
   If an assessment defect invalidates comparison, resolve the comparison design before continuing.
   Finish with a round using the final skills without further tuning on its results.

Duct logging is requested for scientific execution.
Retain every attempt, input, output, assessment, intervention and execution record, including failures and partial results, with the selected study's experiments.
Use annex for large artifacts, preserve relevant environment snapshots, and verify independent retrieval and replay.
When reassessing results, state what stays fixed and what changes across data, code, dependencies and host, according to the question being tested.

Deliver improved skills, examples of the frozen assessment, and the complete research object.
Include clear figures of scientific outcomes, checklist attainment, recurring failures, costs and variability across rounds.
Keep scientific validity separate from STAMPED evidence, retain `not-checked`, and do not invent an overall assessor score.
Have a fresh judge assess the complete effort.
Limit conclusions to the chosen study and exploratory sample; future studies can test transfer.
Poster production follows separately.
