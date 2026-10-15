# Paired change result

The five within-person changes are 1, 1, 2, 2, and 3 arbitrary units.
Their mean is **1.800**, with a
**95% Student t confidence interval of [0.761149, 2.838851]** using 4 degrees of
freedom.
The sample standard deviation is 0.836660 and the standard error is 0.374166.
All five supplied participants were retained; no values were missing and no
exclusions were made.

![Individual paired changes and the mean with its 95% t interval](results/paired-change.png)

The figure shows individual variation and the mean interval; its editable source
is `code/analyze.py`, with SVG and PNG outputs in `results/`.
The rendered PNG was visually inspected for labels, clipping, participants,
units, mean, interval, and zero reference.

## Scientific validity

`results/validation.json` records checks against an independent rational-arithmetic oracle, using mean 9/5,
variance 7/10, standard error sqrt(7/50), and a separately specified t critical
value.
A direct `scipy.stats.ttest_rel(after, before).confidence_interval()`
calculation agrees within 1e-12.
Input schema, the exact five original rows, participant identity, direction of
change, output schema, missingness, and inclusion counts were checked.
Seven invalid-input cases are rejected: duplicate ID, missing ID, missing value,
nonfinite value, nonnumeric value, singleton data, and reversed schema.

This is a correct calculation for the supplied synthetic paired design.
The interval requires a hypothetical sampling model with independent normally
distributed changes.
Five deliberately constructed examples cannot substantiate that model,
population generalization, or a causal effect.
The study reports a descriptive paired change, not a treatment-effect
conclusion.

## Research-object evidence

The native DataLad run is identified in `evidence/run.json` and declares the
code, data, protocol, environment manifest, results, and logs.
The completed direct duct record is in `logs/paired/`; the original substantive
command exited 0 after 29.368 seconds and sampled a peak resident memory of
286.3 MB.
This duration includes initial Matplotlib font-cache construction.
The native run marker and structured record remain intact, with fresh
commit-provenance trailers appended after the record.
The guard's accepted and rejected cases are recorded in
`evidence/guard-check.json`.

Exact lock bytes are retained separately on `env-snapshot` as described in the
README.
The final delivery receipt and STAMPED assessment are written outside this
assessed Git tree, so they can identify the finished commit without changing it.
They report actual annex payload retrieval, exact native rerun results, and
assessment outcomes separately.
This project's delivery scope is an independent local clone on the same host;
persistent online hosting and a second platform are not claimed.
Setup errors and observed instruction friction are retained in `evidence/`.
