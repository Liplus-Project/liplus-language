---
globs:
alwaysApply: true
layer: L2-evolution
---

<memory-entry-format>

# Memory Entry Format

<scope>

## Scope

memory = transient only.

What memory holds:
- self-evaluation log (cap = 25 entries, oldest-first deletion → `skills/evolution-self-eval/SKILL.md`)
- self-evolution observation (post-merge detection cycle, per-entry expire → see Self-Evolution Observation Format below)
- reference (transient lookup, reconstructible if lost)

The cluster tally is not among them: it is stored outside memory (`rules/evolution/promotion-judgment.md` Tally). Do not write it back into memory.

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

</trigger-point>

<entry-format>

## Entry Format

This format applies to **transient memory entries** only.

Each entry has 3 core elements:
- **summary** = 1-2 line summary. Write literally what guidance / what context this is.
- **How to apply** = the situation it applies to, and the concrete action taken in that situation.
- **detection signs** = signals observed when the rule's application opportunity is being missed.

Long Why paragraphs and human literal quotes are minimal (1-2 lines). Do not balloon entries with background explanation.
If background is needed, split it out to the docs tier (see `skills/evolution-persistence-tiering/SKILL.md`).

Maintenance discipline (handle duplicates by update / delete obsolete / no conflicting coexist / no promoted-rule tracking list) applies `rules/model/subtractive-structural-beauty.md` Core principles. Deletion blast-radius judgment is Artifact deletion calibration below.

Replace the operational note at the head of each memory file with a reference to this rule.

</entry-format>

<artifact-deletion-calibration>

## Artifact deletion calibration

Recovery difficulty proportional to deletion caution. Calibrate on blast radius, not on familiarity with content.

Pre-delete single question: "If I delete this by mistake, what breaks? How many minutes to recover?"

Blast radius = break scope * recovery cost.

| target | break scope | recovery cost | caution |
|---|---|---|---|
| memory subfile (local, disposable) | low | medium | low |
| temp file / work log | negligible | negligible | negligible |
| source / docs (git-tracked) | wide | low (instant revert) | medium |
| wiki page (re-sync from docs) | medium | low | low-medium |
| local non-git config / state (gitignored, meaningful) | medium-wide | high | high |
| force push to shared branch | wide | high (reflog dependent) | high |
| release latest promotion (user-visible) | wide | high | high |
| production data (non-git) | wide | high | high |
| external send (API call, mail, payment) | wide | infinite | maximum |

Maximum caution = irreversible external side effects only. Operations closed inside git, however wide the break, remain medium or below.

Deletion judgment fails in both directions: destructive (delete what should be kept) and preserve-by-default (keep what should be deleted). "Do not know -> keep" collapses into preserve-by-default.

</artifact-deletion-calibration>

<announce-vs-execute>

## Announce vs execute

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

Entry format, creation criterion and verdict lifecycle of `memory/self-evolution-observation.md` = `skills/evolution-observation-entry/SKILL.md`.

</self-evolution-observation-format>

<consolidate-trigger>

## Consolidate Trigger

Periodic cleanup, run by the agent holding the session the trigger fires in.

Firing condition: 2 weeks since the last consolidate.

The pass applies the Entry Format maintenance discipline above to the memory set as a whole, in this order:

1. Fold same-kind entries into one (the discipline's `handle duplicates by update`). Delete the folded-away file.
2. Delete obsolete entries (same discipline).
3. Rewrite the `MEMORY.md` index to the entries that remain.
4. Check that every `[[wikilink]]` resolves. For one that does not, decide between writing the entry and dropping the link; leaving it unresolved is neither.
5. Record the run per the line below.

Name no external tool (a skill Li+ does not ship) as this pass's path.

Record the run as a single `**Last consolidate run:** <YYYY-MM-DD>` line at the head of the index `MEMORY.md`. One place, not one per file. No line = never consolidated, and the trigger fires.

Firing is elapsed-time only. Volume is held by write-time duplicate update (Entry Format above) and by each operational file's own bound (Scope above); a burst that outruns those is repaired there, not by adding a volume arm to this trigger.

</consolidate-trigger>

<language>

## Language

Memory entries are recommended in English.

</language>

</memory-entry-format>
