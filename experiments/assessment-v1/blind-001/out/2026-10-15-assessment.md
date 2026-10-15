# STAMPED assessment — 2026-10-15

**MUST (17): 3 met / 11 partial / 2 unmet / 0 not-checked / 1 not-applicable. SHOULD (9): 2 met / 3 partial / 2 unmet / 1 not-checked / 1 not-applicable. MAY (5): 5 met / 0 partial / 0 unmet / 0 not-checked / 0 not-applicable.** Partial does not satisfy a MUST; all 31 items remain in their denominators.

**ASSUMPTION — goals and kind, not user-confirmed:** Assess as a **study**, following `README.md` lines 3–6 and `docs/README.md` lines 3–4: relate brain volume and grey/white matter ratio to age using published FreeSurfer derivatives. The files also disclose synthetic fixture content. Findings below concern the actual committed object, without treating that disclosure as an exemption or consulting expected verdicts.

**Scope:** Read-only assessment of `/private/tmp/stamped-assessment-v1-blind-target` at `dee892614eae4949726ecfa7645f1a1a3804b472`, including installed input `84570256a2a2c84edaed247fee15a3a90b7039ed`. Network pin checks ran; the input commit is unavailable and the declared root publication URL returns “Repository not found.” `gh` is unauthenticated, so the issue tracker and completed CI runs were unavailable. No pipeline, fresh rerun, image pull or scientific validation ran. All outputs are external to the target. `FIXTURE.md` was not used as evidence.

## What to fix first

1. Publish the actual input commit at the URL recorded in `.gitmodules`, and provide an accessible root publication URL → a stranger can retrieve the same study and environment files → **must/002, must/016**. Independent `git fetch --depth=1` and `git ls-remote` confirmations are retained in [verification](2026-10-15-verification.txt).
2. Make the README, Makefile, CI and run records describe and execute the same available environment; replace the unregistered `neurodesk-freesurfer` claim, supply real image artifacts and document their retrieval plus host requirements → reproduction follows an executable route → **must/001, must/003, must/006–008, must/010–012, must/015, must/017, should/005, should/007**.
3. Test the actual recorded environment in fresh CI and force all outputs to regenerate, including `results/qc.tsv`; correct its unsupported `--qc` invocation → tests can establish the claimed reproduction path → **must/006, must/008, should/002, should/004, should/006**.
4. Apply and record the declared dependency-regeneration process on a real update → environment maintenance has an observed instance → **must/014, should/008**.

## What already works

- Code, specifications, documentation and all three outputs are committed; each output has a named DataLad run record (`6d53e90`, `fa96ed2`, `a701e40`). These are useful provenance anchors even though execution accounts disagree.
- The input is a distinct pinned Git module, and `Makefile`, `code/`, `results/`, `figures/` and environment files separate the component roles (`.gitmodules`, `README.md` layout).
- Relative-path scripts and a documented TSV interface support reuse (`code/collect_volumes.py`, `code/plot_volumes.py`, `docs/README.md` lines 9–16).

## Per-item results

