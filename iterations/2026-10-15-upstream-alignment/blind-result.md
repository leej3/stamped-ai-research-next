# Creation and handoff plan

This exercise establishes a proposed sequence and acceptance criteria only. It does not establish that a research object is complete, that any remote is accessible, that the table or plot is correct, or that replay succeeds. No computation, repository modification, commit, publication, worker launch, or assessment has been performed. The existing project and scientific task are to be preserved.

The primary object is provisionally a study: its product is a scientific answer expressed as a table and plot. This follows the request, rather than an inspection of the project. The concrete repository URLs, task name, object root, input paths, commit IDs, snapshot ID, recorded environment name, assessor identity and scientific tolerances were not supplied; those are explicit handoff fields, not values to invent.

## 1. Establish the boundary and execution contract

At the future execution stage, inspect the existing root, README, root Pixi manifest, DataLad metadata, subdataset declarations, hooks and task implementation. Inventory the question, unchanged method, exact permitted inputs, access/licence terms, expected table and plot, parameters, resource limits and stopping conditions. Record which source modules and commits supply the inputs. Retrieve only the needed input slice, preserve raw data and metadata, and initialize children at their recorded commits.

Reuse the existing layout and root environment. Add only missing structure or ordinary experiment files; do not create a nested project. Keep code and small specifications in Git, and use effective annex attributes for large inputs, outputs and requested logs. Keep credentials in host providers and document replaceable access configuration. There is no reason to create concurrent writers or launch workers for this planning exercise.

Retain the selected immutable assessor's exact source, checklist and runtime identities independently of the evolving working-skill revision. If a baseline is needed for comparative grading, run that selected assessor against the named existing committed revision, with its output outside the assessed tree. Do not replace it with the moving sibling assessor merely because a skill links there.

## 2. Prepare the existing runnable slice

Confirm that the named task invokes the existing scientific calculation and generates both declared artifacts, creating its own output directories. Repair workflow gaps without changing the scientific method. Record the input, code, parameter and environment identities and expose needed analysis, validation and replay operations through the root task runner. Add missing dependencies through Pixi only if a demonstrated gap requires them; that change would require a newly identified validated environment, not a silent change to the supplied immutable snapshot.

Use the available immutable environment snapshot as the fixed dependency selection. Record its retrievable URL/ref plus immutable commit, the matching code revision, manifest identity, lock digest, environment name and supported host/platform. Restore the matching manifest and lock without solving again, then use `pixi install --locked -e <recorded-env>`. Do not create a redundant snapshot or merge the existing one into main. Preserve the project's chosen lock policy when subsequent authorized work produces a new final validated state.

Compose existing hooks rather than replacing them. Exercise preparation checks and relevant guard acceptance/rejection cases before relying on them. Commit executable inputs before scientific execution under project policy; preserve native DataLad run markers and structured records, with required attribution added without rewriting those records. Avoid unrelated commits while a recorded run is active.

## 3. Compute and validate only in the future authorized execution phase

The result has not yet been computed, so creation alone cannot establish a complete research object. Hand off the remaining scientific work to the full-research-loop procedure while keeping its scope to the existing task. Record the existing protocol and consequential assumptions; do not prescribe a different estimator, sample, uncertainty method or scientific design.

Run the smallest useful unit, which may be the entire small task, through native `datalad run --explicit` with explicit code/data/environment inputs and table/plot outputs. Record the calculation itself, not a task that recursively invokes `datalad run`. Any requested computation capture must be included among declared outputs, with complete final records retained before committing them; retain failures separately. Use requested logging only according to the project's actual policy.

Inspect source meanings, units, counts, missingness and output structure using checks appropriate to the existing contract. Compare meaningful values against independently derived expected values or a trusted reference, with tolerances declared before comparison. Retain the figure's editable source and inspect the rendered plot at intended size against the table, including labels, units and clipping. Successful exit status alone is insufficient. Retain the original accepted artifacts as the future replay comparison target.

## 4. Publish the complete object without touching shared main

