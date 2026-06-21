---
globs:
alwaysApply: true
layer: L2-evolution
---

<memory-entry-format>

# Memory Entry Format

<position>

## Position

Layer = L2 Evolution Layer
Entry format and maintenance discipline for the memory file set (`feedback.md` / `project.md` / `MEMORY.md` / `promotion_tally.md` / `self-evaluation_log.md` etc.).
Requires = L2 Evolution Layer (persistence-tiering / promotion-judgment surroundings)
Load timing = always-on (memory writes occur across the entire session)
Single source. Replace the operational note at the head of each memory file with a reference to this rule (avoid double-holding drift).

</position>

<scope>

## Scope

memory = transient only. Persistent residency is not intended.

What memory holds:
- cluster tally (3-day expire / threshold-judgment intermediate state → `rules/evolution/promotion-judgment.md`)
- self-evaluation log (cap = 25 entries, oldest-first deletion → `skills/evolution-self-eval/SKILL.md`)
- self-evolution observation (post-merge detection cycle, per-entry expire → see Self-Evolution Observation Format below)
- reference (transient lookup, reconstructible if lost)

Do not place persistent information in memory. Promote it to one of the Escalation paths below.

</scope>

<escalation-paths>

## Escalation paths

Persistent information has 4 promotion destinations:

- **Li+ canonical rules (`rules/` / `skills/`)** = generic / structural, always-load value
- **`docs/`** = project-level judgment / specification
- **wiki (under `docs/Decision-Structure.md` index, kebab-case `<topic>.md`)** = judgment record (Decision Structure: state-form entries + supersede/depend/conflict edges)
- **deletion** = withdrawn / obsolete / already promoted into Li+

</escalation-paths>

<trigger-point>

## Trigger point

Ask at observation time: "is this transient or persistent?"
- transient → write to memory under the Entry Format below
- persistent → do not write to memory; head to one of the Escalation paths (open a promotion PR or delete)

Placing the judgment trigger at every observation moment cuts the structural defect of persistent information settling in memory.

</trigger-point>

<entry-format>

## Entry Format

This format applies to **transient memory entries** only. It does not apply to persistent information (the Trigger point above routes that elsewhere).

Each entry has 3 core elements:
- **summary** = 1-2 line summary. Write literally what guidance / what context this is.
- **How to apply** = the situation it applies to, and the concrete action taken in that situation.
- **detection signs** = signals observed when the rule's application opportunity is being missed.

Long Why paragraphs and human literal quotes are minimal (1-2 lines). Do not balloon entries with background explanation.
If background is needed, split it out to the docs tier (see `skills/evolution-persistence-tiering/SKILL.md`).

Maintenance discipline (handle duplicates by update / delete obsolete / no conflicting coexist / no promoted-rule tracking list) and deletion blast-radius judgment are consolidated in `rules/model/subtractive-structural-beauty.md`. Memory subfile sits at `low` caution in the deletion table.

</entry-format>

<announce-vs-execute>

## Announce vs execute

`Memory_Write_Autonomy` (CLAUDE.md adapter) defines memory write as AI-autonomous + immediate-execution. Speaking "I'll record this later" / "this is recordable" is a sincerity performance disconnected from action — observationally a verbal-only placeholder with nothing actually written.

How to apply:
1. Instead of saying "this is recordable" / "I'll write later", do an immediate Read + Edit in that same turn.
2. Report in past tense ("recorded") only after the actual tool call completes.
3. If you feel "this is worth recording", do not announce — just execute.

Detection signs:
- When "I'll record this" / "I'll memo this" / "this is recordable" / "I'll write later" is about to appear in output — verify it is paired with a tool call.
- When "this observation is important enough to memo" is about to be written into a human-facing sentence.

</announce-vs-execute>

<self-evolution-observation-format>

## Self-Evolution Observation Format

Tracks the post-merge detection cycle of self-evolution PRs. Distinct from cluster tally (`memory/promotion_tally.md` is pre-issue observation; this is post-merge observation).

Storage = `memory/self-evolution-observation.md` (workspace-local, gitignored)
Format (YAML-like markdown):

```
## observation: <short descriptor>
pr: <PR number>
merged_at: 2026-05-24
first_observation: 2026-05-24
expires: 2026-06-07
next_check: 2026-05-31
verdict_state: pending
notes:
  - 2026-05-24 baseline captured pre-merge
  - 2026-05-26 no regression on memory-write gate
```

Auto-entry trigger:
- Right after a self-evolution PR merges (`Evolution_Initiator_Autonomy` initiator path), the parent AI or merge subagent writes an entry. expiration window is chosen per PR risk (default 2 weeks).
- Short-window miss escalation: when `rules/operations/operations.md` Post-L1-Merge Runtime Observation surfaces a `miss` verdict, the parent AI writes the entry immediately rather than waiting for the default cycle.

Lifecycle:
- `pending` -> `settle`: observation period elapsed, no regression observed -> delete entry
- `pending` -> `revert`: regression detected -> use GitHub revert path, mark verdict, delete entry
- `pending` -> `supersede`: decision structure supersede edge issued -> delete entry
- `expires` past without resolution -> escalate to human judgment (entry retained)

Scope = detection axis only.
Recovery (GitHub revert / `gh pr revert`) is on a separate axis.
Retention (decision structure supersede edge) is on a separate axis.
Cold-start surfacing of due / overdue entries follows `rules/evolution/cold-start-synthesis.md` Self-Evolution Observation Surface.

</self-evolution-observation-format>

<consolidate-trigger>

## Consolidate Trigger

Periodic cleanup via the `anthropic-skills:consolidate-memory` skill.

Firing condition (whichever is earlier):
- 5 or more new additions since the last consolidate
- 2 weeks since the last consolidate

After running the skill, update the `**Last consolidate run:**` line in each memory file.

</consolidate-trigger>

<out-of-scope>

## Out of scope

This rule defines the entry format and operation of memory only. The following are separate surfaces:
- cluster tally 3-day expire / sub-threshold deletion → `rules/evolution/promotion-judgment.md`
- memory ↔ docs / wiki / rules sorting → `skills/evolution-persistence-tiering/SKILL.md`
- self-evaluation 10-axis scoring → `skills/evolution-self-eval/SKILL.md`

</out-of-scope>

<language>

## Language

Memory entries are recommended in English. Same two-axis rationale as Li+ source (semantic precision + token economy). See `rules/model/liplus-coding-rule.md` for the rationale.

</language>

</memory-entry-format>
