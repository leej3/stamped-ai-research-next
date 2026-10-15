# Native capture proof

This is a technical rehearsal, not a scientific trial.
Tests used Entire 0.11.4, Codex Desktop 26.1007.71326 and bundled CLI 0.162.0-alpha.17.2, model `gpt-6-astra`, effort `ultra`, on one macOS host on 15 October 2026.

| Case | Native evidence | Exact uploaded refs + remote checkpoint metadata |
|---|---|---|
| Same session, before branch switch | Real file event and commit | Passed; `clean-branch-a-hosted.json` |
| Same session, after branch switch | Same session; new branch/file/commit | Passed; `clean-branch-b-hosted.json` |
| Separate linked worktree | Fresh session in prepared worktree | Passed; `clean-worktree-hosted.json` |
| Fresh clone | Fresh session in prepared independent clone | Passed; `clean-clone-hosted.json` |
| Native spawned child in parent checkout | Native child identity, completed file event and stored task transcript | Passed; `clean-child-hosted.json` |
| Native child assigned a separate prepared worktree | Absolute file event and child-owned commit | Passed; `separate-child-hosted.json` |

Receipts are under [receipts](receipts).
Each clean test now has a visible Entire session page as well as matching remote checkpoint metadata and exact uploaded refs.
The new repository initially returned 404: remote checkpoint resolution alone did not prove dashboard indexing.
Explicitly onboarding its GitHub mirror resolved that distinction; the UI then showed all five sessions.

| Capture | Actual session page observed in Entire |
|---|---|
| Branch switch | [Open session](https://entire.io/gh/leej3/stamped-ai-research-next/session/01a1406b-2f30-78c1-add0-8766cd1a9b90) |
| Linked worktree | [Open session](https://entire.io/gh/leej3/stamped-ai-research-next/session/01a1406b-c517-7da3-914b-6eeef77c0bdd) |
| Fresh clone | [Open session](https://entire.io/gh/leej3/stamped-ai-research-next/session/01a1406c-049c-7f30-8fca-25f6f3302dcd) |
| Child in parent checkout | [Open session](https://entire.io/gh/leej3/stamped-ai-research-next/session/01a1406c-6c70-7082-aee1-e7f79a901f90) |
| Child in separate worktree | [Open session](https://entire.io/gh/leej3/stamped-ai-research-next/session/01a14078-0213-7c81-b719-3eae308453f4) |

Both child tests are tasks nested under their parent checkpoint, not top-level sessions.
In the separate-worktree test the child wrote only its assigned absolute path and committed in that worktree.
Its native session's initial cwd remains the parent's checkout.
The cross-worktree task summary omitted its file list; the receipt checks the stored completed absolute FileChange event and the child commit instead.
Independent native CLI sessions per worktree remain the simpler launch route for parallel research.

[All twelve original study session links](original-session-links.md) were observed directly in the hosted UI.

## Reuse

After the one-time [host setup](../../scripts/README.md), run from the stable repository checkout:

```sh
python3 scripts/prepare_launch.py --branch codex/my-task \
  --prompt /absolute/path/task.txt --evidence experiments/my-task/launch \
  --condition baseline
```

Use `--kind clone --clone-path /absolute/absent/path` for an independent clone.
Use `--condition skills` to expose the five project STAMPED skills.
The same project tree and common resource skills remain present in both conditions; this controls skill discovery, not filesystem read permissions.
The effective prompt is audited before launch.
Its hash and visibility results are retained.

The launcher creates the checkout, initializes pinned submodules, validates and copies the matching source Pixi lock, installs the worker environment, initializes annex with its explicit payload remote, installs native Entire hooks, reuses only byte-identical existing approval records, and launches a fresh native process with inherited session IDs removed.
Changed or denied hooks fail.
Preparation is serialized; launch can then run independently.
A native file event and real commit must still be checked before research.

For requested execution capture, wrap the whole command once with direct `duct -p /absolute/experiment/logs/unique/run_ --fail-time 0 ...`.
The worker must not nest wrappers.
Failed and partial logs remain intact.

## Boundaries

Automatic checkpoint publication is disabled.
Only reviewed explicit code and checkpoint refs are pushed.
Early probes inherited private host guidance; their captures remain local and are excluded from publication.
Later probes used an isolated host profile with existing auth referenced by symlink, no copied global instructions, and explicit host-skill exclusions.
No credential contents are read into the project or capture receipts.

Complete clean duct records and CLI outputs are committed under `logs` and `trials`; all 16 annexed files were copied successfully to `con-hub`.
The [capture inventory](capture-inventory.json) records every original hash, size and mode: 87 publishable files and 30 locally held files from three early ambient-host runs.
Complete held bytes remain local and were not uploaded.
Metadata, stdout, stderr, usage, summary data and empty streams are retained.
No events were simulated, imported or adopted.
Success proves these observed sessions, not automatic trust or guaranteed capture of future sessions.
