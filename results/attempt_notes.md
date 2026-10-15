# Analysis attempt log

The initial permutation run used `sum * sqrt((n-1) / variance_sum)` for each sign-flipped voxel, omitting the factor `sqrt(n)` in the denominator. It inflated the null *t* statistics, yielded a max-*t* cutoff near 39.5, and incorrectly assigned FWE *p* = 1 to every voxel. That run was rejected. The final script uses `sum * sqrt((n-1) / (n * variance_sum))`; the final outputs and report were regenerated from that corrected statistic. The valid run is recorded in `run.log`.

A subsequent verification rerun initially stopped because two generated NIfTI files had been annexed and were read-only. The files were unlocked, the script completed, and the regenerated large maps were annexed again. No scientific results from that failed rerun were used.
