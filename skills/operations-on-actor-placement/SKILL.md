---
name: operations-on-actor-placement
description: Invoke when an `operations-*` skill is about to gain or change a requirement / a procedure is about to move between `rules/operations/main-agent-procedures.md` and an `operations-*` skill / an adapter line is found naming an operations skill as where policy lives. Provides the actor criterion for placement and the relocation maintenance rule.
layer: L4-operations
---

<actor-placement>

# Actor Placement

Upkeep of the bar and its pair (`rules/operations/main-agent-procedures.md` The bar and its pair): the bar holds only while every procedure whose actor can be the main agent has its canonical text on a surface the main agent may read. Reader = the agent editing Li+ source: the implementation subagent, or the main agent under the substrate-absence fallback (`skills/task-subagent-delegation/SKILL.md` Autonomy).

<actor-criterion>

## Actor criterion

An actor can be the main agent when one of the two below holds. The main agent's freedom to execute something itself does not count (implementation and operations are delegated by default, `skills/task-subagent-delegation/SKILL.md` Rules).

- the procedure is on `Parent retains` (`skills/task-subagent-delegation/SKILL.md` Rules). Read that list at its own granularity: `issue management` there is scoped by its parenthetical to non-state lifecycle labels, type, maturity, marker and close, so a requirement about issues that is none of those is not reached by it.
- the procedure needs a surface no subagent has — an utterance to the human, a human-facing report, or the user-turn boundary. Escalating a stop to the human is not that surface on its own (`skills/operations-on-ci/SKILL.md` does not fire on its own escalate-to-human line). What fires is a prescribed human-facing utterance the agent must author, or a go-sign the agent must receive and act on where no already-resident gate carries it.

Both are read per requirement, not per file: one skill can hold a firing clause and a non-firing one.

</actor-criterion>

<maintenance-rule>

## Maintenance rule

Applied when an `operations-*` skill gains a requirement whose actor can be the main agent: move the canonical to a main-readable surface and leave a pointer in the skill. Two wrong repairs:

- copy the text to a main-readable surface and keep it in the skill as well.
- narrow the bar so the main agent may read the skill "when it is the actor".

Detection sign: a procedure written into an `operations-*` skill whose actor is mode-dependent, or stated as "the agent holding the merge decision" — that agent is the parent in `auto` / `semi_auto` (`skills/task-subagent-delegation/SKILL.md` Rules).

Where the literal's actor is the subagent and the main agent is only the carrier, the canonical stays in the skill and the main agent carries a pointer to it instead (`skills/task-subagent-prompt/SKILL.md` Resume-phase authority boundary). Move the canonical when the main agent has to execute it; leave a pointer when the main agent only has to convey it.

Relocating the canonical is half the move. The second half: narrow the skill's `description` to the reader it retains. Retained readers are the subagent, and the main agent under the substrate-absence fallback (`skills/task-subagent-delegation/SKILL.md` Autonomy). A skill that retains neither reader is deleted, not left as a pointer — unless it is the resolution target of a pointer that cannot itself be edited, in which case it stays as a redirect stub whose description declares it non-invocable rather than naming any moment.

Adapter literals that point the main agent at an operations skill are repaired the same way where they are editable. `adapter/claude/CLAUDE.md` and `adapter/codex/AGENTS.md` `## Optional Webhook Notification Flow` is byte-frozen: do not edit it to satisfy the bar, and carry the redirect in `rules/operations/main-agent-procedures.md` instead. Detection sign that this shape is present: an adapter line naming an operations skill as where policy lives, in the same sentinel section as the bar.

</maintenance-rule>

</actor-placement>
