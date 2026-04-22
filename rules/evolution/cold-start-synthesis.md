---
globs:
alwaysApply: true
layer: L2-evolution
---

# Cold-start Synthesis

Trigger = session start, after Li+config.md execution completes.
Action:
1. Read docs/a.- (decision log index) and recent Li+ source changes.
2. Synthesize the current Li+ state = active tag, recent structural shifts, unresolved threads.
3. Report synthesis to human as the opening orientation — conditional on non-redundancy with hook-surfaced material.

Steps 1-2 are internal AI priming. They run every session regardless of what the hook already emitted.
Step 3 is conditional output gating, not unconditional report.

Hook coordination:
`on-session-start.sh` already persists and surfaces at session open: recent release tags, decision log index head, self-evaluation log head, cold-start rule literal. These items are already visible to the human via the hook payload.

Operational criterion:
- hook-surfaced items = silent (do not re-report what the human already received from the hook)
- unique synthesized insight = speak (structural shift, unresolved thread, cross-artifact pattern not visible in the raw hook material)
- no unique insight after synthesis = silent skip

Goal = do not depend on human re-explanation of Li+ state at session start, while avoiding duplicate orientation noise. The hook handles raw surfacing; step 3 handles synthesis delta only.

Scope = Li+ state, not workspace task state. Workspace-specific orientation follows the adapter's own startup path.
