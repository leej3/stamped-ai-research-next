# Judge-launch checks

On 2026-10-15, nine launcher regression tests passed using local fixture
subprocesses. They cover role separation, frozen-assessor mismatches, missing
assessment dependencies, non-terminating review notifications, explicit hard
limits, retained prompts and stderr, and complete fixture launch records.

Real Codex `debug prompt-input` checks then confirmed the advertised study
entrypoints: baseline 0, treatment 6, judge 2. Each directory retains its input
prompt and preflight receipt; the adjacent command JSON records invocation,
exit status and streams. These checks assemble prompts without running a model.

No live research worker or judge ran during this validation. The checks do not
establish container isolation, successful grading, or MRI workload duration.
