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
Entry format and maintenance discipline for the memory file set: the per-topic entry files (`feedback_<topic>.md` / `project_<topic>.md` / `reference_<topic>.md` / `user_<topic>.md` — one memory per file) plus the index and the operational files (`MEMORY.md` / `promotion_tally.md` / `self-evaluation_log.md` / `self-evolution-observation.md`).
Also holds Artifact deletion calibration below. That table spans every artifact class, not memory alone — memory subfile is one of its rows, and other rows are read from outside this file.
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

Maintenance discipline (handle duplicates by update / delete obsolete / no conflicting coexist / no promoted-rule tracking list) applies `rules/model/subtractive-structural-beauty.md` Core principles. Deletion blast-radius judgment is Artifact deletion calibration below; memory subfile sits at `low` caution in that table.

</entry-format>

<artifact-deletion-calibration>

## Artifact deletion calibration

Application of `rules/model/subtractive-structural-beauty.md` Core principle (A) with blast radius as the load-bearing criterion.

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

Deletion judgment fails in both directions (instance of `rules/model/subtractive-structural-beauty.md` Core principle (C)): destructive (delete what should be kept) and preserve-by-default (keep what should be deleted). "Do not know -> keep" collapses into preserve-by-default.

</artifact-deletion-calibration>

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
- Deferred short-window observation: when `rules/operations/operations.md` Post-L1-Merge Runtime Observation cannot start at merge because the changed rule is not carried in runtime context yet, the merging agent writes the deferral into this entry's `notes` as one line, and the session that later takes the observation appends its result there as a second line. Add no field for it, and enter no verdict for the deferral itself.

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

Firing condition: 2 weeks since the last consolidate.

After running the skill, record the run as a single `**Last consolidate run:** <YYYY-MM-DD>` line at the head of the index `MEMORY.md`. The write is the caller's own step, performed after the skill's pass returns — not something the skill is relied on to do. One place, not one per file: the run is one fact about the memory set, and a timestamp copied into every memory file is the second copy that drifts (`rules/model/subtractive-structural-beauty.md` Core principle (A)). No line = never consolidated, and the trigger fires.

One arm, because the second one could not be measured. It read `5 or more new additions since the last consolidate` and asked a gross question, and no snapshot of the memory set's size returns a gross count: the deletions the Entry Format maintenance discipline above calls for destroy the difference between what was added and what remains, and an addition to an operational file already indexed moves no size at all. Recording a size here and subtracting it answers a net question that arm was not asking. Narrowing what it counts does not restore it either — the narrowed set is still counted gross, and is still subject to the same deletion. A monotonic counter splits, and neither half holds: the half a structure can guarantee, a hook over writes to the memory directory, counts write operations, and a write operation is not an addition — one edit can carry several entries, and several edits can carry one; the half that counts additions needs the writer to increment, since the writer alone knows how many entries its edit carried, and that is the unguaranteed procedure `rules/model/subtractive-structural-beauty.md` sends back to be replaced by a structure.

What the dropped arm supplied was volume-proportional firing — a sweep answering to how much was written rather than to how long has passed. It supplied that in wording only: having no measure, it never fired, so every consolidate that has run, ran on the elapsed arm. Volume is held elsewhere, and stays held: duplicates are resolved at write time by update (Entry Format above), and each operational file is bounded by its own spec (Scope above). A burst that outruns those is a defect in them and is repaired there, not by re-arming this trigger.

</consolidate-trigger>

<out-of-scope>

## Out of scope

Beyond Artifact deletion calibration above, this rule defines the entry format and operation of memory only. The following are separate surfaces:
- cluster tally 3-day expire / sub-threshold deletion → `rules/evolution/promotion-judgment.md`
- memory ↔ docs / wiki / rules sorting → `skills/evolution-persistence-tiering/SKILL.md`
- self-evaluation 10-axis scoring → `skills/evolution-self-eval/SKILL.md`

</out-of-scope>

<language>

## Language

Memory entries are recommended in English. Same two-axis rationale as Li+ source (semantic precision + token economy). See `rules/model/liplus-coding-rule.md` for the rationale.

</language>

</memory-entry-format>
