# Analysis protocol: NARPS Hypothesis 1, equal-indifference group

## Question and scope

Test whether the population mean gain-effect estimate is positive in any vmPFC voxel in the 54-member equal-indifference group, at the group-analysis stage. The fixed inputs are the 54 AO86 participant cope maps, metadata and upstream methods in `input/`; no time-series scans or upstream reanalysis are in scope.

## Data and estimand

- Unit: participant; one unthresholded participant-level gain contrast parameter estimate map per participant, averaged across four runs upstream.
- Population: all 54 participants in the supplied equalIndifference cohort. Join map IDs to `input/participants.tsv`; duplicate, missing, nonfinite, geometry-mismatched and all-zero maps are checked. Exclude no participant based on observed effect magnitude. If a map fails a prespecified integrity check, report it and stop rather than silently changing the sample.
- Target: mean of participant cope estimates at each voxel, and its one-sided group statistic. These cope values use a mean-centered, variance-normalized gain modulator upstream; they are not per-currency-unit slopes, standardized statistics, nor raw BOLD change. Gain is modeled separately from loss, so the estimate is conditional on that first-level model.
- Group inference: one-sample positive one-sided t statistic with equal participant weights; sign-flip permutation under a symmetric zero-centered null, with max statistic across all in-mask voxels for whole-brain family-wise error control. Use 9,999 random permutations, fixed seed, add-one p-values, alpha=.05. Report effect estimates and uncertainty as well as the corrected inference.
- Search mask: intersection of finite, nonzero support across all 54 maps, with identical dimensions and affine required. This uses the supplied maps only and defines the spatial family before testing. Document mask voxel count and volume. A predefined vmPFC anatomical overlay (Harvard-Oxford cortical atlas: Frontal Medial Cortex and Subcallosal Cortex labels) will identify localization; it does not narrow the correction family or determine support.

## Quality checks and uncertainty

Verify exact cohort-to-map correspondence, file checksums against `input/sources.json`, NIfTI dimensions/affines/spatial reference, finite values, nonzero support and per-map summary distributions. Inspect group mean and subject-level vmPFC ROI distribution. Use a participant bootstrap interval for the descriptive vmPFC ROI mean if implemented; whole-brain significance remains based on the max-statistic permutation test. Variance maps and the full first-level pipeline are absent, so inverse-variance mixed-effects inference cannot be reconstructed. The cope-only group model relies on exchangeability/symmetry and may be less efficient or less calibrated than a model using participant variances.

## Interpretation and stopping rules

Hypothesis support requires at least one positive whole-brain FWE-corrected voxel anatomically within the predefined vmPFC overlay. Report all corrected whole-brain findings; do not select among models by significance. No corrected vmPFC result is lack of evidence at this sample size and analysis resolution, not evidence of no effect. State whether correction was based on the full in-mask family and whether any exclusions occurred. Retain command/log metadata and output summaries under `logs/`; scientific outputs and figures go under `results/`.
