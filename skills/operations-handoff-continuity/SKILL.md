---
name: operations-handoff-continuity
description: Invoke when token / session / model boundary may interrupt work, or when judging whether to leave intermediate state in local workspace vs push to linked branch — enforces that handoff source of truth is issue body + linked branch + commits/PR, never local-only.
layer: L4-operations
---

<HandoffContinuity>

If token/session/model boundary may interrupt work = push useful intermediate state to the linked personal branch.
Handoff source of truth = issue body + linked branch + commits/PR.
Do not leave meaningful progress only in local workspace or chat memory.

</HandoffContinuity>
