---
globs:
alwaysApply: true
layer: L2-evolution
---

<initiator-autonomy>

# Initiator Autonomy

Detailed scope spec for `Evolution_Initiator_Autonomy` (`adapter/claude/CLAUDE.md` Autonomy section). Declares: what counts as a self-evolution PR, what scope it covers, the two-stage brake mechanism, and the recovery axis. The adapter side carries the autonomy declaration; this rule carries the operational detail.

<self-evolution-pr-definition>

## Self-evolution PR definition

A PR is a "self-evolution PR" when both conditions hold:

1. It is filed under the `Evolution_Initiator_Autonomy` initiator path (AI-authored issue → AI implementation).
2. It modifies Li+ source — `rules/**/*.md`, `skills/**/SKILL.md`, or `adapter/**/*` files in the `LI_PLUS_REPO` repository.

Bug-fix PRs on user repos and PRs filed by human at the issue stage are outside this definition (different gate surfaces apply).

</self-evolution-pr-definition>

<scope-l2-l6-improvement-issues-in-general>

## Scope ("L2-L6 improvement issues in general")

In-scope = any Li+ source file with `layer: L2-evolution` / `L3-task` / `L4-operations` / `L5-notifications` / `L6-adapter` frontmatter, plus `docs/`, `adapter/`, `scripts/`, `hooks/`, and `Li+update.md`.

Out-of-scope = L1 Model Layer source (`layer: L1-model`, typically `rules/model/`), which routes to brake 2.

</scope-l2-l6-improvement-issues-in-general>

<two-stage-brake>

## Two-stage brake

- **brake 1 (always)**: every self-evolution PR runs `skills/parallel-subagent-eval` before the commit/merge gate. N=1 self-check is prohibited; minimum N=3.
- **brake 2 (L1 only)**: when the PR touches L1 Model Layer source, human review is required on top of brake 1. "Touches L1" = any added / modified / deleted line in an L1 file within the PR diff (single-line edits count). Mixed PRs (L1 + non-L1) trigger brake 2 for the whole PR; cannot be split-merged to bypass. semi_auto patch-auto-merge does not bypass this gate (see `rules/operations/execution-mode.md` L1 brake 2 override).

</two-stage-brake>

<post-merge-axis>

## Post-merge axis

The brakes above are pre-merge gates. Post-merge short-window observation (5-min runtime check for L1 changes) runs on a separate axis — see `rules/operations/operations.md` Post-L1-Merge Runtime Observation.

</post-merge-axis>

<recovery-axis>

## Recovery axis

GitHub revert (`gh pr revert` / UI button) is the primary undo path for reversible changes (Li+ source edits, docs, wiki entries).

Out-of-scope for the autonomous loop = changes whose effect cannot be undone by git revert: release publish, Latest flip, tag delete, merged-PR delete, force push to shared branch, external API calls with non-idempotent effect. These remain on the existing human gate regardless of brake 1 / brake 2 outcome.

</recovery-axis>

<existing-maintenance-rules-still-apply>

## Existing maintenance rules still apply

- `skills/evolution-l1-update-gating` long-horizon observation requirement is unchanged.
- `rules/operations/execution-mode.md` mode matrix applies on top (semi_auto patch-auto-merge ↔ minor/major human review; L1 brake 2 override).
- `rules/evolution/promotion-judgment.md` noise-floor gate is unchanged.

</existing-maintenance-rules-still-apply>

<boundary-clarification>

## Boundary clarification

This rule covers the initiator axis of the Sheepdog three-axis framing (`docs/G.-Sheepdog-Engineering.md`). Position axis (`.claude/` as internal tools) and modifier axis (AI edits Li+ source) are already on AI; the `Evolution_Initiator_Autonomy` declaration completes the third axis.

</boundary-clarification>

</initiator-autonomy>
