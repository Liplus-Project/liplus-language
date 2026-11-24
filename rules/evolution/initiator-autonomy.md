---
globs:
alwaysApply: true
layer: L2-evolution
---

<initiator-autonomy>

# Initiator Autonomy

Detailed scope spec for `Evolution_Initiator_Autonomy` (`adapter/claude/CLAUDE.md` Autonomy section).

<self-evolution-pr-definition>

## Self-evolution PR definition

A PR is a "self-evolution PR" when both conditions hold:

1. It is filed under the `Evolution_Initiator_Autonomy` initiator path (AI-authored issue → AI implementation).
2. It changes a governed surface in the `LI_PLUS_REPO` repository (criterion below).

Both, and neither alone. A PR that fails condition 2 is not a self-evolution PR at all, however plainly it sits on the initiator path.

### Governed surface (condition 2)

Condition 2 holds for a changed file when both are true of it: it constrains how the system behaves, and reading is the only thing that would catch it being wrong. What closes condition 2 is that criterion, not the entries below; the entries are the cases that have come up.

- `rules/**/*.md`, `skills/**/SKILL.md`, `adapter/**/*`, `Li+update.md` — prose the agent loads and runs as its own instruction.
- `tests/**` and `.github/workflows/**` — the enforcement backstop: the contract tests, and the workflow that runs them and produces the check. It is executed code no check stands behind.

The excluded surfaces, each by the property that excludes it = `skills/evolution-parallel-agent-eval/SKILL.md` Governed surface exclusions. Open it before a PR on the initiator path is ruled out of brake 1.

A changed file the criterion places on neither side is on the firing side.

Prose in a `tests/**` file = `skills/operations-on-docs-ownership/SKILL.md` Prose in tests.

</self-evolution-pr-definition>

<scope-l2-l6-improvement-issues-in-general>

## Scope ("L2-L6 improvement issues in general")

In-scope = any Li+ source file with `layer: L2-evolution` / `L3-task` / `L4-operations` / `L5-notifications` / `L6-adapter` frontmatter, plus `docs/`, `adapter/`, `scripts/`, `tests/`, `.github/`, and `Li+update.md`.

A path enters this list on a measured run of the initiator path on it, not on the prospect of one. Initiator path here means who decided to file and implement, not which account pushed: a change carrying the same account but whose own body records it as Master-originated is not such a run.

Out-of-scope = L1 Model Layer source (`layer: L1-model`, typically `rules/model/`), which routes to `skills/evolution-l1-update-gating/SKILL.md`. The `layer: L1-model` frontmatter wins over directory location — an L1-tagged file sitting under a directory this list blankets is out-of-scope all the same.

</scope-l2-l6-improvement-issues-in-general>

<merge-brake>

## Merge brake

Each item below is held at the location it names and is not restated here; no figure from `skills/evolution-parallel-agent-eval` (the evaluator count or any other) is carried into this rule:
- `skills/operations-on-pr-review/SKILL.md` Delegated-subagent stop condition = the stop condition at the firing moment.
- `adapter/claude/CLAUDE.md` and `adapter/codex/AGENTS.md` Subagent_Delegation = the host mechanism resuming the author.
- `skills/evolution-parallel-agent-eval/SKILL.md` = Procedure (the operational form of what the evaluators receive; routing at step 3's reporting destination and steps 4 and 6 to 8; loop exit and recurrence stop at step 8), Report shape, Constraint (the evaluator-count floor; Findings are posted to the PR by the evaluator = the parent's conduct while the exchange passes and its one read of the whole thread at the exit), what one round trip is, and a rejection's standing inside the loop.

**Position (canonical)**: the brake runs after CI green and before the merge gate. It does not run before commit. Firing moment = the delegated subagent's report at its stop condition. The evaluators receive the PR URL, a pushed commit SHA, and a green CI run URL, never a path in the parent's clone. Other surfaces point here; do not restate the position.

The rule effect measurement between that CI green and this brake (`skills/evolution-rule-effect-measurement/SKILL.md` Application point, Position on the self-evolution PR pipeline) is not a brake: nothing about it gates the merge, and the eval runs whether or not a run was taken.

**Adjudication actor (canonical)**: findings are adjudicated by the implementation subagent, resumed with its context intact. The parent does not adjudicate. The parent's remaining share is spawning the evaluators, resuming the author, self-review, and the merge decision. Spawn depth stays 1. The evaluators are spawned by the parent, not by the author, and neither the resumed author nor an evaluator spawns anything.

**Channel (canonical)**: the exchange between evaluator and author runs on the PR's own comment thread, and the parent is not in the path. The round trips carry no cap.

**brake 1 (always)**: every self-evolution PR runs `skills/evolution-parallel-agent-eval`, and nothing exempts one. This rule owns that gate declaration only; what the eval is made of is the skill's. `brake 1` is a name, not an ordinal: it is the only brake at the merge gate and stays uniform across it — an L1 Model Layer change adds no brake of its own, and semi_auto patch-auto-merge does not bypass it. Human = final judge stands unchanged on its own axis (`rules/model/role-separation.md`).

</merge-brake>

<recovery-axis>

## Recovery axis

GitHub revert (`gh pr revert` / UI button) is the primary undo path for reversible changes (Li+ source edits, docs, wiki entries).

Out-of-scope for the autonomous loop = changes whose effect cannot be undone by git revert: release publish, Latest flip, tag delete, merged-PR delete, force push to shared branch, external API calls with non-idempotent effect. These remain on the existing human gate regardless of the brake 1 outcome.

</recovery-axis>

<existing-maintenance-rules-still-apply>

## Existing maintenance rules still apply

- `skills/evolution-l1-update-gating` long-horizon observation requirement is unchanged.
- `rules/operations/execution-mode.md` mode matrix applies on top (semi_auto patch-auto-merge ↔ minor/major human review).
- `rules/evolution/promotion-judgment.md` noise-floor gate is unchanged.

</existing-maintenance-rules-still-apply>

</initiator-autonomy>