Document both the GitHub history URL and the CON Hub annex URL, together with the `objects/demo-01` object branch and immutable published revision. Identify the annex remote UUID and confirm that the named Hub remote supports annex delivery. Publish every required child commit and child annex payload before publishing its parent gitlink; apply this ordering recursively. Include required inputs, outputs and retained execution records, rather than assuming that copying just the plot covers the object.

Adapt the supplied shared-repository recipe to the actual selected commit and named branch. The future commands have this shape, with placeholders resolved from inspected state:

```sh
git remote add hub <CON-Hub-repository-URL>  # reuse if already configured
# First publish required child histories and bytes, then the parent's history:
git push hub <object-commit>:refs/heads/objects/demo-01
git fetch hub git-annex:refs/remotes/hub/git-annex
pixi run git annex merge
pixi run git annex copy --to hub <explicit-required-annex-paths>
git push hub git-annex:refs/heads/git-annex
# Publish the intended object history to GitHub with an explicit destination:
git push <GitHub-remote> <object-commit>:refs/heads/objects/demo-01
```

Use the project's actual GitHub object ref if an existing policy specifies a different one; the request explicitly fixes the shared publication branch to `objects/demo-01`. Do not push the local branch under its default name, use `git annex sync hub`, force-update shared branches, or modify the Hub repository's main. If the annex metadata push races with another publisher, fetch and merge the updated location log and retry a fast-forward push. Publish a retrievable environment snapshot ref too, and document its immutable ID. Git history, payload transfer and location-log publication are distinct requirements; no completion claim follows from one alone.

## 5. Test recipient delivery and computational replay separately

Create a disposable clone outside the project from the documented GitHub history URL, select the exact published object revision, initialize recorded child commits and configure the documented Hub annex route. Fetch its annex metadata, retrieve the required keys specifically from Hub, and verify expected content hashes. Retrieve original outputs and any required logs separately from replay. Record clone URL, object/environment/child revisions, annex keys, named remote and retrieval receipts. Access must work with the intended recipient's privileges; maintainer-only access or same-host cached payloads do not establish that claim. State who can obtain access and any unresolved restricted components.

For replay, hold data, code, parameters and the supplied dependency selection fixed. Use a fresh workspace/installation on a compatible recorded platform, restore the matching manifest and lock, and synchronize before launching the computation. Select the intended checkout before an outer Pixi invocation; a running interpreter does not change when DataLad changes revisions. If historical checkout transitions are involved, use an explicit inner environment synchronization or otherwise select each intended state before launch.

Verify native discovery with `datalad rerun --report <run-commit>` and perform a genuine native rerun using the correct selected state. Keep original expected artifacts elsewhere, remove only declared generated paths in the disposable clone, and require newly generated output; an exit-zero no-op must fail. Do not delete input data or shared annex objects. Compare exact table identifiers/schema/labels, deterministic digests where meaningful, and declared numerical tolerances with explicit missing/nonfinite handling. Compare figure data and visually inspect the regenerated rendering; arbitrary pixel identity is not automatically the scientific criterion.

Retain replay command, revisions, environment/lock hash, host, caches/external services, regeneration evidence and comparison results. A fresh checkout on the same host supports same-host repeatability only. Scientific validation, annex delivery, native run discovery and numerical replay each need their own evidence.

## 6. Assess and hand off within scope

After the authorized computation, delivery and replay checks, assess the named finished commit with the same immutable assessor and checklist used for the baseline. Write assessment artifacts outside the assessed tree (or an already ignored location), preserve assessor/runtime identity, and cite evidence rather than intentions. Treat a retrievable immutable environment snapshot as environment evidence even though its lock is off the assessed branch. Use align-with-stamped-principles only to close supported in-scope workflow gaps, preserve scientific measurements, and reassess any changed committed object with the unchanged assessor.

The handoff packet should contain a concise README with the existing question and method, root/module boundary, input/access terms, executable task, code/run/environment identities, both publication routes, explicit branch/commit selection, recipient setup and retrieval commands, accepted table/plot locations, validation/replay receipts and known limits. Include before/after assessment references and item-level differences where actually measured. Keep numerical scientific validity separate from STAMPED conformance.

