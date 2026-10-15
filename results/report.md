# Potential gains and vmPFC activity

## Conclusion

In the equal-indifference group, these maps do **not support a positive gain effect in the vmPFC under whole-brain family-wise error control**. A 10-mm a priori sphere centered at MNI (0, 45, -6) contained no significant positive voxel. Its mean participant-level contrast estimate was -0.010 (95% t interval -0.039 to 0.018); the largest vmPFC-sphere statistic was t(53) = 1.33, with whole-brain max-T adjusted p = 0.9999. This is a lack of corrected evidence for the specified effect, not evidence that the true effect is exactly zero.

The whole-brain test did identify 160 positive voxels (six 26-connected components; whole-brain maximum t = 6.62, adjusted p = 0.0001), with the peak at MNI (-26, -102, -3.6). These posterior findings are outside the target vmPFC and do not answer the hypothesis affirmatively.

## Data and model

We analyzed all 54 supplied AO86 equal-indifference participant maps, with no exclusions. The maps passed source SHA256 checks and shared a 97 x 115 x 81 MNI152NLin2009cAsym grid (2 x 2 x 2.4 mm); there were no nonfinite values or zero-variance voxels in the analysis mask. The mask was the union of nonzero map support (251,063 voxels), a sign-independent coverage rule. The vmPFC sphere overlapped 434 voxels of that mask.

At each voxel, the group model was an equal-weight one-sample random-effects test of the participant contrast estimates against zero. For the directional hypothesis we used 9,999 random participant-level sign flips plus the observed assignment, preserving within-map spatial dependence. The positive maximum t statistic over the full analysis mask supplied voxelwise family-wise-error adjusted p values. The sign-flip test assumes participant effects are exchangeable and symmetric about zero under the null. There are no supplied participant variance maps, so this is an ordinary equal-weight second-level model rather than a precision-weighted mixed-effects model. Whole-brain correction follows the original NARPS instruction to decide support from a whole-brain corrected result for the hypothesized region ([analysis instructions, Hypothesis 1](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf)).

The vmPFC is not a uniquely bounded atlas label. We operationalized it before examining results as a 10-mm radius MNI sphere at (0, 45, -6), and evaluated whether any voxel in that sphere passed the same whole-brain correction. The circle in the figure marks this definition. Its mean estimate and confidence interval are descriptive summaries; the inference uses the voxelwise max-T procedure.

## Interpretation and limits

Each supplied image is a participant contrast parameter estimate for the upstream mean-centered, variance-normalized gain modulator, averaged across runs. It is not a z/t map, and its coefficient is **not** BOLD change per currency unit. It reflects the gain-related response conditional on the specified participant model: response-time-duration trials, separate response-choice and gain modulators, and a separate gain model rather than a joint gain/loss model. The upstream choices are fixed here; there are no time-series scans, participant variance maps, or executable upstream pipeline with which to reassess them. Because the gain range was twice the loss range, this analysis also says nothing about a gain-versus-loss slope comparison.

No corrected vmPFC result means this analysis did not detect the hypothesized positive response at its chosen whole-brain-controlled threshold. It does not establish a null effect or rule out smaller effects; the descriptive interval still includes positive values. The sphere is one defensible operational definition, and other reasonable vmPFC boundaries could yield different localization summaries. Sign-flip inference also depends on symmetry of participant effects, and the finite permutation sample gives p-value resolution of 0.0001.

## Figure

![Group gain-effect estimates and positive whole-brain max-T significant voxels](group_effect_and_fwe.png)

Top row: mean upstream contrast estimate in MNI slices. Bottom row: t values shown only where positive whole-brain max-T FWE p <= .05; gray indicates the analysis mask. The black/cyan circles show the vmPFC sphere cross-sections. Posterior corrected voxels are visible at y = -100 mm; no corrected voxel overlaps the vmPFC sphere.

## Reproducibility files

- `analyze.py`: complete group-analysis and figure-generation code.
- `results.json` and `quality_checks.json`: machine-readable findings and QC.
- `vmPFC_participant_effects.csv`: one sphere-averaged contrast estimate per participant.
- `group_mean_effect.nii.gz`, `group_tstat.nii.gz`, `group_p_fwe_maxT.nii.gz`, `analysis_mask.nii.gz`: group maps and mask.
- Duct run metadata, captured stdout/stderr, and resource-use samples are in `../logs/`; the report-ready run is `group_analysis_20261015_final2_*`. Earlier runs, including the corrected failed attempt, were retained.
