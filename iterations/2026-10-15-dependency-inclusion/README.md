# Dependency inclusion and exact environments

The NARPS pilot review found that MUST/010 incorrectly lost credit for floating dependency declarations.
Inclusion, version control and exact environment replication are separate checklist questions.

Adopt working skills [`fdf31fe`](https://github.com/con/skills/commit/fdf31feecb4ee37a8487188447d61c006b11099f), replacing `496d470`; its evaluation submodule is [`d2ec49a`](https://github.com/con/skills/commit/d2ec49a784eea8667abf0231b53e178bc1c7c4f1), replacing `20511bd`.
The change removes version pinning as a condition for the dependency-inclusion probe's positive suggestion.
It retains specification-kind evidence and checks for undeclared host tools; the assessor still reviews dependency completeness.
No new skill prose was needed.

[Published validation and independent scoped review](https://github.com/con/skills/tree/d2ec49a784eea8667abf0231b53e178bc1c7c4f1/stamped/blind-runs/2026-10-15-dependency-inclusion) cover 120 ordinary tests, 26 evaluation cases, 18 detected mutants, two no-DataLad checks and two synthetic floating-environment objects.
Lint reports zero errors and 10 existing warnings.
The review's initial interpreter lacked the declared `jsonschema` prerequisite; the supplied installed runtime subsequently completed all three documented commands.
Both attempts remain in the evidence.
These checks support the narrow correction, not general assessor validity or a demonstrated research benefit.

This is a working-skills update between preparation rounds.
The historical assessment source remains `d867c1d` with runtime `3552d50`; its version record and existing judgments are unchanged.
No new scientific comparison or regrading was launched.
Annex-publication evidence remains an open assessor-development issue, so this is not a formal freeze recommendation.
