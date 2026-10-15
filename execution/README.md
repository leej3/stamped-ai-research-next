# Preparation pilot execution record

This independent baseline pilot used the same fixed input package, Luna model and high reasoning effort as its two companion pilots.
The scientific result is preserved at `466d43f39dc3d40ac64038ff03066b483b6d9457` before coordinator packaging.
The worker left its research artifacts uncommitted; no scientific repair was made.

`launch/` retains the prompt, exact input boundary, environment and hook setup, native public event stream, stderr and completion record.
`native-session/execution-transcript.jsonl` adds timestamped public tool calls and outputs; `export.json` documents the export and locally retained original.
`scientific-completion.json` records hashes of the unchanged scientific artifacts.

`outer/` retains the launch stream and `/usr/bin/time -l` measurements.
These CPU and maximum-process RSS values cover setup, the CLI and its descendants, not analysis alone.
All three pilots ran concurrently on the same Apple M4 host.
`summary.json` separates native-agent elapsed time from preparation and launcher overhead; isolated analysis-only resource values were not captured.

No experimental research skills or frozen judging round were used.
This is a descriptive preparation sample, not evidence of skill efficacy or a stable estimate of natural variability.
