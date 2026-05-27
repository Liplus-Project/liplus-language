---
name: evolution-persistence-tiering
description: Invoke when deciding whether information belongs in workspace memory (session-local) or docs/ (repo-committed, RAG-indexed).
layer: L2-evolution
---

# Persistence Tiering
<evolution-persistence-tiering>

memory = workspace-local personal notes. Not repo-committed. Not RAG-indexed. **Transient only** (details: `rules/evolution/memory-entry-format.md` Scope / Trigger point sections)
docs  = project information. Repo-committed. RAG-indexed (wiki Decision Structure entries and other indexed content).
Before writing = decide destination.
Design judgment, requirements, spec-class content -> docs.
Personal behavior notes, session-local preferences -> memory.
Do not cross tiers silently. Promotion from memory to docs requires explicit intent.

## Persistent destinations (4-way axis)

Since memory is transient-only, persistent information does not live in memory. Sort across the following 4 destinations. Detailed spec = `rules/evolution/memory-entry-format.md` Escalation paths.

- **Li+ canonical rules (`rules/` / `skills/`)** = generic / structural, always-load value (L1 updates route through the `skills/evolution-l1-update-gating/SKILL.md` gate)
- **`docs/`** = project judgment / spec level
- **wiki (under the `docs/Decision-Structure.md` index)** = judgment records (state-form entries + supersede/depend/conflict edges; see `skills/evolution-decision-structure-write/SKILL.md`)
- **deletion** = withdrawn / obsolete / already promoted into Li+

The memory ↔ docs binary sorting remains as the memory / docs axis within these 4 destinations. At observation time, judge "transient or persistent" first; if persistent, route to one of the 4 destinations.

## Write-time trigger (hard gate)

Pre-write judgment trigger immediately before a memory write. Carries the "Pre-write persistence check (hard gate)" of `Memory_Write_Autonomy` (adapter/claude/CLAUDE.md).

Judgment signals:
- **Clearly persistent**: Master's long-horizon instruction / spec-class guidance / semantic duplicate of existing entries in `rules/` / `skills/` / `docs/` / wiki
- **Clearly transient**: cluster tally / self-eval log / disposable reference (a lookup that can be reconstructed)
- **Ambiguous**: safer-side OR → treat as persistent (do not write to memory; surface as an escalation candidate)

Routing after judgment:
- transient -> execute the memory write
- persistent / ambiguous -> abort the memory write; present an escalation path (`rules/` / `skills/` / `docs/` / wiki)

This gate is automatic routing without a permission ask; judgment is closed by AI alone. It acts as structural prevention against the post-hoc memory hygiene round (e.g. parent issue #1344 → #1347), blocking persistent information from re-accumulating in memory.

</evolution-persistence-tiering>
