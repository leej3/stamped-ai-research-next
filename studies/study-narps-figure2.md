# Reproduce NARPS Figure 2

**Question:** How consistent are the whole-brain gain-related fMRI maps produced by independent teams analyzing the same data, and do similar maps necessarily imply the same reported conclusion?

Reproduce Figure 2 of [Botvinik-Nezer et al. (2020)](https://doi.org/10.1038/s41586-020-2314-9), using its shared maps, metadata and published analysis.
The [open manuscript](https://pmc.ncbi.nlm.nih.gov/articles/PMC7771346/) describes the methods and exclusions.
Limit the analysis to Hypothesis 1, the gain effect in the equal-indifference group, and the 64 teams included in the published unthresholded-map analysis.
Use the original methods; identify any necessary software changes explicitly.

## Inputs and analysis

[The source manifest](narps-figure2/sources.json) identifies the archived input data, reference results and exact analysis-code revision used by the publication.
Start from the shared team-level statistical images, not an already computed correlation matrix.
Read the paper and published code to establish team exclusions, contrast directions, statistic conversions, common space and voxel mask.
Do not reverse a team's sign merely because its results disagree with others.

Recompute the whole-brain Spearman correlation matrix and the published Ward clustering with three clusters.
Recover the cluster-average statistical maps and the fraction of teams reporting a positive conclusion in each cluster.
Use established MRI and scientific tools, preserving image geometry and team identifiers.
Provide:

- The labeled correlation matrix, cluster membership, mean NIfTI maps and decision fractions.
- A correlation/clustering figure and brain-map panels corresponding to the published result, with editable plotting code.
- A concise account of the finding, disagreements with the reference, limitations and how to rerun the analysis.

Compare numerical arrays and team membership with the archived reference after aligning identifiers; cluster numbering and display ordering may differ.
Report maximum absolute numerical differences and agreement of cluster partitions.
Never treat a visually similar plot as sufficient evidence of numerical reproduction.
Keep scientific correctness distinct from the quality of the delivered research object.

## Available inputs and scope

The original team maps, archived reference results and historical FSL reference grid/mask are annexed under `studies/narps-figure2/`; the source manifest records their source versions, checksums and verification evidence.
Provide the same verified inputs to every worker before starting its clock.
The original analysis code is available to every worker as a scientific resource.
Reference outputs support comparison; workers must recompute the result from the team maps.

Choose suitable scientific libraries and tools, including whether to use a container.
The published software specification is a compatibility reference, not a required execution platform.
Record the environment actually used and explain any methodological changes.

This task covers team-level MRI map analysis, not raw fMRI preprocessing.
The working target is approximately 45 minutes, allowing longer to finish correctly.
Its runtime and numerical agreement remain untested; establish both in a rehearsal before scored rounds and fix comparison tolerances then.
Do not reduce the 64-team cohort or change the scientific target to meet the target time.
