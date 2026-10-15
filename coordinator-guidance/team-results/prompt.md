# Agreement in gain-related fMRI findings

**Scientific question:** How consistently do independent teams' analyses of the same fMRI dataset localize responses to potential gains, and how does agreement between their spatial maps relate to agreement in their reported conclusions?

Investigate this question using the supplied NARPS team-level data.
Produce a defensible analysis, clear figures and a concise account of the findings and limitations, with the code and results supporting your conclusions.
Choose your analytical methods, scientific tools and execution environment, including whether to use a container.
No particular published figure, clustering or numerical answer is required.

## What the data mean

Participants performed a mixed-gambles task during fMRI.
The supplied maps represent the parametric effect of potential gains for the equal-indifference group: potential gains ranged up to twice the potential losses.
Each map is a team's unthresholded group statistical image for this contrast, drawn from independent analyses of the same underlying participants.

The package includes all 64 original `hypo1_unthresh.nii.gz` maps found in numbered team-collection directories of the archived input release.
Filenames preserve the collection and team identifiers; the supplied observations do not represent every team that originally participated.
`data/observations/hypothesis1_decisions.tsv` records each included team's original Yes/No decision for a positive gain effect in the **ventromedial prefrontal cortex (vmPFC)**.
These are reported conclusions, not ground truth or whole-brain activation labels.

`data/observations/image_metadata.tsv` describes map statistic types, reported templates and image comments.
Repeated metadata submissions are retained with their source timestamps and row numbers.
`data/observations/pipeline_metadata.tsv` contains the teams' reported sample sizes and relevant analysis details; total reported participant counts need not equal the size of the equal-indifference group.
Images differ in grid, spatial reference and statistical scale; the supplied FSL MNI152 2-mm template and brain mask are available as resources.
The original exclusion table is retained in `data/orig/SuppTable3_exclusions.tsv` for context.
Team analyses share participants, so they are not independent samples of people.

## Scope and delivery

Work from these team-level images and observations; raw fMRI preprocessing is outside this task.
Use the available sample, documenting any scientifically justified exclusions.
Explain the evidence for your answer, its uncertainty and what it does not establish.
Distinguish observed associations from causal explanations.

The expected working time is approximately 45 minutes, with flexibility to finish correctly.
Create your research outputs in the provided checkout, keeping the supplied inputs intact.
The source manifest identifies original locations, extraction details and checksums.
