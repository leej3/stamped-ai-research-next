# Scientific assessment context

Assess the original NARPS Hypothesis 1: a positive parametric effect of potential gain in vmPFC for the equal-indifference group.
The original [analysis instructions](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf) require whole-brain-corrected inference.
The scientific task is in `input/study-task.md`.

Workers receive 54 participant gain-effect maps from team AO86 and the corresponding cohort metadata.
Preprocessing and participant modeling are fixed; evaluate group inference conditional on those inputs.
Judge whether the analysis handles the intended participants, image geometry, quality, gain scaling, uncertainty and anatomical interpretation appropriately.
The maps represent independent participants; runs have already been combined within each person.
Evaluate exclusions, uncertainty and multiple-comparison correction against the actual method.
Defensible approaches can reach different conclusions; matching a prior team's answer is not the criterion.
Keep scientific validity separate from the frozen STAMPED assessment.

## Input preparation and rehearsal

`prepare_subject_inputs.py` selects all 54 original single-subject Hypothesis 1 effect maps from [NeuroVault collection 4932](https://neurovault.org/collections/4932/), totaling 96,387,264 bytes.
Their participant IDs exactly match the equal-indifference group in pinned OpenNeuro ds001734 version 1.0.4.
`input/sources.json` records the source URLs, cohort and methods revisions, file sizes and SHA256 hashes.
`input/upstream-methods.md` explains the fixed model and its scaling limits; participant variance maps are not supplied.
The task makes no claim to reproduce or evaluate choices in the upstream time-series analysis.

`participant-preparation/` retains selected source metadata, verification and annex retrieval evidence.
`rehearse.py` times an intercept-only group model, whole-brain correction and figure generation; `rehearsal/` and `rehearsal-replay/` retain its outputs and timings.
The repeated numerical arrays matched exactly.
This establishes computational feasibility on the recorded host, not benchmark suitability, an agent completion time, a prescribed method or a definitive anatomical answer to Hypothesis 1.
Task-depth validation remains pending: meaningful scientific decisions and checks must justify the intended workload, without adding computation merely to consume time.
Research agents must not receive these rehearsal outputs.

## Retained reference material

`team-results/` preserves the former agreement-task package, including its prompt and source manifest.
Those team maps and decisions are prior answers to Hypothesis 1 and are excluded from worker inputs.
`prepare_team_results.py` regenerates this reference package from `published/`.
The existing verification, retrieval and publication receipts describe the paths at commit `2658c4759dac2d3817a1895444459adadadcd239`; their original evidence is retained unchanged.
No research-agent comparison or independent judging rounds have been run here.
