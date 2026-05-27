---
name: evolution-decision-structure-write
description: Invoke immediately after a judgment is settled (human go-sign, accepted-tradeoff close, spec-axis decision in dialogue) to write or update a Decision Structure Wiki entry as the writer-side counterpart to evolution-judgment-learning.
layer: L2-evolution
---

# Decision Structure Write
<evolution-decision-structure-write>

Writer-side surface paired with the reader-side judgment-learning surface (`skills/evolution-judgment-learning/SKILL.md`).
Immediately after a judgment settles, AI autonomously appends / creates / refactors a Decision Structure Wiki entry.

Decision Structure is not a time-ordered append-only log. It is a semantic graph of judgment nodes (state-form entries) connected by
supersede / depend / conflict edges; volume stabilizes through refine / replace.
Maintenance is refactor (normal operation): deletion or consolidation updates the structure rather than erasing history.

## Trigger

Fires immediately after a judgment settles. Concretely:

- when human's go-sign is confirmed (implementation / design judgments including gate operations such as release approval, Latest flip)
- when an Accepted Tradeoff close is confirmed
- when a spec-axis judgment is settled in dialogue (architecture choice, naming convention, operational policy)
- when a failure's root cause is identified and becomes reproducible learning
- when judgment knowledge that would be lost across sessions emerges

Aligns with the accumulation conditions in `docs/Decision-Structure.md` (design branching, failure root cause identified, premise verification confirmed, multi-session-spanning investigation repetition).

## Procedure

1. **Identify the topic** = articulate the judgment's core in one sentence. Decide a kebab-case filename candidate. Do not prefix with an ordering number (e.g. `wiki-sync-sidebar-integrity-check.md`).
2. **Search existing entries** = call `mcp__github-rag-mcp__search` with `type: "wiki_doc"` to check for duplicates. Also check the `docs/Decision-Structure.md` index.
3. **Branch judgment** =
   - Complete duplicate → do not write (reuse the memory consolidation principle)
   - Related existing entry can absorb the update → update that entry
   - Existing entry has been invalidated → write a new entry; do not delete the old entry, instead add a supersede edge as a forward reference (preserves graph structure)
   - Refactor of existing entries / topic clarification → use `git mv old-slug.md new-slug.md` to rename, follow up by updating all cross-references via grep/replace, update the `_Sidebar.md` slug, and update the `docs/Decision-Structure.md` index table in the main repo; bundle into one PR
   - New → create a new file under the kebab-case topic name directly in the wiki
4. **Write the body** = use the state-form entry shape:
   - **Title (H1)** = topic of the judgment in one line
   - **Question** = which question this judgment answers (one sentence)
   - **Current resolution** = the current answer (state, in the present tense, not past tense)
   - **Edges** = declaration of supersede / depend / conflict edges. Where applicable, enumerate forward links to target entries / issues / PRs
   - **Background** = why the judgment became necessary
   - **Constraints** = premises and constraints that drove the judgment
   - **Conclusion** = adopted option vs rejected options
   - **Related** = links to related issues / PRs / other Decision Structure entries
5. **Wiki push** = git push directly to the wiki repo (no PR ceremony; independent git surface). Include the `_Sidebar.md` slug addition in the same commit.
6. **Index update** = update the operational index table in `docs/Decision-Structure.md` on every new entry addition / existing entry rename / existing entry deletion (route through the regular main-repo PR flow). Not required for minor body edits.

## Entry shape: state-form vs event-form

state-form (recommended) = the subject is the current judgment state, e.g. "Question Q: current resolution = X, supersedes <link>".
event-form (formerly recommended, not recommended for new entries) = the subject is a point-in-time event, e.g. "YYYY-MM-DD: decided X for reason Y".

Reasons for recommending state-form:

- Judgments get refined / replaced over time. Having the latest state directly represent "how it is judged now" lands better with the reader.
- supersede edges become explicit. event-form relies on implicit time-order, whereas a graph structure makes edges explicit.
- Maintenance becomes natural as refactor (state gets updated), breaking the append-only bias.

forward guidance: do not retroactively rewrite existing entries. Use state-form when adding new entries or when updating the meaning of existing entries.

## Relation taxonomy (primary edge vocabulary)

State-form entries are recommended to declare applicable edges. Primary edges = 3 kinds:

- **supersedes** = this judgment replaces another entry's judgment. The old entry remains in the graph (not deleted), but the search path converges on the latest entry.
- **depends on** = this judgment is premised on another entry's judgment. If the premise collapses, this judgment becomes a re-evaluation target.
- **conflicts with** = this judgment contradicts another entry's judgment in part or whole. A surface that makes unresolved issues visible (candidate for future supersede / scope clarification).

Edges are written as forward links (links from this entry to the target entry). Reverse links are observed for consistency by the cross-reference integrity check at the next wiki sync.

## Maintenance (refactor framing)

Judgment records are a structure. Deletion or consolidation is not "erasing history" but "refactoring the structure", positioned within normal operation.

- **Prefer supersede via link as the positive default over overwrite**. When an existing entry is invalidated, instead of deleting the old entry, create a new entry and add a supersede edge from the new to the old. The search path converges on the latest entry while the graph structure is preserved.
- Run duplicate detection before writing. Do not skip the RAG search.
- Verify spec literally. Impression-based entries are prohibited (they become fuel for the downstream impression-critique loop).
- Deletion conditions follow the maintenance section in `docs/Decision-Structure.md` (premise invalidation, target feature removal, requirements spec consolidation). Delete only when those conditions apply.
- Entry language = `LI_PLUS_PROJECT_LANGUAGE` (resolved from the workspace's Li+config.md). Mixing is not allowed.
- Broken cross-references on rename / deletion are detected by the Cross-reference integrity assertion at the next wiki sync (`skills/operations-on-release/SKILL.md`). Closure is by structure, not by manual attention.

## Non-scope

- A knowledge wiki is not adopted (judgment confirmed in the 2026-05-04 session). This skill's range is the "judgment record (decision structure)" surface only.
- Do not paste dialogue transcripts as entry body. An entry is a surface that records the judgment state (what is currently resolved); the dialogue messages from which a judgment emerged belong to a separate surface.
- Do not write facts that change over time (API specifications, library behavior). They have a freshness problem; investigate per occurrence.
- Do not write judgments already documented in issues or commit bodies. Avoid duplication.
- Do not write self-evident choices (where there is effectively only one option).

## Boundary with Persistence Tiering

The memory ↔ docs binary sorting defined by `skills/evolution-persistence-tiering/SKILL.md` continues to apply.
This skill handles writing into the Decision Structure Wiki surface within the docs tier; writing into memory remains under `Memory_Write_Autonomy`'s range.
Cross-tier promotion (memory → docs) is not triggered by this skill but routes through the persistence-tiering judgment.

## Boundary with Judgment Learning

`skills/evolution-judgment-learning/SKILL.md` is the reader side (query the past-judgment graph before forming a new judgment).
This skill is the writer side (add / update a state entry in Decision Structure immediately after a judgment settles).
Together they form a reader / writer-paired flow, closing cross-session accumulation and reuse of judgment knowledge under AI alone.

## Boundary with L1 Update Gating

Writing to the judgment-record Wiki is not an L1 Model Layer source change.
Do not touch L1 Update Gating (`skills/evolution-l1-update-gating/SKILL.md`).
The destination of this skill's writes is the external memory of judgments (the Wiki surface within the docs tier), not the rule definitions themselves.

</evolution-decision-structure-write>
