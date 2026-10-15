# Protocol: synthetic paired experiment

Question: what is the mean within-person change, defined as after minus before?
This is a study of five synthetic paired observations supplied directly in the
request.
The participant is the independent unit; A–E are five distinct units, each with
exactly one before and after value.
Measurement units were not specified, so report changes in arbitrary units
without interpreting a physical quantity.
The dataset is a complete synthetic example, not evidence about a target
population or a randomized causal effect.

Before computation, define d = after − before and estimate the arithmetic mean.
Use the unbiased sample standard deviation of d (ddof=1), standard error
s/sqrt(n), and a two-sided 95% Student t interval with df=n−1.
The interval describes a hypothetical independent, normally distributed
population of paired changes; normality cannot be meaningfully established with
five constructed observations.
All supplied rows must be retained; no missing values or exclusions are
expected.
Reject duplicate participants, missing IDs, nonnumeric or nonfinite
measurements, wrong schema, and fewer than two pairs.

Independent checks: the supplied rows imply ordered changes [1, 1, 2, 2, 3],
total 9, mean 9/5, sum of squared deviations 14/5, unbiased variance
7/10, standard error sqrt(7/50), df=4.
Use independently fixed t(0.975,4)=2.7764451051977987 and tolerance 1e-12 for
the expected interval; compare the implementation with SciPy's direct paired
t-test confidence interval as a second route.
Validate actual labels, ordering, row count, values, missingness, and the
reusable rejection contract separately.
The complete dataset is also the pilot; no batch or method change is needed for
five pairs.

The figure will show each participant's paired change alongside the mean and the
95% t interval, including the zero-change reference.
Use NumPy/SciPy/Pandas and Matplotlib from the root Pixi environment.
One direct duct capture wraps the substantive command; retain metadata, stdout,
stderr, resource samples, and the final outer summary.
Native DataLad records inputs and outputs.
Fresh replay must restore the exact lock, remove only generated result/log
paths, execute native rerun, verify nonempty regeneration, and compare
deterministic results exactly.
No cluster, Entire capture, or external publication is used.
Stop after validated analysis, inspected figure, independent clone retrieval,
fresh replay, review, and a separate STAMPED assessment; computation is limited
to a few minutes.
