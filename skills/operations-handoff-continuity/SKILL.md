---
name: operations-handoff-continuity
description: Invoke when a token or session or model boundary may interrupt work / judging whether to leave intermediate state in the local workspace instead of pushing it to the linked branch. Enforces that the handoff source of truth is the issue body plus linked branch plus commits and PR, never local-only.
layer: L4-operations
---

<handoff-continuity>

# Handoff Continuity

If token/session/model boundary may interrupt work = push useful intermediate state to the linked personal branch.
Handoff source of truth = issue body + linked branch + commits/PR.
Do not leave meaningful progress only in local workspace or chat memory.

</handoff-continuity>
