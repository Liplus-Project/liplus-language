---
globs:
alwaysApply: true
layer: L2-evolution
---

<initiator-autonomy>

# Initiator Autonomy

Detailed scope spec for `Evolution_Initiator_Autonomy` (`adapter/claude/CLAUDE.md` Autonomy section). Declares: what counts as a self-evolution PR, what scope it covers, the merge brake, and the recovery axis. The adapter side carries the autonomy declaration; this rule carries the operational detail.

<self-evolution-pr-definition>

## Self-evolution PR definition

A PR is a "self-evolution PR" when both conditions hold:

1. It is filed under the `Evolution_Initiator_Autonomy` initiator path (AI-authored issue → AI implementation).
2. It changes a governed surface in the `LI_PLUS_REPO` repository (criterion below).

Both, and neither alone. A PR that fails condition 2 is not a self-evolution PR at all, however plainly it sits on the initiator path.

Bug-fix PRs on user repos and PRs filed by human at the issue stage are outside this definition (different gate surfaces apply).

### Governed surface (condition 2)

Condition 2 holds for a changed file when both are true of it: it constrains how the system behaves, and reading is the only thing that would catch it being wrong. What closes condition 2 is that criterion, not the entries below; the entries are the cases that have come up.

- `rules/**/*.md`, `skills/**/SKILL.md`, `adapter/**/*`, `Li+update.md` — prose the agent loads and runs as its own instruction.
- `tests/**` and `.github/workflows/**` — the enforcement backstop: the contract tests, and the workflow that runs them and produces the check. It is executed code no check stands behind.

Excluded, each by the property that excludes it:

- **Record surfaces** — `docs/**`, the wiki, `README.md`, `LICENSE`, `NOTICE`. Read on demand as a record of past judgment or as description. A file carrying a line that can go stale with no change inside the repo is not covered by this exclusion, whichever of its lines a change touches; the criterion above places it.
- **Executed code a check stands behind** — `scripts/**`, `.github/scripts/**`. A defect surfaces as a raised exception in the calling turn or as a red check. The backstop itself (`tests/**`) is on the firing side above. Executed code this exclusion does not cover is reached by the default below, not by this bullet.

A changed file the criterion places on neither side is on the firing side.

### Prose in `tests/**`

Binds every line of prose — docstring, comment — in a `tests/**` file. What such prose may state is what that test observes, and where the claim it tests is fixed; a norm of its own it may not state. Where a norm is needed, point at the surface that holds it (`rules/**`, `skills/**`) instead of restating it.

A statement about system behavior carries the conditions it was observed under. A word reaching past them — `permanently`, `always`, `never`, `any` — is written out, or the conditions are written in beside it.

Out of scope: the test's intent, reproduction steps, and references to a prior issue / PR / commit. This states nothing about them.

`docs/` is in Scope below and excluded here, save a file the Record surfaces bullet hands back to the criterion. The two lists run on different axes — Scope is what the AI may initiate, condition 2 is what brake 1 gates. Do not read either membership off the other.

</self-evolution-pr-definition>

<scope-l2-l6-improvement-issues-in-general>

## Scope ("L2-L6 improvement issues in general")

In-scope = any Li+ source file with `layer: L2-evolution` / `L3-task` / `L4-operations` / `L5-notifications` / `L6-adapter` frontmatter, plus `docs/`, `adapter/`, `scripts/`, `tests/`, `.github/`, and `Li+update.md`. Hooks get no entry of their own: they live at `adapter/claude/hooks/` and `adapter/codex/hooks/`, which `adapter/` already covers.

A path enters this list on a measured run of the initiator path on it, not on the prospect of one. Initiator path here means who decided to file and implement, not which account pushed: a change carrying the same account but whose own body records it as Master-originated is not such a run. Naming a path records authority that was exercised; it does not extend any.

Out-of-scope = L1 Model Layer source (`layer: L1-model`, typically `rules/model/`), which routes to `skills/evolution-l1-update-gating/SKILL.md`. The `layer: L1-model` frontmatter wins over directory location — an L1-tagged file sitting under a directory this list blankets is out-of-scope all the same.

</scope-l2-l6-improvement-issues-in-general>

<merge-brake>

## Merge brake

