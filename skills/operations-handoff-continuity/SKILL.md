---
name: operations-handoff-continuity
description: Invoke when a subagent judges whether intermediate state may stay in the local workspace instead of being pushed to the linked branch / a delegated run may be interrupted before its stop condition is reached / subagent capability is unavailable and the parent is executing operations directly. Pointer only - the Handoff continuity canonical lives in `rules/operations/main-agent-procedures.md`.
layer: L4-operations
---

<handoff-continuity>

# Handoff Continuity

Pointer. Canonical = `rules/operations/main-agent-procedures.md` Handoff continuity: the push-on-interruption rule, the source-of-truth set, and the prohibition on local-only progress all live there.

Why the canonical is not here: the main agent is an actor too. It holds the issue body (`skills/task-subagent-delegation/SKILL.md` Rules puts `issue management` on `Parent retains`), the aggregated findings comment, and the resume target for an implementation subagent — and `chat memory`, which the canonical names, is its alone. A canonical held here would sit where one of its two actors cannot read it (`rules/operations/main-agent-procedures.md` The bar and its pair).

The subagent still reaches the canonical — `rules/**` loads for it without invocation — so nothing it needs at its own boundary is lost by the move.

</handoff-continuity>
