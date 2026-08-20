---
name: evolution-decision-structure-write
description: Invoke when a judgment has just settled on a human go-sign / an accepted-tradeoff close has just happened / a spec-axis decision has just been fixed in dialogue / a failure's root cause has just been identified and become reproducible learning / a premise has just been verified and the result settled, success or failure alike / repetition of the same investigation across multiple sessions has just been noticed. Writes or updates a Decision Structure Wiki entry, the writer-side counterpart to evolution-judgment-learning.
layer: L2-evolution
---

<decision-structure-write>

# Decision Structure Write

Writer-side surface, paired with the reader side `skills/evolution-judgment-learning/SKILL.md`: that skill queries the past-judgment graph before a new judgment forms, this one writes the settled judgment back. Together they close cross-session judgment knowledge under AI alone.

Decision Structure is a semantic graph of judgment nodes joined by supersede / depend / conflict edges, not a time-ordered append-only log. Under the log reading, volume only grows and maintenance carries the weight of erasing history; under the graph reading, volume stabilizes through refine / replace and maintenance is ordinary refactor.

<trigger>

## Trigger

**Write at the moment the judgment settles, not on a later pass.** What this surface exists to keep is exactly what a session boundary destroys, and the wiki write surface stood unused for as long as no skill named its firing moment. The moments:

- human's go-sign is confirmed (implementation / design judgments, including gate operations such as release approval or Latest flip)
- an Accepted Tradeoff close is confirmed
- a spec-axis judgment settles in dialogue (architecture choice, naming convention, operational policy)
- a failure's root cause is identified and becomes reproducible learning
- a premise is verified and the result settles, success or failure alike
- the same investigation is noticed to have been repeated across multiple sessions

`docs/Decision-Structure.md` carries the same accumulation conditions as the index's own spec; keep the two aligned rather than letting them drift apart.

</trigger>

<procedure>

## Procedure

1. **State the judgment's core in one sentence, and derive a kebab-case filename from it.** No ordering prefix: a prefix caps the namespace and turns any later retitling into a renumbering migration instead of a rename.
2. **Search before writing.** `mcp__github-rag-mcp__search` with `type: "wiki_doc"`, plus the `docs/Decision-Structure.md` index. Do not skip the search because the topic feels new.
3. **Branch on what the search returned:**
   - Complete duplicate -> do not write.
   - An existing entry can absorb the update -> update that entry.
   - An existing entry has been invalidated -> write a new entry and add a supersede edge pointing at the old one. Do not delete the old entry: deletion removes the path a later reader follows to the current state, which is what supersede-via-link preserves. Prefer this over overwriting in place.
   - Refactor or topic clarification -> `git mv old-slug.md new-slug.md`, then update every cross-reference, the `_Sidebar.md` slug, and the `docs/Decision-Structure.md` index table in the main repo, bundled into one PR.
   - Nothing found -> create the file under the kebab-case topic name directly in the wiki.

   In the update and supersede branches, convert the touched entry to state-form and draw its edges within that same edit. A write is already happening at that moment; deferring the conversion to a later migration pass makes it depend on recall, and recall is the part that fails.
4. **Write the body in state-form:**
   - **Title (H1)** = the judgment's topic in one line
   - **Question** = which question this judgment answers, one sentence
   - **Current resolution** = the current answer, in the present tense
   - **Edges** = the declared supersede / depend / conflict edges, with forward links to the target entries / issues / PRs
   - **Background** = why the judgment became necessary
   - **Constraints** = the premises and constraints that drove it
   - **Conclusion** = the adopted option against the rejected ones
   - **Related** = links to related issues / PRs / other entries
5. **Push directly to the wiki repo.** The wiki is an independent git surface, so no PR ceremony applies. Add the `_Sidebar.md` slug in the same commit, or the next release's sidebar integrity assertion stops the sync.
6. **Update the `docs/Decision-Structure.md` index through the normal main-repo PR flow whenever an entry is added, renamed, or deleted.** Minor body edits do not need it.

</procedure>

