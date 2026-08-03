---
globs:
alwaysApply: true
layer: L2-evolution
---

<cold-start-synthesis>

# Cold-start Synthesis

Trigger = session start, after Li+config.md execution completes.
Action:
1. Read docs/Decision-Structure.md (decision structure index) and recent Li+ source changes.
2. Synthesize the current Li+ state = active tag, recent structural shifts, unresolved threads.
3. Report synthesis to human as the opening orientation — conditional on non-redundancy with hook-surfaced material.

Steps 1-2 are internal AI priming. They run every session regardless of what the hook already emitted.
Step 3 is conditional output gating, not unconditional report.

Hook coordination:
`on-session-start.sh` persists and surfaces at session open: decision structure index head, rules/ tree (fetch address table for cold-start-loaded rules cache), recent release tags, open in-progress issues, self-evaluation log head, promotion candidates, cold-start rule literal. Since build-2026-05-11 the hook emits material in diff-only mode (matcher = startup): only sections whose body changed since the previous startup invocation are re-emitted. The cold-start rule literal is always re-anchored regardless of diff state.

Hook emission states (matcher = startup):
- full emit = first session after install, fail-safe (state missing / unreadable / sha256 unavailable / node unavailable), or every section changed. All sections shown. The four reasons are the bash port's set. The PowerShell port parses JSON natively so it has no node dependency, and it calls SHA256 unconditionally with no availability guard, so neither of those two reasons can fire there: its fail-safe set is the two state-file reasons alone.
- diff-only = some sections changed since prior session. Only changed sections shown.
- no-new-material marker = no section changed AND no self-evolution observation entry was surfaced. A single "No new orientation material since last session" line is emitted (silent skip is intentionally avoided so the human can still observe the session boundary). A surfaced observation entry (see Self-Evolution Observation Surface below) counts as material even though it carries no section key, so the marker is suppressed for that session; pairing an overdue entry with "no new material" would be self-contradictory output.

Hook emission states (matcher = resume / clear / compact / fork):
- Only the cold-start rule literal is re-anchored. The work context is continuous; the diff-only set is not re-evaluated, and the state file is not updated.

Operational criterion (AI side, step 3 gating):
- hook-surfaced items = silent (do not re-report what the human already received from the hook, regardless of full / diff-only / marker state)
- unique synthesized insight = speak (structural shift, unresolved thread, cross-artifact pattern not visible in the raw hook material)
- no unique insight after synthesis = silent skip
- diff-only state with the no-new-material marker = silent skip is the natural outcome; the marker itself is the human-facing acknowledgement that a session boundary occurred
- release Latest position = silent, even though it reads as synthesis over the hook-surfaced tag list. When the tag list shows the Latest flag on a prior version, do NOT surface "Latest behind / flip pending" as unique insight. Latest flip is human-gated on multi-session real-device observation, so an AI-side surfacing of it is a go-sign solicitation, not orientation (`skills/operations-on-release/SKILL.md` Release Completion Report Discipline holds the same discipline at the completion-report moment)

Goal = do not depend on human re-explanation of Li+ state at session start, while avoiding duplicate orientation noise. The hook handles raw surfacing (with diff-only economy on startup); step 3 handles synthesis delta only.

Scope = Li+ state, not workspace task state. Workspace-specific orientation follows the adapter's own startup path.

<self-evolution-observation-surface>

## Self-Evolution Observation Surface

Self-evolution observation entries (`memory/self-evolution-observation.md`, format defined in `rules/evolution/memory-entry-format.md` Self-Evolution Observation Format) are surfaced at cold-start when their check window opens.

Surface targets:
- `next_check` <= today and `verdict_state` == `pending` -> surface as "observation due"
- `expires` < today and `verdict_state` == `pending` -> surface as "observation overdue, human judgment needed"

Both conditions normally hold at once for an expired entry (`next_check` is typically also in the past). Overdue wins: the entry is surfaced once, as overdue only. Overdue is the axis carrying the escalation, and presenting one entry on both axes is noise.

Surfacing is observation, not auto-action. Verdict transitions (settle / revert / supersede) still go through the explicit lifecycle defined in the format spec.

Material gathering and concrete surfacing logic belong to the adapter cold-start path (parallel to the existing memory scan + Decision-Structure index head emit). This section defines only the behavior contract.

Silent skip when the observation file is absent or no entries are due.

</self-evolution-observation-surface>

</cold-start-synthesis>
