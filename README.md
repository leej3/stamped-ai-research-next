# Synthetic paired-change study

Estimate the mean within-person change (after minus before) for five synthetic
paired observations supplied with this task.
Measurements have unspecified arbitrary units.
This is a small study and a workflow demonstration; the confidence interval is
conditional on an independent normal sampling model for the changes, and the
constructed data support no population or causal claim.
The analysis protocol and independent expected quantities were written before
computation in [protocol/protocol.md](protocol/protocol.md).

## Layout and execution

- `data/`: exact original synthetic input and its meaning, stored in Git.
- `code/`: analysis, figure source, independent validation, capture, replay, and
  guards.
- `protocol/`: method and exact environment/input hashes.
- `results/`: JSON summary, pair-level CSV, rendered PNG/SVG, and validation
  receipt, stored in annex.
- `logs/paired/`: one direct duct capture and its completed outer summary,
  stored in annex.
- `evidence/`: setup failures, guard exercise, and delivery references.

The root `pixi.toml` declares the scientific and tooling dependencies.
Requirements are Apple Silicon macOS >=14, a Git client and Pixi on PATH, a
POSIX shell, and internet access (or populated package caches) for initial
installation.
Only macOS arm64 is claimed; no cluster, credentials, Entire capture, external
data service, or GPU is needed.
Git-annex is the declared PyPI wheel; explicit annex path rules avoid its
missing MagicMime support.
The Snapper authoring hook formats staged Markdown when Snapper is available; it
is not needed for computation.
Codex-authored commits must use fresh commit-provenance trailers supplied
through local `provenance.resolver` configuration, never an embedded host path.
Native DataLad generated commit subjects retain their required markers.

## Exact environment and replay

Ordinary working `pixi.lock` files are ignored.
The final validated lock is retained as an ordinary Git file on `env-snapshot`,
exactly one commit above the delivered `main` task commit.
The immutable snapshot and task IDs are supplied in the external delivery
receipt alongside this project; the run ID is in `evidence/run.json`.
The original computation used this same lock hash, retained in
`protocol/environment.json`.
The snapshot's manifest must equal the checked-out code manifest; replay
enforces that equality before each locked install.

For a recipient, first clone the project and restore the lock from the exact
snapshot ID supplied with delivery:

```sh
git clone SOURCE paired-copy
cd paired-copy
git show SNAPSHOT_COMMIT:pixi.lock > pixi.lock
pixi install --locked
pixi run git annex get --from=origin results logs
```

To repeat the complete local delivery and native replay check from a prepared
clone:

```sh
pixi run replay --source SOURCE --snapshot SNAPSHOT_COMMIT --run RUN_COMMIT \
  --destination NEW_ABSOLUTE_CLONE_PATH --receipt EXTERNAL_RECEIPT_DIRECTORY
```

When Codex executes the replay, additionally pass
`--provenance-resolver PATH_TO_LOCAL_RESOLVE_SH`.
The replay checks missing annex content before `git annex get --from=origin`,
hashes all delivered outputs and logs, confirms native `datalad rerun --report`,
checks out the exact input commit, reinstalls the exact lock, verifies generated
paths are absent, and executes a genuine `datalad rerun`.
It requires newly generated outputs and exact hashes for every deterministic
result.
The returned receipt states whether same-host caches were reused.
No external publication or different-platform replay is claimed.

`pixi run preflight` verifies clean committed inputs and basic preparation.
`pixi run record` is the original native-recorded analysis entry point; it must
start from the input commit, before generated outputs exist.
It invokes `pixi run analyze`, which performs the computation and independent
validation inside one direct duct capture.
`pixi run validate` independently verifies regenerated scientific outputs, and
is normally invoked within the recorded computation.
Do not edit numerical outputs by hand; a changed method needs a distinct
derivative and new recorded run.
A repeated original capture intentionally refuses to overwrite retained logs.

For dependency updates, use `pixi add PACKAGE` or `pixi update`, commit the
manifest and code, rerun the checks, then preserve the new validated lock bytes
on a new snapshot branch one commit above the final task commit.
Never re-solve while claiming an earlier locked environment.
This new study has not yet performed a post-baseline dependency update.

## Delivery scope

The requested delivery is local to an independent clone on the same host.
Original synthetic data need no credentials; this work does not assert a license
or public distribution grant for the user's material.
External persistent hosting and cross-platform execution remain outside this
trial.
The scientific result and STAMPED assessment are reported separately.
