Repository context is sufficient to coordinate the workflow. It supplies the scientific question, condition assignments, isolated launcher, judging procedure, version pins, and retention rules. Formal execution still needs a fixed total budget and resolution of the task-depth inconsistency below.

I inspected tracked coordinator files and selected NARPS guidance only; I did not open iteration records, experiment results, or prior chats, and made no changes.

The current freeze candidate is:

| Component | Revision |
|---|---|
| Coordinator | `589ebf7d29a03775ed8101a3bffe661d95f97d7f` |
| NARPS study | `af60b4cf3d28319a0a676eb19270ea9c7dcbb3e7` |
| Study `input/` tree | `a484f41db2095ef116f08d359f9b95ad41981698` |
| Explicit skills | `fdf31feecb4ee37a8487188447d61c006b11099f` |
| Assessor source | `d867c1d04bbb58b3b0f64122ebd5f76bd8e5a7ca` |
| Assessor environment | `3552d5003a2485b6405805236d5c54e7ed42f097` |

My first round would be:

1. Start from a fresh shallow coordinator clone. Freeze the scientific brief, 54 participant maps and metadata, evaluation guidance, condition prompts, common environment and lock, model/runtime/settings, access, launch-order randomization, duplicate-judgment selection, and total budget. Use `gpt-6-luna` with high reasoning and record the actual resolved identity.
2. Preflight all four conditions, then run **12 fresh independent workers**: three each for `baseline`, `discover-general`, `discover-science`, and `stamped-explicit`, with varied launch order. Supply only committed inputs, common resources, and assigned skills. Keep discovery failures and spontaneous baseline discovery in their assigned arms.
3. Preserve each scientific result commit. Obtain **16 independent judgments**: one per object, plus a second judgment of one randomly selected object per condition. Judges receive the original scientific task and frozen guidance; inspect, check remote retrieval, and perform one replay without repairing the object.
4. Compare scientific adequacy separately from STAMPED evidence, retaining `not-checked`, failures, costs, uncertainty, worker variability, and judge disagreement. Record evidence motivating generic skill changes in the coordinator’s iteration directory.
5. Revise skills only between iterations. Three iterations imply 36 workers and 48 object judgments, followed by assessment of the whole workshop. The third iteration tests final skills without further tuning.

Workers choose their group models, quality checks, software, figures, and justified anatomical identification. The fixed scientific requirement is positive gain-related vmPFC inference in the equal-indifference group, conditional on the supplied AO86 effect estimates, using whole-brain correction. They must account for coefficient scaling, fixed upstream modeling, and absent participant variance maps.

These are the documented execution commands, once the supplied host configuration and fresh checkout are ready:

```sh
pixi run git submodule update --init -- studies/narps skills assessment
pixi run launcher-tests
pixi run assessment-check

pixi run launch \
  --host-config "$HOST_CONFIG" \
  --study studies/narps \
  --base "$FROZEN_COORDINATOR" \
  --branch codex/narps-i1-r01 \
  --clone-path "$WORKERS/narps-i1-r01" \
  --evidence "$EVIDENCE/narps-i1-r01/launch" \
  --condition baseline \
  --capture-execution \
  --review-seconds 5400 \
  --seconds 0

pixi run judge \
  --host-config "$HOST_CONFIG" \
  --repo "$WORKERS/narps-i1-r01" \
  --base "$RESULT_COMMIT" \
  --branch codex/narps-i1-r01-judge01 \
  --study studies/narps \
  --reference studies/narps/coordinator-guidance/judging.md \
  --evidence "$EVIDENCE/narps-i1-r01/judgment-01"
```

`--prepare-only` provides a launch preflight, but **it still creates repositories, installs environments, and writes receipts**; it is unsuitable for this read-only trial. Duct capture is explicitly requested by `prompt.md`. The 90-minute setting records a review point; it does not terminate the worker.

Two issues remain before formal execution:

- **Budget:** the repository specifies repetitions but no total cost/time budget. The coordinator must freeze that before launching.
- **Task depth:** NARPS readiness says `ready: true` and describes a compact task; judging guidance says task-depth validation remains pending, while the workshop targets roughly 45 minutes. This needs a deliberate designation or corrected guidance. No scientific conclusion should be inferred from readiness.

After judging, I would retain receipts in later experiment commits without changing the judged commit, preserve each final lock on its environment branch, publish required annex payloads, register experiments under the study’s `results/`, and publish child revisions before updating parent gitlinks. The launcher handles individual runs; scheduling, duplicate selection, comparison, and skill revision remain coordinator responsibilities.
