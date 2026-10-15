# Scientific assessment context

Assess the original NARPS Hypothesis 1: a positive parametric effect of potential gain in vmPFC for the equal-indifference group.
The original [analysis instructions](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf) require whole-brain-corrected inference.
The scientific task is in `input/study-task.md`.

Judge whether the analysis uses the intended participants and events, estimates the gain effect with a defensible model, handles image geometry and quality appropriately, and supports its group inference and anatomical interpretation.
Repeated runs are observations within participants, not independent people.
Evaluate exclusions, uncertainty and multiple-comparison correction against the actual method.
Defensible approaches can reach different conclusions; matching a prior team's answer is not the criterion.
Keep scientific validity separate from the frozen STAMPED assessment.

## Input preparation

Participant data are available in [OpenNeuro ds001734, version 1.0.4](https://openneuro.org/datasets/ds001734/versions/1.0.4), corresponding to [source commit 64ec117](https://github.com/OpenNeuroDatasets/ds001734/tree/64ec117560ab58ed0fe1273f3e90887b1768b268).
The participant table identifies 54 equal-indifference participants.
Each has four preprocessed runs, with events in the source subject directories and confounds under `derivatives/fmriprep/`.
The public S3 inventory contains all 216 corresponding preprocessed BOLD files, totaling 263,550,623,893 bytes.
This checks availability metadata only: the scan payloads have not been retrieved or verified here.

Stage and verify the relevant participant inputs before launching workers, then rehearse the workload on the intended resources.
Do not substitute prior group maps for participant observations.
If starting from participant contrast and variance maps instead, document their derivation and the resulting limits on worker analytical choices before freezing the task.

## Retained reference material

`team-results/` preserves the former agreement-task package, including its prompt and source manifest.
Those team maps and decisions are prior answers to Hypothesis 1 and are excluded from worker inputs.
`prepare_team_results.py` regenerates this reference package from `published/`.
The existing verification, retrieval and publication receipts describe the paths at commit `2658c4759dac2d3817a1895444459adadadcd239`; their original evidence is retained unchanged.
No participant-level analysis, timing rehearsal or research-agent comparison has been run here.