**Position (canonical)**: the brake runs after CI green and before the merge gate. It does not run before commit. Firing moment = the delegated subagent's report at its stop condition (`skills/operations-on-pr-review/SKILL.md` Delegated-subagent stop condition); implementation is always delegated (`skills/task-subagent-delegation/SKILL.md` Rules), so the parent reaches the brake holding a report, not a working tree. What the evaluators receive is fixed by that position: the PR URL, a pushed commit SHA, and a green CI run URL (never a path in the parent's clone) (`skills/evolution-parallel-agent-eval/SKILL.md` Procedure carries the operational form). Other surfaces point here; do not restate the position.

One thing stands between that CI green and this brake: the rule effect measurement, on a PR whose firing condition holds. Its position, its firing condition, its actor, and how a run that could not be taken is recorded are `skills/evolution-rule-effect-measurement/SKILL.md` Application point, Position on the self-evolution PR pipeline; none of that is restated here. What this surface holds about it is that it is not a second brake: nothing about the measurement gates the merge, the eval runs whether or not a run was taken, and brake 1 below stays the only brake at the gate.

**Adjudication actor (canonical)**: findings are adjudicated by the implementation subagent, resumed with its context intact (`adapter/claude/CLAUDE.md` and `adapter/codex/AGENTS.md` Subagent_Delegation carry the host mechanism). The parent does not adjudicate. The parent's remaining share is spawning the evaluators, resuming the author, self-review, and the merge decision.

**Channel (canonical)**: the exchange between evaluator and author runs on the PR's own comment thread. The evaluator posts its findings there itself and the author answers there, and the parent is not in the path — it does not compose either artifact, does not consolidate, and does not read what passes while it passes, save the recurrence test it runs at each round boundary (the skill's Procedure step 8). Its share of the exchange is scheduling: it wakes the author onto new findings, and it opens or closes the next round or stops the loop for the human. The parent still reads the whole thread once, at the exit, and its self-review and merge judgment are formed there (`rules/operations/execution-mode.md`, `rules/model/role-separation.md`).

The routing that makes this hold — where an evaluator posts its findings, how the author is woken onto them, what the author writes back, and where a round ends — is `skills/evolution-parallel-agent-eval/SKILL.md` Procedure (the reporting destination at step 3, then steps 4 and 6 to 8), with its Report shape fixing the artifacts each produces. Those steps are conditional; do not restate them here.

The round trips carry no cap: what ends the loop is the skill's Procedure step 8, whose recurrence stop hands the loop to the human, and convergence does not rest on `skills/model-loop-safety` held by an actor inside the loop. What ends the loop, what one round trip is, and what standing a rejection has inside the loop are the skill's; none of them is restated here.

Spawn depth stays 1. The evaluators are spawned by the parent, not by the author, and neither the resumed author nor an evaluator spawns anything.

**brake 1 (always)**: every self-evolution PR runs `skills/evolution-parallel-agent-eval`. That is the part this rule owns — the gate declaration: the brake is on, on every such PR, and nothing exempts one. What the eval is made of is the skill's: the evaluator-count floor (its Constraint) and the loop's exit and recurrence stop (its Procedure step 8), each carrying the conditions that qualify it. Neither is restated here and no figure from either is carried.

`brake 1` is a name, not a position in a sequence: it is the only brake at the merge gate, and nothing is waiting behind it. It stays uniform across that gate — an L1 Model Layer change adds no brake of its own, and semi_auto patch-auto-merge does not bypass it. What an L1 change carries instead sits on other axes and, except for the last, before this point: the observation threshold at issue formation (`skills/evolution-l1-update-gating/SKILL.md`), the execution-mode human gate for minor / major (`rules/operations/execution-mode.md`), and the post-merge runtime observation (Post-merge axis below). Human = final judge stands unchanged on its own axis (`rules/model/role-separation.md`); release-axis and irreversibility human gates are untouched (Recovery axis below).

</merge-brake>

<post-merge-axis>

## Post-merge axis

The brake above is a pre-merge gate. Post-merge short-window observation (5-min runtime check for L1 changes) runs on a separate axis — see `rules/operations/operations.md` Post-L1-Merge Runtime Observation.

</post-merge-axis>

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

<boundary-clarification>

## Boundary clarification

This rule covers the initiator axis of the Sheepdog three-axis framing (`docs/G.-Sheepdog-Engineering.md`). Position axis (`.claude/` as internal tools) and modifier axis (AI edits Li+ source) are already on AI; the `Evolution_Initiator_Autonomy` declaration completes the third axis.

</boundary-clarification>

</initiator-autonomy>
