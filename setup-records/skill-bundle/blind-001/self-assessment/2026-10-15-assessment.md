# STAMPED assessment: synthetic paired study

Assumption, not separately confirmed with the human: this is a **study** answering the supplied synthetic paired-change question, with local independent-clone delivery as the requested distribution scope.
The task prompt and committed README establish those goals.

MUST: **16 met / 1 partial / 0 unmet / 0 not-checked**, denominator 17.
SHOULD: **3 met / 4 partial / 1 unmet / 0 not-checked / 1 not-applicable**, denominator 9.
MAY: **3 met / 1 partial / 0 unmet / 0 not-checked / 1 not-applicable**, denominator 5.

## What to improve if this study is maintained

1. Run the documented dependency-update process on the first substantive dependency change; creation is not evidence of a later update (`must/014`, duplicate `should/008`).
   No meaningless update was invented to satisfy a rubric.
2. Add recurring replay/lock rebuild checks if this becomes a maintained project (`should/002`, `should/006`).
   The requested one-time local trial already passed.
3. Archive actual package artifacts and establish persistent remote delivery if distribution requirements grow (`should/007` and broader D.1 coverage).
   Current delivery is local only and package restoration uses public registries/caches.
4. Create a fresh environment per ordinary computation if repeated analyses are introduced (`should/005`); the delivered replay already creates an independent checkout and environment.

These are retained limits or future scope, not missing actions in the authorized tiny trial.
The separate license extra remains unmet: no public license is asserted for user-supplied material, and no public publication was requested.

## What works

- Native DataLad run `00103044a25dddb01aabda261fef06754ca5987a` records explicit inputs and outputs; exact lock hash in `protocol/environment.json` matches ordinary-Git snapshot `472fbcfdcde21a4120a29ee2e6e3b13d8e72f67c`, exactly one commit above task `9c15dfe23eb8ad03ac6420f381ca645a6c3dddda`.
- Independent recipient retrieved all **10 initially absent annex payloads**, including logs; native `rerun --report` discovered the run; a real replay from the input revision regenerated all **5 scientific artifacts with exact SHA-256 agreement**.
  Evidence: [delivery receipt](../stamped-paired-independent-ZWuYEl-delivery2/receipt.json) and [commands](../stamped-paired-independent-ZWuYEl-delivery2/commands.json).
  The clone and its environment were fresh; the host and download caches were shared.
- Original semantics, analytical oracle, a second SciPy paired-t route, seven invalid-input controls, rendered figure inspection, and exercised run guard are retained in the committed research object.