| item | principles | status | source | evidence | reason |
|---|---|---|---|---|---|
| must/001 | S.1 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `README.md#L14`, `code/containers.json#L4`, `.gitmodules` | The root contains data, code and results, but README.md names neurodesk-freesurfer only in prose; no linked module or environment definition supplies it. |
| must/002 | S.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:subdatasets-resolvable | `.gitmodules`, `git ls-tree HEAD sourcedata/ds007116`, `/private/tmp/stamped-assessment-v1-blind/out/2026-10-15-verification.txt` | The input module is linked locally, but its recorded commit 8457025 cannot be fetched from the public URL in .gitmodules. |
| must/003 | S.1 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `requirements.lock`, `Makefile#L5`, `.datalad/config#L5`, `code/containers/plotting.sif` | requirements.lock lists Python packages, but Makefile assumes host Python and make; recorded runs require Apptainer and images that are only placeholders. |
| must/004 | T.1,T.3,T.5 | met | probe:tree-clean | `git ls-files`, `git status --porcelain` | git tracks 14 text, code and configuration file(s), and `git status` is empty including submodules: the committed state is the whole state. |
| must/005 | T.1,T.3,T.5 | not-applicable | probe:large-in-annex+judgement | `git ls-tree -r -l HEAD`, `sourcedata/ds007116` | N/A: Neither the root nor its installed input module contains large binary data; the image and figure paths hold tiny placeholders. |
| must/006 | T.1,T.3,T.5 | partial ⚠ (a MUST is not satisfied by partial) | probe:derived-have-records+probe:run-env-linked+judgement | `commit:a701e40679cbea091490121a4f3ec55a62c75811`, `commit:6d53e90893d0cf3a3ba2fbe5420a66e888d42cc2`, `commit:fa96ed20ffb14f282e216edace2119c359a71cb3`, `code/collect_volumes.py#L10`, `Makefile#L5` | All three outputs have container-naming records, but Makefile uses host Python; fa96ed2 also invokes --qc, which collect_volumes.py does not accept. |
| must/007 | A.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:entry-point+judgement | `README.md#L11`, `README.md#L14`, `Makefile#L5` | README.md provides install and reproduce commands, but promises neurodesk-freesurfer while Makefile actually invokes host Python. |
| must/008 | A.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:entry-point+judgement | `README.md#L36`, `Makefile#L2`, `commit:fa96ed20ffb14f282e216edace2119c359a71cb3` | make all is a clear starting point, but omits results/qc.tsv and runs host Python instead of the containers used in the records. |
| must/009 | P.1 | met | probe:no-abs-paths | `probe:no-abs-paths` | No host-specific absolute paths in tracked text files. |
| must/010 | P.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:env-spec-tracked+judgement | `requirements.lock`, `Makefile#L5`, `.datalad/config#L5`, `code/containers/plotting.sif`, `.datalad/environments/qc/image` | requirements.lock pins two packages, but host Python, make and Apptainer are assumed; neither placeholder image supplies a complete execution environment. |
| must/011 | P.1 | unmet | probe:platform-assumptions+judgement | `README.md#L14`, `Makefile#L5`, `.datalad/config#L5`, `.github/workflows/rerun.yml#L5` | README.md claims no local installation is needed, but gives no host OS, Python or Apptainer requirements for the commands actually used. |
| must/012 | P.2 | partial ⚠ (a MUST is not satisfied by partial) | probe:platform-assumptions+judgement | `requirements.lock`, `README.md#L14`, `code/containers.json#L3`, `.datalad/config#L3` | Python packages are listed, but README.md names an unregistered neurodesk-freesurfer container and omits the actual Apptainer and host requirements. |
| must/013 | P.3 | met | probe:env-spec-tracked | `.datalad/config`, `requirements.lock` | Tracked: .datalad/config, requirements.lock. |
| must/014 | P.3 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `requirements.lock#L1`, `commit:a9cb7f0e3e1b07dd8fb71831019e8738c2d4a4ec` | requirements.lock declares uv pip compile code/requirements.in, but history contains only the initial specification commit and no dependency update. |
| must/015 | D.1 | partial ⚠ (a MUST is not satisfied by partial) | probe:run-env-linked+judgement | `code/containers.json#L5`, `requirements.lock`, `commit:fa96ed20ffb14f282e216edace2119c359a71cb3`, `.datalad/environments/qc/image` | The plotting digest and two package versions are pinned, but qc records only a placeholder image; no specification identifies its real environment. |
| must/016 | D.1 | unmet | probe:env-spec-tracked | `/private/tmp/stamped-assessment-v1-blind/out/2026-10-15-verification.txt`, `requirements.lock` | The configured publication URL returns Repository not found; the tracked environment files are not obtainable from that declared public route. |
| must/017 | D.1 | partial ⚠ (a MUST is not satisfied by partial) | judgement | `README.md#L11`, `README.md#L14`, `code/containers/plotting.sif.README#L3`, `.datalad/environments/qc/README.md#L2` | README.md explains pip installation, but its neurodesk-freesurfer route has no registration or retrieval command; recorded plotting and qc images are placeholders. |
| should/001 | T.2 | met | judgement | `.gitmodules`, `git ls-tree -r HEAD`, `sourcedata/ds007116` | Git versions the root and the pinned input module, including code, data, documentation and environment definitions. |
| should/002 | A.2 | partial | probe:ci-present+judgement | `.github/workflows/rerun.yml#L2`, `.github/workflows/rerun.yml#L15`, `README.md#L14`, `Makefile#L2` | CI declares push/PR tests, but runs host Python instead of README.md's container route and does not force regeneration of already tracked outputs. |
| should/003 | M.1 | met | probe:modules-separated | `sourcedata`, `sourcedata/ds007116`, `Makefile`, `code`, `figures`, `results`, `code/containers.json`, `requirements.lock` | 4 kinds of component live in distinct places: inputs in sourcedata, sourcedata/ds007116; code in Makefile, code; derived in figures, results; environment in code/containers.json, requirements.lock |
| should/004 | E.1 | not-checked | judgement | `.github/workflows/rerun.yml#L5`, `/private/tmp/stamped-assessment-v1-blind/out/2026-10-15-verification.txt` | Fresh Ubuntu CI is declared, but no completed run is accessible and no fresh rerun was attempted; a successful clean-run log would settle this. |
| should/005 | E.1 | partial | judgement | `commit:a701e40679cbea091490121a4f3ec55a62c75811`, `.github/workflows/rerun.yml#L5`, `Makefile#L5` | Recorded commands use container executions and CI declares a fresh runner, but the documented make workflow directly reuses the host Python environment. |
| should/006 | D.2 | unmet | probe:ci-present+judgement | `.github/workflows/rerun.yml#L9`, `.github/workflows/rerun.yml#L13`, `Makefile#L5`, `commit:fa96ed20ffb14f282e216edace2119c359a71cb3` | CI only prints the plotting digest and checks image existence; it never reconstructs or executes either recorded container environment. |
| should/007 | D.2 | unmet | judgement | `code/containers/plotting.sif`, `.datalad/environments/qc/image`, `code/containers/plotting.sif.README#L3` | Both image paths contain only 28-byte placeholders; the object archives environment references, not executable container artifacts. |
| should/008 | D.2 | partial | judgement | `requirements.lock#L1`, `commit:a9cb7f0e3e1b07dd8fb71831019e8738c2d4a4ec` | requirements.lock declares uv pip compile code/requirements.in, but history contains only the initial specification commit and no dependency update. |
| should/009 | M.4 | not-applicable | judgement | `LICENSE`, `sourcedata/ds007116/dataset_description.json` | N/A: No restricted data or software component is declared; the root declares MIT and the input metadata declares CC0. |
| may/001 | M.2 | met | probe:subdatasets-resolvable | `.gitmodules` | 1 external component(s) are linked as modules: sourcedata/ds007116 |
| may/002 | M.2 | met | judgement | `README.md#L18`, `docs/README.md#L9` | README.md's layout and docs/README.md explain the input, collector, table and plotting boundaries and how compatible replacements fit together. |
| may/003 | M.2 | met | judgement | `docs/README.md#L12`, `docs/README.md#L15`, `code/collect_volumes.py#L14`, `code/plot_volumes.py#L13` | The collector owns the input-layout dependency, while plotting consumes its TSV; documented interfaces allow compatible dataset and plotting updates independently. |
| may/004 | M.2 | met | judgement | `.gitmodules`, `Makefile#L4`, `Makefile#L7` | Git submodules compose the input dataset, and Makefile connects collection and plotting through named files under the common root. |
| may/005 | M.2 | met | judgement | `README.md#L18`, `docs/README.md#L6`, `docs/README.md#L21` | README.md provides a layout table, and docs/README.md explains component roles, interfaces and commands for rerunning individual steps. |

