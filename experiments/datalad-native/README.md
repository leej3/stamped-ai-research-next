# DataLad reassessment and replay

Choose what to hold fixed according to the scientific question.
Following [Choosing what changes (PR39)](https://github.com/stamped-principles/stamped-examples/blob/e3b7fe237a6c2954fc67d8161394b6d9a24fef6e/content/guides/choosing-what-changes.md):

| Question | Hold fixed | Change |
| --- | --- | --- |
| Can we recover a previous result? | Recorded data, code and dependency selection | Rebuild the installed environment on a compatible host |
| What do new data change? | Code and dependency selection | Input data |
| What does a code change do? | Data and dependency selection | Implementation |
| What do dependency updates change? | Data and code | Selected package versions |
| Can the environment be rebuilt from requirements? | Data, code and declared requirements | Fresh installation; a new solve may select newer packages |
| Does the analysis travel to another platform? | Data, code and scientific checks | Host and compatible platform-specific packages |

Record the chosen revisions, input identities, environment selection and platform with the result.
Compare numerical tolerances or scientific invariants; require identical bytes only where meaningful.
Retrieve retained annex inputs to recover old data; downloading a changing upstream source tests a new acquisition.

Each experiment owns its Pixi environment in its worktree, initially using the default requirements.
The coordinator integrates differences as [named environments](https://pixi.prefix.dev/latest/workspace/multi_environment/) in the root `pixi.toml` and routes tasks through `pixi run -e <experiment> ...`.
Keep working locks ignored; retain the final validated lock on the separate snapshot branch described in [AGENTS.md](../../AGENTS.md).

Reproducibility, ephemerality and portability involve choices: disposable installations reduce hidden state, flexible requirements ease reuse, and retained selections help recover historical results.
A fresh solve tests today's requirements; it does not reconstruct yesterday's packages.
A lock records selections but cannot guarantee future package availability or compatibility with another host.
Retaining package or container artifacts improves recovery at a storage cost.

[`datalad rerun RUN_REV`](https://docs.datalad.org/en/stable/generated/man/datalad-rerun.html) selects an old command and normally applies it to the current checkout.
Select the intended data and code separately.
When holding historical dependencies fixed, restore the matching manifest and lock from the retained environment snapshot, then synchronize with `pixi install --locked -e <recorded-env>`.
An outer `pixi run` selects its environment before DataLad changes revisions; a checkout does not update a running interpreter.
For checkout-changing replay, select the intended state before launching, or record an explicit inner Pixi invocation that synchronizes after the transition.
Record the calculation command, not a task that recursively invokes `datalad run`.

## Retained compatibility trial

The [native-001 trial](receipts/native-001/summary.json) passed 15 checks, including two native rerun generations with identical TSV, SVG and PNG bytes in a fixed environment.
This tests native run-record and commit-hook compatibility; it does not establish all the comparisons above.
Complete streams and resource records remain in [logs/native-001](logs/native-001/).

DataLad run commits retain their native `[DATALAD RUNCMD]` subject and record, with fresh Codex provenance appended; ordinary authored commits remain Conventional.
The earlier compatibility experiment remains historical evidence; new native records need no parser adapter.
