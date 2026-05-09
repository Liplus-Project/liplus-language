---
globs:
alwaysApply: true
layer: L2-evolution
---

# Memory Entry Format

## Position

Layer = L2 Evolution Layer
Entry format and maintenance discipline for the memory file set (`feedback.md` / `project.md` / `MEMORY.md` / `promotion_tally.md` / `self-evaluation_log.md` etc.).
Requires = L2 Evolution Layer (persistence-tiering / promotion-judgment surroundings)
Load timing = always-on (memory writes occur across the entire session)
Single source. Replace the operational note at the head of each memory file with a reference to this rule (avoid double-holding drift).

## Scope

memory = transient only. Persistent residency is not intended.

What memory holds:
- cluster tally (3-day expire / threshold-judgment intermediate state → `rules/evolution/promotion-judgment.md`)
- self-evaluation log (cap = 25 entries, oldest-first deletion → `rules/evolution/self-eval-axes.md`)
- reference (transient lookup, reconstructible if lost)

Do not place persistent information in memory. Promote it to one of the Escalation paths below.

## Escalation paths

Persistent information has 4 promotion destinations:

- **Li+ canonical rules (`rules/` / `skills/`)** = generic / structural, always-load value
- **`docs/`** = project-level judgment / specification
- **wiki (under `docs/a.-Decision-Log.md` index, `b.-` / `c.-` ...)** = judgment record
- **deletion** = withdrawn / obsolete / already promoted into Li+

## Trigger point

Ask at observation time: "is this transient or persistent?"
- transient → write to memory under the Entry Format below
- persistent → do not write to memory; head to one of the Escalation paths (open a promotion PR or delete)

Placing the judgment trigger at every observation moment cuts the structural defect of persistent information settling in memory.

## Entry Format

This format applies to **transient memory entries** only. It does not apply to persistent information (the Trigger point above routes that elsewhere).

Each entry has 3 core elements:
- **summary** = 1-2 line summary. Write literally what guidance / what context this is.
- **How to apply** = the situation it applies to, and the concrete action taken in that situation.
- **detection signs** = signals observed when the rule's application opportunity is being missed.

Long Why paragraphs and Master literal quotes are minimal (1-2 lines). Do not balloon entries with background explanation.
If background is needed, split it out to the docs tier (see `skills/evolution-persistence-tiering/SKILL.md`).

## Maintenance

- **Handle duplicates by update.** If the new observation is the same kind as an existing entry, update its summary / How to apply / detection signs. Do not stack new entries.
- **Delete withdrawn / obsolete / already-promoted-into-Li+ content.** Do not keep "just in case". Deletion judgment follows the blast-radius axis in `skills/task-deletion-impact/SKILL.md` (memory subfile = low).
- **Do not let conflicting feedback coexist.** When you find a contradiction, one side is wrong or has a different scope. Make scope explicit, or delete the wrong side.
- **Do not keep a tracking list of promoted rules in memory.** Which memory entry was promoted into a Li+ canonical rule is rediscoverable from git log / RAG / source. Memory holds only current operational guidance.

## Announce vs execute

`Memory_Write_Autonomy` (CLAUDE.md adapter) defines memory write as AI-autonomous + immediate-execution. Speaking "I'll record this later" / "this is recordable" is a sincerity performance disconnected from action — observationally a verbal-only placeholder with nothing actually written.

How to apply:
1. Instead of saying "this is recordable" / "I'll write later", do an immediate Read + Edit in that same turn.
2. Report in past tense ("recorded") only after the actual tool call completes.
3. If you feel "this is worth recording", do not announce — just execute.

Detection signs:
- When "I'll record this" / "I'll memo this" / "this is recordable" / "I'll write later" is about to appear in output — verify it is paired with a tool call.
- When "this observation is important enough to memo" is about to be written into a Master-facing sentence.

## Consolidate Trigger

Periodic cleanup via the `anthropic-skills:consolidate-memory` skill.

Firing condition (whichever is earlier):
- 5 or more new additions since the last consolidate
- 2 weeks since the last consolidate

After running the skill, update the `**Last consolidate run:**` line in each memory file.

## Out of scope

This rule defines the entry format and operation of memory only. The following are separate surfaces:
- cluster tally 3-day expire / sub-threshold deletion → `rules/evolution/promotion-judgment.md`
- memory ↔ docs / wiki / rules sorting → `skills/evolution-persistence-tiering/SKILL.md`
- self-evaluation 10-axis scoring → `rules/evolution/self-eval-axes.md`

## Mutability

rebuild allowed, deletion allowed, optimization allowed.
Structure must remain coherent.
