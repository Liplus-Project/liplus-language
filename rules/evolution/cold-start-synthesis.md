---
globs:
alwaysApply: true
layer: L2-evolution
---

# Cold-start Synthesis

Trigger = session start, after Li+config.md execution completes.
Action:
1. Read docs/Decision-Structure.md (decision structure index) and recent Li+ source changes.
2. Synthesize the current Li+ state = active tag, recent structural shifts, unresolved threads.
3. Report synthesis to human as the opening orientation — conditional on non-redundancy with hook-surfaced material.

Steps 1-2 are internal AI priming. They run every session regardless of what the hook already emitted.
Step 3 is conditional output gating, not unconditional report.

Hook coordination:
`on-session-start.sh` persists and surfaces at session open: recent release tags, decision structure index head, self-evaluation log head, cold-start rule literal. Since build-2026-05-11 the hook emits material in diff-only mode (matcher = startup): only sections whose body changed since the previous startup invocation are re-emitted. The cold-start rule literal is always re-anchored regardless of diff state.

Hook emission states (matcher = startup):
- full emit = first session after install, fail-safe (state missing / unreadable / sha256 unavailable), or every section changed. All sections shown.
- diff-only = some sections changed since prior session. Only changed sections shown.
- no-new-material marker = no section changed. A single "No new orientation material since last session" line is emitted (silent skip is intentionally avoided so the human can still observe the session boundary).

Hook emission states (matcher = resume / clear / compact):
- Only the cold-start rule literal is re-anchored. The work context is continuous; the diff-only set is not re-evaluated.

Operational criterion (AI side, step 3 gating):
- hook-surfaced items = silent (do not re-report what the human already received from the hook, regardless of full / diff-only / marker state)
- unique synthesized insight = speak (structural shift, unresolved thread, cross-artifact pattern not visible in the raw hook material)
- no unique insight after synthesis = silent skip
- diff-only state with the no-new-material marker = silent skip is the natural outcome; the marker itself is the human-facing acknowledgement that a session boundary occurred

Goal = do not depend on human re-explanation of Li+ state at session start, while avoiding duplicate orientation noise. The hook handles raw surfacing (with diff-only economy on startup); step 3 handles synthesis delta only.

Scope = Li+ state, not workspace task state. Workspace-specific orientation follows the adapter's own startup path.

## Self-Evolution Observation Surface

Self-evolution observation entries (`memory/self-evolution-observation.md`, format defined in `rules/evolution/memory-entry-format.md` Self-Evolution Observation Format) are surfaced at cold-start when their check window opens.

Surface targets:
- `next_check` <= today and `verdict_state` == `pending` -> surface as "observation due"
- `expires` < today and `verdict_state` == `pending` -> surface as "observation overdue, human judgment needed"

Surfacing is observation, not auto-action. Verdict transitions (settle / revert / supersede) still go through the explicit lifecycle defined in the format spec.

Material gathering and concrete surfacing logic belong to the adapter cold-start path (parallel to the existing memory scan + Decision-Structure index head emit). This section defines only the behavior contract.

Silent skip when the observation file is absent or no entries are due.