## Per-item evidence

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | met | judgement | `README.md`, `commit:472fbcfdcde21a4120a29ee2e6e3b13d8e72f67c` | All scientific inputs, code, specifications, results, and logs belong to one Git/DataLad object; exact lock is retained in its snapshot branch. |
| must/002 | S.1 | met | probe:subdatasets-resolvable+judgement | `data/README.md`, `data/paired.csv` | Original task input is a small Git-tracked CSV under data; no external dataset or external input path is required. |
| must/003 | S.1 | met | judgement | `pixi.toml`, `/tmp/stamped-paired-independent-ZWuYEl-delivery2/receipt.json` | NumPy, SciPy, Pandas, Matplotlib, DataLad, git-annex and duct are declared in the root Pixi environment and restored in the recipient. |
| must/004 | T.1,T.3,T.5 | met | probe:tree-clean | `git ls-files`, `git status --porcelain` | git tracks 27 text, code and configuration file(s), and `git status` is empty including submodules: the committed state is the whole state. |
| must/005 | T.1,T.3,T.5 | met | probe:large-in-annex | `git ls-tree -r -l HEAD`, `.datalad/config` | git-annex carries the binary content (10 pointer(s) tracked) and no binary blob over 10 MiB is in git. |
| must/006 | T.1,T.3,T.5 | met | probe:derived-have-records+probe:run-env-linked+judgement | `commit:00103044a25dddb01aabda261fef06754ca5987a`, `protocol/environment.json`, `commit:472fbcfdcde21a4120a29ee2e6e3b13d8e72f67c`, `data/README.md` | Native run records code, data, protocol, and manifest; the protocol records the exact lock hash, matching the retained snapshot. Raw supplied CSV is an input, not a derived file. |
| must/007 | A.1 | met | probe:entry-point | `README.md` | README.md has an install/usage/reproduce section. |
| must/008 | A.1 | met | probe:entry-point+judgement | `README.md`, `pixi.toml`, `/tmp/stamped-paired-independent-ZWuYEl-delivery2/receipt.json` | README identifies pixi run record and pixi run replay; actual native execution and fresh replay exercise those named tasks. |
| must/009 | P.1 | met | probe:no-abs-paths+judgement | `code/analyze.py`, `code/replay.py`, `evidence/run.json` | Runtime data paths are relative. Absolute paths flagged by the probe are retained execution receipts and failure traces, not required host locations. |
| must/010 | P.1 | met | probe:env-spec-tracked+judgement | `pixi.toml`, `README.md`, `code/run-recorded.sh` | Scientific/tooling packages are declared. Git, Pixi and POSIX shell are documented bootstrap requirements. The alleged missing tool is is ordinary English in a template comment. |
| must/011 | P.1 | met | probe:platform-assumptions+judgement | `README.md`, `pixi.toml` | README documents Apple Silicon macOS >=14, POSIX shell, Git/Pixi, install network or caches, and optional authoring hooks; no cluster, GPU or credentials required. |
| must/012 | P.2 | met | probe:platform-assumptions+judgement | `README.md`, `pixi.toml` | README supplies host requirements and the manifest lists scientific and provenance dependencies; one macOS arm64 platform is explicitly claimed. |
| must/013 | P.3 | met | probe:env-spec-tracked | `pixi.toml`, `code/run-recorded.sh#L23` | Tracked: pixi.toml. |
| must/014 | P.3 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `README.md`, `git log -- pixi.toml` | README gives executable pixi add/update, revalidation, and snapshot procedures; this new study has no post-baseline dependency update in its history. |
| must/015 | D.1 | met | probe:run-env-linked+judgement | `commit:472fbcfdcde21a4120a29ee2e6e3b13d8e72f67c`, `protocol/environment.json`, `/tmp/stamped-paired-independent-ZWuYEl-delivery2/receipt.json` | Exact validated lock is an ordinary Git snapshot one commit above the task; recipient restored it and installed with --locked before both checkout states. |
| must/016 | D.1 | met | probe:env-spec-tracked+judgement | `/tmp/stamped-paired-independent-ZWuYEl-delivery2/receipt.json`, `README.md` | Within requested local scope, an independent clone fetched the snapshot and installed its exact environment. No persistent public hosting or remote-host access is claimed. |
| must/017 | D.1 | met | judgement | `README.md`, `/tmp/stamped-paired-independent-ZWuYEl-delivery2/receipt.json` | README documents clone, exact lock extraction, locked installation, annex get, and native replay, with immutable IDs in the delivery receipt. |
| should/001 | T.2 | met | judgement | `.datalad/config`, `.gitattributes`, `git log --all` | Git and DataLad/git-annex share one history for source, protocol, environment, results, and task logs. |
| should/002 | A.2 | partial | probe:ci-present+judgement | `code/validate.py`, `/tmp/stamped-paired-independent-ZWuYEl-delivery2/receipt.json`, `/tmp/stamped-paired-independent-ZWuYEl-assessment/2026-10-15-probes.json` | Known-input validation and one fresh replay passed, but the disposable study has no recurring CI or scheduled workflow testing. |
| should/003 | M.1 | met | probe:modules-separated | `data`, `code`, `results`, `pixi.toml` | 4 kinds of component live in distinct places: inputs in data; code in code; derived in results; environment in pixi.toml |
| should/004 | E.1 | met | judgement | `/tmp/stamped-paired-independent-ZWuYEl-delivery2/receipt.json`, `/tmp/stamped-paired-independent-ZWuYEl-delivery2/commands.json` | A fresh independent checkout built its own locked Pixi environment and regenerated outputs; this is same-host isolation, not a second OS or machine. |
| should/005 | E.1 | partial | judgement | `code/replay.py`, `pixi.toml` | Replay creates a disposable checkout and environment; ordinary record/analyze tasks reuse the project's environment rather than create one per invocation. |
| should/006 | D.2 | partial | probe:ci-present+judgement | `/tmp/stamped-paired-independent-ZWuYEl-delivery2/receipt.json`, `/tmp/stamped-paired-independent-ZWuYEl-assessment/2026-10-15-probes.json` | The exact saved environment was restored and tested once; no recurring rebuild service or schedule exists for this disposable local study. |
| should/007 | D.2 | unmet | judgement | `commit:472fbcfdcde21a4120a29ee2e6e3b13d8e72f67c`, `README.md` | The lock archives exact package identities, not executable package artifacts; reinstallation relies on package registries or an existing Pixi cache. |
| should/008 | D.2 | partial | judgement | `README.md`, `git log -- pixi.toml` | README gives executable pixi add/update, revalidation, and snapshot procedures; this new study has no post-baseline dependency update in its history. |
| should/009 | M.4 | not-applicable | judgement | — | N/A: the supplied synthetic input and required software contain no restricted-access component. |
| may/001 | M.2 | not-applicable | probe:subdatasets-resolvable+judgement | — | N/A: no external dataset or source-code module; third-party packages are managed through Pixi rather than Git submodules. |
| may/002 | M.2 | met | judgement | `README.md`, `code/compute.py` | README maps input, code, protocol, output, log, and environment boundaries; raw and derivative artifacts are separately addressable. |
| may/003 | M.2 | partial | judgement | `code/analyze.py`, `code/validate.py` | Data, computation, validation, and results are separated, but code intentionally fixes the five-row study paths and known-input contract rather than support independently versioned modules. |
| may/004 | M.2 | met | judgement | `pixi.toml`, `code/compute.py`, `code/run-recorded.sh` | The Pixi task graph and compute entry point compose analysis and validation under one native DataLad execution with explicit boundaries. |
| may/005 | M.2 | met | judgement | `README.md`, `protocol/protocol.md` | README documents structure, task entry points, environment restoration, and local replay; protocol explains the scientific input/output contract. |


