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

</the-bar-and-its-pair>

<self-review-formal-record>

## Self-review formal record

Mandatory in every mode (trigger / semi_auto / auto).
Canonical. `skills/operations-on-pr-review/SKILL.md` owns the surrounding self-review flow and points here.
Actor = the agent holding the merge decision: the parent in `auto` / `semi_auto`, the subagent in `trigger` (`skills/task-subagent-delegation/SKILL.md` Rules).

After the internal self-review passes, that agent MUST post the outcome as a formal GitHub PR review:

  gh pr review {pr} -R {owner}/{repo} --comment --body "<summary of self-review outcome>"

Review body must include: acceptance-criteria check result, scope deviations (if any), next-step expectation (e.g. "awaiting human review" for trigger / minor-major semi_auto).
Rationale: creates an audit trail visible on the PR's Reviews tab, separating the AI's review record from PR author authorship.
Mechanism note: GitHub rejects `--add-reviewer` self-assignment silently; only `gh pr review --comment` works for PR author self-review records (empirically verified 2026-04-20 on PR #1095).

</self-review-formal-record>

<merge-execution>

## Merge Execution

Canonical. `skills/operations-on-merge/SKILL.md` held this until #1708 and was removed rather than reduced to a pointer: at its own firing moment — `self-review has passed and the mode gate has cleared` — it had no reader both present and permitted. In `auto` / `semi_auto` the agent standing there is the parent, which the bar keeps out. In `trigger` the gate clears after the delegated subagent's session has ended (`skills/operations-on-pr-review/SKILL.md` Delegated-subagent stop condition), so no subagent is there to invoke it either. The removal does not rest on settling which actor merges in `trigger`: whichever agent is put there reads this file, because `rules/**` loads without being invoked, which is strictly more available than the skill it replaces.

Merge executor is AI in every mode (trigger / semi_auto / auto).
AI runs `gh pr merge` after all preconditions pass (self-review + mode-specific human gate, and mergeable state check). GitHub auto-merge handoff (`--auto`) is used only in trigger mode, where it fires merge on human approval; semi_auto and auto modes use AI direct merge (no `--auto`). Authoritative: `rules/operations/operations.md` PR auto-merge policy.

Pre-merge mergeable state check:
  gh pr view {pr} -R {owner}/{repo} --json mergeStateStatus --jq '.mergeStateStatus'
  CLEAN -> proceed to merge.
  BEHIND -> git fetch origin main && git rebase origin/main && git push --force-with-lease -> restart [CI Loop] from step1.
  CONFLICTING -> attempt rebase: git fetch origin main && git rebase origin/main
    if rebase succeeds: git push --force-with-lease -> restart [CI Loop] from step1
    if rebase fails: git rebase --abort -> comment on issue -> escalate to human
  BLOCKED or UNKNOWN -> wait and recheck (GitHub may still be computing)

Merge strategy:
  Default = squash (repo convention).
  All modes = AI runs: gh pr merge {pr} -R {owner}/{repo} --squash
  Deviation from squash = AI pauses and asks human.

Parent close condition: closed automatically on merge via issue reference.

Real device test:
Merge first. Then test on main. Not a merge gate.

Post-merge observation for L1 source changes:
After merging any PR touching L1 Model Layer source (any file with `layer: L1-model` frontmatter, typically `rules/model/*`), apply `rules/operations/operations.md` Post-L1-Merge Runtime Observation. Separate observable axis from Real device test above (AI internal judgment behavior vs external process output).

</merge-execution>

</main-agent-procedures>
