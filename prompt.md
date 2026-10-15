# Improve research skills through repeated use

Test whether iterative improvements to STAMPED skills increase checklist attainment and scientific reproduction success, reduce recurring failures, and reduce variation between independent agents performing the same MRI study.
Fresh baseline agents provide a contemporaneous reference for ordinary variability and drift.
The complete development study must itself become a STAMPED research object; poster production follows separately.

Use the single, fixed task in [study.md](study.md).
Run three rounds, each with three independent baseline workers and three independent workers using the current research skills.
Use Luna with high reasoning effort, recording the exact model and settings.
Keep the scientific task, data, common resources and settings identical across conditions and rounds; vary launch order.
Record the skill revision for every run and change skills only between rounds.

Each worker starts in a prepared worktree containing only the common scientific task, inputs, operational resources and selected skills.
Exclude coordinator instructions, earlier experiments and assessment results from worker context.
Start each baseline from the same minimal starting state; a treatment start differs only in its declared skill revision and exposure.
Do not start research workers from the accumulating coordinator branch.
Worktrees share Git objects and refs: separate directories alone do not prove information isolation.
If containerizing workers, expose only their checkout, inputs and required host services; verify actual file and skill visibility.

The task should normally fit within 45 minutes after preparation.
Allow completion, review progress around 90 minutes, and extend productive work.
Record elapsed time, interruptions and assistance; retain failures and partial outputs.
Do not discard an attempt because it runs long or scores poorly.

Use `pixi run judge` for a fresh judgment of each committed research object.
Freeze the assessor, its runtime, judge model/settings, [judging prompt](judge-prompt.md) and replay scope before round one.
The coordinator never supplies grades, condition labels or prior-round history to judges.
Independently judge one randomly selected object per condition per round twice; retain both judgments and report disagreement separately from worker variability.
Blinding is partial and must be described honestly.

After each of the first two rounds, improve the research skills from observed problems and useful practices.
Record the evidence motivating each change; compress and modularize guidance without embedding this study's answers.
Keep the assessment frozen.
If a defect prevents valid assessment, document it and pause comparisons rather than silently changing the measuring instrument.

Retain all inputs, code, outputs, figures, assessments, skill revisions, native capture, DataLad records and requested module-local duct logs.
Use annex for large files and verify independent retrieval and replay.
Distinguish original worker products from later curation.

Deliver the improved skills, assessment examples and complete research object, with figures showing per-item attainment, scientific reproduction outcomes, recurring failure frequencies, costs and variation across rounds.
Keep `not-checked` visible; use the frozen checklist's verdicts without inventing an overall assessor score.
Three replicates give exploratory evidence, not a precise variance estimate.
Have a fresh judge assess the final research object.
Limit conclusions to this task; future contributed studies can test transfer using the same process.
