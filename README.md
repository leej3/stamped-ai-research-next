# NARPS

Investigate the original NARPS hypothesis that increasing potential monetary gain produces a greater fMRI response in ventromedial prefrontal cortex in the equal-indifference group.
The task starts from 54 participant effect maps (96 MB); upstream processing and individual modeling are fixed.

- `input/study-task.md` describes the scientific task; `input/` holds only material supplied to workers.
- `coordinator-guidance/` holds evaluation guidance, published reference results and preparation evidence.
- `results/<run>/` holds returned research objects, assessments and execution records.

The workshop pins this study as a submodule and supplies its skill-improvement process.
Workers receive only `input/`, their assigned skills and common resources.

Run `pixi run verify-input` to check the participant maps and metadata.
`pixi run prepare-input` retrieves missing inputs; `pixi run rehearse` checks group-analysis cost without launching research agents.
**Inputs are verified; an independent agent trial remains pending.** The computational smoke test completed in seconds and repeated numerical outputs exactly.
Fast computation is acceptable; scientific reasoning, checks, interpretation and reproducibility are the intended workload.
A full agent's research and reporting time remains unmeasured, so task-depth validation is still pending.
See [readiness](coordinator-guidance/readiness.json) and the [computational timing record](coordinator-guidance/rehearsal-replay/report.json).

The older team-level maps and decisions remain in `coordinator-guidance/team-results/` as reference material, outside worker inputs.