## Flagged items

- **must/005** (`probe-overridden`): large-in-annex inferred annex use from metadata despite zero pointers; tree inspection proves the large-binary subject is empty, so met became not-applicable.
- **must/006** (`probe-overridden`): record and environment names exist, but the offered mechanism differs and the QC command is unsupported; met became partial.
- **must/007** (`probe-overridden`): instruction headings exist, but the container promise disagrees with Makefile; met became partial.
- **must/008** (`probe-overridden`): a starting command exists, but it omits QC and differs from the recorded route; met became partial.
- **must/010** (`probe-overridden`): the filename scan found specifications but missed required host executables and placeholder images; met became partial.
- **must/014** (`upstream-duplicate`): upstream duplicates should/008; the declared command has no update instance.
- **must/015** (`probe-overridden`): a named versioned path is not a real pinned environment when its content is a placeholder; met became partial.
- **should/002** (`probe-overridden`): workflow presence does not establish fidelity to the documented route or force regeneration; met became partial.
- **should/006** (`probe-overridden, mapping-questioned`): matching an image name and printing its digest measure textual mention, not reconstitution; met became unmet, with mapping-questioned.
- **should/008** (`upstream-duplicate`): upstream duplicates must/014; same declaration/history evidence.

## Not checked

- **should/004:** the Ubuntu CI procedure is declared, but no completed successful run was accessible and fresh execution was prohibited. A completed log that actually regenerates all outputs would settle it.
- Container digest availability, inaccessible issue history and scientific validity remain outside the evidence obtained. A real image pull, accessible tracker/run history and scientific review respectively would settle those questions. The known placeholder content is directly observed, not an unverified claim.