## Flagged judgments

- `stamped-checklist:must/002`: probe-overridden — Original task input is a small Git-tracked CSV under data; no external dataset or external input path is required.
- `stamped-checklist:must/006`: probe-overridden — Native run records code, data, protocol, and manifest; the protocol records the exact lock hash, matching the retained snapshot.
  Raw supplied CSV is an input, not a derived file.
- `stamped-checklist:must/008`: probe-overridden — README identifies pixi run record and pixi run replay; actual native execution and fresh replay exercise those named tasks.
- `stamped-checklist:must/009`: probe-overridden — Runtime data paths are relative.
  Absolute paths flagged by the probe are retained execution receipts and failure traces, not required host locations.
- `stamped-checklist:must/010`: probe-overridden — Scientific/tooling packages are declared.
  Git, Pixi and POSIX shell are documented bootstrap requirements.
  The alleged missing tool is is ordinary English in a template comment.
- `stamped-checklist:must/014`: upstream-duplicate — README gives executable pixi add/update, revalidation, and snapshot procedures; this new study has no post-baseline dependency update in its history.
- `stamped-checklist:must/015`: probe-overridden — Exact validated lock is an ordinary Git snapshot one commit above the task; recipient restored it and installed with --locked before both checkout states.
- `stamped-checklist:must/016`: probe-overridden — Within requested local scope, an independent clone fetched the snapshot and installed its exact environment.
  No persistent public hosting or remote-host access is claimed.
- `stamped-checklist:should/002`: probe-overridden — Known-input validation and one fresh replay passed, but the disposable study has no recurring CI or scheduled workflow testing.
- `stamped-checklist:should/006`: probe-overridden — The exact saved environment was restored and tested once; no recurring rebuild service or schedule exists for this disposable local study.
- `stamped-checklist:should/008`: upstream-duplicate — README gives executable pixi add/update, revalidation, and snapshot procedures; this new study has no post-baseline dependency update in its history.
- `stamped-checklist:may/001`: probe-overridden — N/A: no external dataset or source-code module; third-party packages are managed through Pixi rather than Git submodules.

The untouched probe output is retained.
In particular, it mistakes original `data/paired.csv` for a derivative, does not recognize the documented Pixi tasks, treats English `is` in the supplied wrapper's comment as a missing executable, and treats a historical working-directory field as an execution dependency.
Its environment heuristic does not follow the selected manifest + protocol lock hash + separate snapshot policy.
These were resolved from the actual committed files and native run/recipient evidence; raw probe output was not edited.

## Not checked and limits

No checklist item remains unanswered.
No different physical host or OS was tested.
No external publication, remote service access, recurring CI, or package-binary archival was performed.
There are no linked modules or issue tracker to contact.
The optional `fresh_rerun.py` assessment probe was not invoked: the authorized native DataLad replay already supplies stronger equivalent execution evidence.
No optional fresh-rerun-probe JSON is claimed.

## Scientific validity is separate

The committed analysis gives mean after-minus-before change **1.8**, 95% t CI **[0.7611493663164324, 2.8388506336835677]**, df=4.
Independent expected quantities agree within 1e-12.
This is a correct calculation for the five supplied synthetic pairs, conditional on a hypothetical independent normal sampling model; it does not establish population generalizability or causality.
STAMPED properties do not supply those scientific assumptions.

## Goals, kind, URL, and provenance

Primary kind: study.
Boundary: committed task and its exact-lock snapshot, with separately retained native recipient history and evaluation receipts.
Distribution scope: same-host local clone, as requested.

[Checklist app URL](2026-10-15-url.txt) · [response JSON](2026-10-15-response.json) · [unedited probes](2026-10-15-probes.json).

Produced by `assess-alignment-with-stamped-principles` 0.1.0 with `stamped-conventions` 0.1.0, checklist 0.3.1 (`stamped-checklist-schema@v0.3.1`, `af259bad237fa57b856417db8dba45a1b283a527`), on `/tmp/stamped-paired-independent-ZWuYEl` at commit `9c15dfe23eb8ad03ac6420f381ca645a6c3dddda`, 2026-10-15 UTC, Codex Desktop 26.1007.71326 / codex-cli 0.162.0-alpha.17.2 / gpt-6-astra (ultra).
The assessment is agent self-assessment with scripted probes, not an independent human review.
Its JSON validates all 31 pinned answers.
