---
globs:
alwaysApply: true
layer: L4-operations
---

<main-agent-procedures>

# Main Agent Procedures

<position>

## Position

Layer = L4 Operations Layer
Holds the operations procedures whose actor can be the main agent, on the resident rules surface instead of in an `operations-*` skill.
Requires = L4 Operations Layer
Load timing = always-on (the main agent is barred from the skill surface, so residency is the only way these reach their actor)

</position>

<the-bar-and-its-pair>

## The bar and its pair

`adapter/claude/CLAUDE.md` and `adapter/codex/AGENTS.md` each carry one line: `Main never reads operations skills directly when subagent is available.` It was never a standalone bar. #881 (`5333c16`) introduced it together with the move that pays for it — the PR review criteria went to the layer the main agent already holds. The intent is role separation (subagent executes procedures, main judges reports), not context economy.

The pair, stated once: **the bar holds only while every procedure whose actor can be the main agent has its canonical text on a surface the main agent may read.** Main-readable = every Li+ surface except `skills/operations-*/SKILL.md`. The subagent reads all of them, so a main-readable surface is also the surface both actors reach, and a canonical placed there needs no second copy for the other actor.

Maintenance rule, applied when an `operations-*` skill gains a requirement whose actor can be the main agent: move the canonical to a main-readable surface and leave a pointer in the skill. Two wrong repairs:

- copy the text to a main-readable surface and keep it in the skill as well — the second copy is what drifts.
- narrow the bar so the main agent may read the skill "when it is the actor" — that discards the role separation the bar exists for, and the requirement still sits on a pull surface its actor reaches only after it has begun acting.

