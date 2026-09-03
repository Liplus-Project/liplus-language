---
name: operations-on-pr-review
description: Invoke when a delegated subagent has reached its stop condition and needs that mode literal / a delegated subagent is about to report to the parent and must confirm where its session ends / subagent capability is unavailable and the parent is executing operations directly. Holds the canonical delegated-subagent stop condition split by mode; the surrounding PR review flow lives in `rules/operations/main-agent-procedures.md`.
layer: L4-operations
---

<pr-review>

# PR Review

Delegated-subagent stop condition (canonical, split by mode):
  if execution_mode == auto or execution_mode == semi_auto:
    Stop at `PR open + CI green`. The subagent neither runs nor posts the self-review; it reports there and exits.
    This point is reached twice, and the literal above is the whole condition at both:
      first pass  - the issue's change is implemented. The parent then runs brake 1 at the position fixed by
                    `rules/evolution/initiator-autonomy.md` Merge brake.
      second pass - the parent has resumed this subagent onto a brake round's evaluator findings on the PR;
                    it has adjudicated them, posted each accept or reject and its reason as a comment on that
                    thread, and pushed what it accepted. Reaching CI green again ends this pass. If nothing was
                    accepted, the same point is reached with no new commit, the adjudication comment posted all
                    the same. The parent may then open a further round, which ends at this same point; the
                    number of them is capped
                    (`skills/evolution-parallel-agent-eval/SKILL.md` Procedure, Round trips).
    Adjudication belongs to the resumed subagent, not to the parent
    (`rules/evolution/initiator-autonomy.md` Merge brake, Adjudication actor). The parent self-reviews and
    merges after the last pass.
  if execution_mode == trigger:
    Stop at `PR open + auto-merge enabled + CI green + self-review posted + awaiting human review`.
    Self-review precedes the human gate in every mode and the subagent is its actor in this mode, so it lands
    before the stop point. Merge fires later via GitHub auto-merge after human approval; the subagent's session
    ends before that.
  Other surfaces point here. Do not restate the condition; the second copy is what drifts.

Why this condition alone is held here, while the flow around it is not: the literal's actor is the subagent,
and the parent is only its carrier at the delegation moment (`skills/task-subagent-prompt/SKILL.md` Resume-phase
authority boundary), which is the shape `rules/operations/main-agent-procedures.md` The bar and its pair resolves
by leaving the canonical in the skill. The surrounding flow resolves the other way — its actor is the parent in
`auto` / `semi_auto` — so the self-review mandate, the review basis, the self-review procedure, the mode-specific
human gate, and the follow-through on deferred items all live at `rules/operations/main-agent-procedures.md`
PR review. Do not restate them here; the second copy is what drifts.

</pr-review>