For this request, stop after delivering this plan. The next executor must resolve the named handoff fields and perform the checks before claiming a complete result. No worker or continuation is automatically authorized by the plan itself.

# Friction in the supplied instructions

1. **Planning boundary is indirect in the creation skill.** `create-stamped-project/SKILL.md` says, “Verify the complete path through one computation, output inspection and fresh-checkout replay” and “Commit the working slice”. Its handoff then says, “When results were requested, continue with [do-full-research-loop]”. The full-loop skill explicitly says “preserve planning-only scope” in its description, but the creation procedure does not state an equivalent planning-only exit. I treated the request's explicit planning restriction as controlling and described these as future steps. Otherwise the imperative creation steps could cause computation or commits during this exercise.

2. **The immutable assessor override must be carried across links.** The creation handoff says “use [align-with-stamped-principles] to assess and close scoped gaps”; align begins “Run [assess-alignment-with-stamped-principles] against the committed project”, using a sibling relative link. It also correctly says “use the same assessor and checklist for before/after comparisons” and “Do not silently change a frozen assessment to suit improvements to the working skills.” The supplied wording does not give an explicit parameter or dispatch rule for substituting a separately selected immutable assessor for that relative path, nor identify how its runtime is supplied. I resolved this by retaining the user-selected assessor throughout, but a concrete execution still needs its path/identity and invocation.

3. **Shared-remote publication requires deliberate adaptation.** The stack reference's “Verified recipe, with explicit refspecs throughout” hard-codes `git push hub master:refs/heads/objects/<name>`. The source branch might not be `master`; the immutable object commit is safer as the source. The recipe also assumes a fetchable `git-annex` branch and does not show handling concurrent publishers' metadata updates. The plan names the actual destination `objects/demo-01`, checks remote state, and requires a fast-forward metadata retry instead of force. This is adaptation of the recipe, not evidence that the remote has been tested.

4. **Publication ordering is spread across levels.** Creation says “publish required child commits and annex bytes before the parent pointer”, while the five-command recipe publishes object history before copying its payloads and location metadata. These can be reconciled: finish each child before the parent pointer, and do not declare the parent delivered until its own content and location records are published. The recipe does not show that recursive ordering or a final publication/completion boundary explicitly. The plan makes both explicit.

5. **The provided runner can weaken the native-record requirement.** `templates/run-recorded.sh` says “Falls back to a plain recorded commit when datalad is absent” and later runs `git add -A`, while `datalad-annex/SKILL.md` requires “Use native `datalad run --explicit` or `containers-run` with declared code, data, environment inputs and generated outputs.” The runner delegates options and does not insert `--explicit` itself. I would preserve/repair the existing declared-environment route, explicitly supply `--explicit`, and require native DataLad availability rather than accept that fallback as sufficient provenance for this task.

6. **The runner's environment shortcut is weaker than exact environment identity.** Its comment says it “declares the tracked environment specification as an input of every run”, but selects a single first matching file, including `pixi.toml`. For this request the exact validated lock is on an immutable snapshot, so a tracked manifest alone does not identify the dependency selection. The Pixi and DataLad skills supply the stronger rule: “record immutable code/snapshot IDs, lock hash and platform” and restore the matching manifest and retained lock. The plan explicitly requires that metadata and retrieval route rather than crediting the wrapper's environment-file detection alone.

7. **The prompt necessarily leaves scientific comparison details unresolved.** The validation reference requires “independent expected results or controls appropriate to the design” and says to “prespecify tolerances”; the request supplies neither scientific method detail nor expected values. These requirements are appropriate, but cannot be turned into numeric acceptance thresholds from this snapshot alone. The plan requires extracting the existing scientific contract before execution, preserves the method, and does not invent tests that could change the research question.

These are followability observations from the supplied snapshot. No assessment verdicts, remote checks or scientific conclusions are implied.
