---
name: task-subagent-spawn
description: Invoke when the Agent tool model parameter is about to be set or omitted for a subagent spawn / a brake evaluator subagent is about to be spawned / more than one subagent is about to be launched in a single batch / a second wave of subagents is about to be launched before the prior wave has reported. Provides the purpose-split model policy (brake evaluators pin an explicit sonnet-class floor, every other spawn omits the parameter and inherits the parent model) with its exhaustive category list, and the parallel-width cap of 5 in flight with its wave-sequencing binding condition and exemptions.
layer: L3-task
---

<subagent-model-policy>

# Subagent Model Policy

- **Brake evaluators set `model` explicitly; never let one inherit.** Floor and default = `sonnet`; a higher-class id (`opus`, `fable`) may be named but is not the default. A sub-floor parent otherwise lowers the evaluation floor silently. The two brake categories are brake-1 evaluators under `skills/evolution-parallel-agent-eval/SKILL.md`, and brake 2, the L1 root-criteria evaluator `adapter/claude/agents/l1-gate-eval.md` (its PASS verdict substitutes for human approval per `Evolution_Initiator_Autonomy`). The floor's detail — `haiku` prohibited, an id that cannot be positively classified as sonnet-class or above falls back to the literal `sonnet` — is in that skill's Constraint, phrased from brake 1's surface and extending to brake 2 unchanged.
- **Every other spawn omits `model` and inherits the parent; do not write the parent's id literally.** A literal rots the moment the parent tier changes, while omission tracks it without a source edit. The evaluator prohibition above does not reach here: for these categories inheriting the parent is the intent. The two non-brake categories are every delegation under `skills/task-subagent-delegation/SKILL.md` (implementation, operations, bounded read-only investigation), and `adapter/claude/agents/dialogue-evaluator.md` with its Codex port, spawned only on explicit human request. These four categories are exhaustive.
- **Set the model at the spawn call; do not edit the agent definition file to pin it.** In Claude Code the agent file body replaces the subagent's system prompt, so a frontmatter `model:` pin cannot be applied without also replacing identity — which mutates the probe-type observation target brake 1 depends on. The per-call parameter changes neither context nor identity.
- **The parent session's own tier is out of scope.** `docs/A.-Concept.md` states the documented minimum operating environment; this policy neither raises nor restates it.

</subagent-model-policy>

<parallel-width-cap>

# Parallel-Width Cap

- **Cap = 5 subagents in flight at once, counted in flight rather than per message.** Five in one message plus five in the next before the first wave returns is ten in flight while every message stays at five. Binding condition: do not launch a new batch until every subagent in the prior batch has completed and reported. Fan-out wider than 5 splits into sequential batches under the same rule.
- **Applies to every parallel delegation routed through `skills/task-subagent-delegation/SKILL.md`**: cross-parent-issue worktree parallelism and same-parent sub-issue parallelism (both defined in `adapter/claude/CLAUDE.md` Subagent_Delegation), and bounded read-only investigation fan-out. Exempt: `skills/evolution-parallel-agent-eval/SKILL.md`'s own N / M / P fan-out, separately bounded by that skill's Design Dimensions.
- **This cap is width, not depth.** `skills/task-subagent-prompt/SKILL.md` Bounded delegation governs whether a subagent may spawn its own children. The two axes neither extend nor narrow each other.
- **Nothing enforces this, and 5 is not a measured value.** No hook, counter, or gate exists; the parent applies the binding condition from procedure alone, which `rules/model/subtractive-structural-beauty.md` puts on the replace side of its procedure-vs-structure judgment. Structural enforcement and the bound's derivation are tracked in #1534.

</parallel-width-cap>
