# NARPS gain consistency

A study of agreement between independent teams' gain-related fMRI maps and its relationship to their reported conclusions.

- `input/` is the complete worker package: scientific prompt, original observations, templates and source manifest.
- `reference/` retains the source archives, published analyses, preparation code and verification evidence for coordinators and assessors.
- `experiments/<run>/` will hold returned research objects and independent assessments.

Launch workers from an input-only snapshot with the assigned skills and common environment.
Do not give them this dataset's reference files or other runs' history.
The parent project pins this dataset as a submodule and controls the research/assessment/skill-improvement loop.

The input package was curated from the original archive without consulting computed reference results to select teams.
Scientific analysis and workload timing have not yet been tested.