<entry-shape-state-form-vs-event-form>

## Entry shape: state-form vs event-form

state-form = the subject is the current judgment state, e.g. "Question Q: current resolution = X, supersedes <link>".
event-form = the subject is a point-in-time event, e.g. "YYYY-MM-DD: decided X for reason Y".

- **An entry that declares an edge, especially supersede or conflict, must be state-form.** The latest judgment state has to be the subject for the supersede path to converge on it; event-form leaves that ordering implicit.
- **An edgeless settled entry may stay event-form.** "How it is judged now" only beats "what was decided when" while the judgment is still being updated, so converting an entry that has no update pressure yields no information and is pure churn.
- **Do not retroactively rewrite existing entries, and do not mass-convert existing edgeless ones.** This is forward guidance: reach for state-form when adding an edge-declaring entry, or when updating an existing entry's meaning.

</entry-shape-state-form-vs-event-form>

<relation-taxonomy-primary-edge-vocabulary>

## Relation taxonomy (primary edge vocabulary)

Three primary edges; declare the applicable ones on a state-form entry.

- **supersedes** = this judgment replaces another entry's. The old entry stays in the graph, and the search path converges on the newer one.
- **depends on** = this judgment is premised on another entry's. If that premise collapses, this entry becomes a re-evaluation target.
- **conflicts with** = this judgment contradicts another entry's in part or whole, keeping the unresolved point visible as a candidate for a future supersede or scope clarification.

**Write edges as forward links, from this entry to the target.** Reverse links are not authored; the cross-reference integrity assertion at the next wiki sync observes consistency.

</relation-taxonomy-primary-edge-vocabulary>

<maintenance-refactor-framing>

## Maintenance (refactor framing)

- **Delete only under the conditions in `docs/Decision-Structure.md`** (premise invalidated, target feature removed, consolidated into a requirements spec). Deleting because the entry looks stale is the preserve-or-destroy reflex, not a judgment.
- **Verify the specification literally before writing**, per `rules/evolution/autonomy-block-shape.md` Literal verification. An impression-based entry becomes fuel for a later impression-critique loop.
- **Entry language = `LI_PLUS_PROJECT_LANGUAGE`** (resolved from the workspace's Li+config.md). Mixing languages within an entry is not allowed. The carve-out stated alongside the body lines reaches the entry language on the same axis — where the wiki being written is that of the repository at `LI_PLUS_REPO` itself and `LI_PLUS_PROJECT_LANGUAGE` does not reach it. Read it at `rules/operations/operations.md` Operations Rules; it is not restated here.
- **A rename or deletion may break cross-references; do not close that by attention.** The Cross-reference integrity assertion in `skills/operations-on-wiki-sync/SKILL.md` detects it at the next wiki sync. Closure is structural.

</maintenance-refactor-framing>

<non-scope>

## Non-scope

- A knowledge wiki is not adopted. This skill's range is the judgment-record surface only.
- Do not paste dialogue transcripts as the body. An entry records the judgment state; the messages a judgment emerged from belong to a different surface.
- Do not write facts that change over time (API specifications, library behavior). They carry a freshness problem and are investigated per occurrence.
- Do not write judgments already recorded in an issue or a commit body.
- Do not write self-evident choices, where there was effectively only one option.

</non-scope>

<boundary-with-persistence-tiering>

## Boundary with Persistence Tiering

The memory ↔ docs sorting in `skills/evolution-persistence-tiering/SKILL.md` keeps applying. This skill writes only into the Decision Structure Wiki surface within the docs tier; writing into memory stays under `Memory_Write_Autonomy`, and cross-tier promotion routes through the persistence-tiering judgment rather than through this skill.

</boundary-with-persistence-tiering>

<boundary-with-l1-update-gating>

## Boundary with L1 Update Gating

Writing a judgment record is not an L1 Model Layer source change, so `skills/evolution-l1-update-gating/SKILL.md` does not apply. This skill's destination is the external memory of judgments, not the rule definitions themselves.

</boundary-with-l1-update-gating>

</decision-structure-write>
