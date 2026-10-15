# NARPS preparation pilot 2

An independent baseline agent investigated the original NARPS positive-gain/vmPFC hypothesis using 54 fixed participant effect maps. Read the [scientific report](results/report.md), [task](input/study-task.md), [input provenance](input/sources.json), and [execution record](execution/README.md).

The coordinator preserved the worker's scientific files unchanged at `466d43f39dc3d40ac64038ff03066b483b6d9457`, then packaged its execution evidence.
The exact final resolved environment is preserved on branch `codex/env-narps-suitability-20261015-02`; the working branch keeps only the root Pixi manifest.

The report gives the worker's declared analysis command.
A fresh recipient also needs annex content:

```sh
pixi install
pixi run git annex init
git remote add con-hub https://hub.centerforopenneuroscience.org/leej3/stamped-ai-research-next.git
git config remote.con-hub.annexurl annex+https://hub.centerforopenneuroscience.org:443/git-annex-p2phttp
pixi run git annex get --from con-hub .
```

The retrieval receipt in `execution/` records the independently checked payloads.
This preparation pilot was not a formal skills comparison or an independently graded scientific result.