Detection sign: a procedure written into an `operations-*` skill whose actor is mode-dependent, or stated as "the agent holding the merge decision". That agent is the parent in `auto` / `semi_auto` (`skills/task-subagent-delegation/SKILL.md` Rules), so the requirement lands where its actor cannot read it. Three measured instances preceded this rule (#1708, all in `semi_auto`): the self-review formal record and the merge procedure, both moved here, and the resume-prompt stop condition, which is not moved — its actor is the subagent and the parent was only the carrier, so the parent now carries a pointer instead of the literal (`skills/task-subagent-prompt/SKILL.md` Resume-phase authority boundary).

A fourth instance (#1714) is the first the sign caught rather than preceded: the review approval check, moved to Review approval check below. It was found while #1713 was implementing the sign itself and left outside that PR's scope, so the sign shipped holding a known positive. Being found by the sign changes nothing about the repair — the same maintenance rule applies, and the move is the same one.

</the-bar-and-its-pair>

<self-review-formal-record>

## Self-review formal record

Mandatory in every mode (trigger / semi_auto / auto).
Canonical. `skills/operations-on-pr-review/SKILL.md` owns the surrounding self-review flow and points here.
Actor = the parent in `auto` / `semi_auto`, the subagent in `trigger` (`skills/task-subagent-delegation/SKILL.md` Rules). In the first two it is the agent that merges. In `trigger` no agent merges (Merge Execution below), so the actor is fixed on the other side instead: the subagent's self-review lands before its own stop point, and nothing else stands on the PR after it.

After the internal self-review passes, that agent MUST post the outcome as a formal GitHub PR review:

  gh pr review {pr} -R {owner}/{repo} --comment --body "<summary of self-review outcome>"

Review body must include: acceptance-criteria check result, scope deviations (if any), next-step expectation (e.g. "awaiting human review" for trigger / minor-major semi_auto).
Rationale: creates an audit trail visible on the PR's Reviews tab, separating the AI's review record from PR author authorship.
Mechanism note: GitHub rejects `--add-reviewer` self-assignment silently; only `gh pr review --comment` works for PR author self-review records (empirically verified 2026-04-20 on PR #1095).

</self-review-formal-record>

<review-approval-check>

## Review approval check

Canonical. `skills/operations-on-pr-review/SKILL.md` owns which modes raise a human gate and points here for the procedure.
Actor = the parent, in every mode that raises the gate. In `semi_auto` the gate is the parent's own (`skills/task-subagent-delegation/SKILL.md` Rules, `Parent retains: ... review judgment`; `rules/operations/execution-mode.md` Mode matrix puts the human PR check on minor / major). In `trigger` the delegated subagent has already stopped at `awaiting human review` (`skills/operations-on-pr-review/SKILL.md` Delegated-subagent stop condition, settled by #1715), so the approval arrives after its session has ended. No mode puts a subagent at this wait, which is why one canonical on a main-readable surface covers both.

Fires after self-review passes: in `semi_auto` for minor / major, in `trigger` for every PR. `auto` raises no human gate and never reaches here.

Prefer webhook over polling.
  if mcp__github-webhook-mcp available:
    poll get_pending_status every 60 seconds
    on pull_request_review pending: list_pending_events -> get_event for this PR -> check state -> mark_processed
  else:
    Wait = human signals review done (do not poll).
    On signal:
      gh pr view {pr} -R {owner}/{repo} --json reviewDecision --jq '.reviewDecision'

The decision read here is the input to the review judgment, not the judgment. What APPROVED and CHANGES_REQUESTED release is `skills/task-pr-review-judgment/SKILL.md`, the main agent's own surface and already main-readable; on APPROVED the mode's merge path is Merge Execution below. Do not restate either here; the second copy is what drifts.

</review-approval-check>

<merge-execution>

## Merge Execution

Canonical. `skills/operations-on-merge/SKILL.md` held this until #1708 and was removed rather than reduced to a pointer: at its own firing moment — `self-review has passed and the mode gate has cleared` — it had no reader both present and permitted. In `auto` / `semi_auto` the agent standing there is the parent, which the bar keeps out. In `trigger` the gate clears after the delegated subagent's session has ended (`skills/operations-on-pr-review/SKILL.md` Delegated-subagent stop condition), so no subagent is there to invoke it either. The removal does not rest on settling which actor merges in `trigger`: whichever agent is put there reads this file, because `rules/**` loads without being invoked, which is strictly more available than the skill it replaces. #1715 has since settled the question — no agent is put there, the merge being a GitHub handoff (Merge Execution below) — and the removal is untouched by that, which is what not resting on it means.

Merge executor is AI in every mode (trigger / semi_auto / auto). That is the actor axis; the act it names differs by mode. Reading the act off the actor is what split the source until #1715 — four surfaces, two on each reading of who merges in `trigger`.

- `semi_auto` / `auto` = direct merge. AI runs `gh pr merge` (no `--auto`) after all preconditions pass: self-review, the mode-specific human gate, and the mergeable state check below.
- `trigger` = handoff. The AI act is enabling GitHub auto-merge (`gh pr merge --auto`) at PR creation, and GitHub fires the merge itself on human approval. No agent runs a merge command at the approval moment, and none stands there to run one (`skills/operations-on-pr-review/SKILL.md` Delegated-subagent stop condition).

Authoritative for the mode split: `rules/operations/operations.md` PR auto-merge policy.

Pre-merge mergeable state check (direct-merge path only — in `trigger` the PR sits with auto-merge armed until GitHub can merge it, and no agent is present to check):
  gh pr view {pr} -R {owner}/{repo} --json mergeStateStatus --jq '.mergeStateStatus'
  CLEAN -> proceed to merge.
  BEHIND -> git fetch origin main && git rebase origin/main && git push --force-with-lease -> restart [CI Loop] from step1.
  CONFLICTING -> attempt rebase: git fetch origin main && git rebase origin/main
    if rebase succeeds: git push --force-with-lease -> restart [CI Loop] from step1
    if rebase fails: git rebase --abort -> comment on issue -> escalate to human
  BLOCKED or UNKNOWN -> wait and recheck (GitHub may still be computing)

Merge strategy:
  Default = squash (repo convention), in every mode.
  Direct-merge path = AI runs: gh pr merge {pr} -R {owner}/{repo} --squash
  Handoff path (`trigger`) = the same strategy is fixed on the `--auto --squash` enable at PR creation.
  Deviation from squash = AI pauses and asks human.

Parent close condition: closed automatically on merge via issue reference.

Real device test:
Merge first. Then test on main. Not a merge gate.

Post-merge observation for L1 source changes:
After merging any PR touching L1 Model Layer source (any file with `layer: L1-model` frontmatter, typically `rules/model/*`), apply `rules/operations/operations.md` Post-L1-Merge Runtime Observation. Separate observable axis from Real device test above (AI internal judgment behavior vs external process output).

</merge-execution>

</main-agent-procedures>