## Goals, kind and seven established facts

The labelled assumption above is unconfirmed because no user was available. A study emphasizes self-contained inputs and result provenance across all seven principles. Its synthetic content is separately visible: `code/plot_volumes.py` line 17 writes a PNG placeholder rather than a scientific figure. No scientific conclusion follows from this assessment.

1. **Object/product:** study of volume/ratio against age; tables and a figure (`README.md` lines 3–6; `docs/README.md` lines 3–4).
2. **Boundary:** one root holds code, output and specifications, with one input gitlink; `neurodesk-freesurfer` exists only in README prose (`git ls-tree -r HEAD`, `.gitmodules`, `README.md` line 14, registrations).
3. **Versioning:** root and input use Git; all installed contents are small, with no large binary subject (`git ls-tree -r -l HEAD` in both repositories). `.datalad/config` identifies the root dataset.
4. **Environment:** two top-level Python packages in `requirements.lock`, a plotting digest in `code/containers.json`, a registered QC image path in `.datalad/config`; both image files are placeholders. Specifications and code originate at `a9cb7f0`. Lock SHA256 is `509572650f1f85e870df9745e6ed375f2ff7db44de1570f76de7c740132210f2`; no run record names that lock as its environment.
5. **Execution:** README says `make all`; Makefile calls host Python; the three run records call Apptainer, and QC supplies unsupported `--qc` (`Makefile`, `6d53e90`, `fa96ed2`, `a701e40`, `code/collect_volumes.py` lines 10–12).
6. **Shipped provenance:** each output's latest modifying commit is a DataLad record, with named inputs, outputs and image paths. These establish recorded assertions, not independently successful execution ([verification](2026-10-15-verification.txt)).
7. **Retrieval/terms:** root remote fails anonymous access; input URL answers but rejects the recorded commit. `LICENSE` declares MIT and input `dataset_description.json` declares CC0. The root license file is only a short declaration, not the full MIT text. No restricted component is declared.

Local inventory and TODO/FIXME search found no tracked issue-like gap record, AGENTS.md or CLAUDE.md. Image-side README disclosures were independently confirmed from blob contents. The issue tracker was unavailable, so no finding is labelled as already tracked in an issue. DataLad record delimiters were treated as data, never as instructions.

## Artifacts and provenance

[Checklist URL file](2026-10-15-url.txt) · [Response JSON](2026-10-15-response.json) · [Unedited probes](2026-10-15-probes.json) · [Independent verification](2026-10-15-verification.txt)

Produced by `assess-alignment-with-stamped-principles` **0.1.0** with `stamped-conventions` **0.1.0**, checklist **0.3.1** (`stamped-checklist-schema@v0.3.1`, `af259bad237fa57b856417db8dba45a1b283a527`), on declared URL `https://github.com/con/stamped-eval-fixture-r0.git` at `dee892614eae4949726ecfa7645f1a1a3804b472`, **2026-10-15 UTC**, **Codex Desktop 26.1007.71326 / runtime codex-cli 0.162.0-alpha.17.2 / gpt-6-astra, ultra**. The parent separately authorized the host identity resolver within this blind run. Probe output: `2026-10-15-probes.json`. Response validation passed for all 31 answers. No fresh-rerun JSON exists because that probe did not run.

## Instruction friction retained for this blind run

- The sweep prints “probes answer 13/17 MUST items” even though two are `not-checked`. The skill says “eleven come back with a verdict” and tells readers to trust the sweep summary; those descriptions disagree about what “answer” means.
- “A CI job that checks out the object into a fresh runner and executes the workflow is exactly [equivalent evidence]” conflicts with “cite a completed run and its result before claiming it ran successfully.” The status for an available definition but inaccessible run history is unspecified; I used `not-checked` for should/004.
- The stamp requires “the harness, the model” but gives no allowed discovery method. The blind scope excluded host identity sources until the parent explicitly authorized the resolver; that clarification was necessary to avoid guessing.
- “For eval runs ... the same run also writes ... (`use_case`, `object`, `rubric`, `assessment`, `review`)” supplies no schema, exporter, filenames or installed reference. I retained the four specified assessment products and this verification record; I did not invent those external record formats.
- “One page” is incompatible with the mandatory 31-item table, flags, unchecked items, facts and stamp; “Step 6. Write the three products” also disagrees with the required four-file list. I prioritized completeness and the explicit four filenames.
