# Assessment version 1

[The source and runtime pins](../../assessment-version.json) keep grading independent of changes to the research workflows.
Run `pixi run assessment-check`, `assessment-probes` or `assessment-validate` from the project root.

Validation passed 116 unit/regression checks, 26 evaluation cases and 18 scripted mutants.
A fresh blind assessment detected the injected defect and validated all 31 answers without running the target pipeline.
The [validation record](candidate-validation.json) distinguishes the exact tested snapshot from the small wording corrections made afterward.
The [installed-task checks](runtime-checks/checks.json) also verify completed-response validation and rejection of changed assessment source.

[Blind evidence](blind-001/) and [complete execution logs](logs/) retain successful and failed attempts.
Probe results require evidence review: task names, raw inputs, comments and recorded historical paths can produce false flags.
The skill records justified overrides; these checks do not establish general assessment accuracy.
