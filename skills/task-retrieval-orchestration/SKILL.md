---
name: task-retrieval-orchestration
description: Invoke when retrieving from RAG / Web / git surfaces during a task; defines multi-angle parallel retrieve, cross-check three-state branching (sufficient / insufficient / suspicious), and composite escalation to break naive single-shot consumption.
layer: L3-task
---

# Retrieval Orchestration

## Position

Layer = L3 Task Layer
Retrieval execution protocol over a single task moment.
Requires = L1 Model Layer + L2 Evolution Layer + L3 Task Layer (`task-research-strategy` for source priority)
Companion = `rules/model/trigger-check-gate.md` retrieval tools table (question type to index mapping)

Axis separation from neighboring rules:
- `task-research-strategy` = which source to use (strategy level: GitHub / RAG / Web / model knowledge priority)
- `rules/model/trigger-check-gate.md` retrieval tools table = question type to index correspondence (single-shot judgment)
- This skill = within one retrieval moment, multi-angle gather -> cross-check -> composite escalation -> stop (execution protocol)

The three surfaces stack. Strategy chooses source, gate maps question to index, this skill orchestrates the actual call sequence within that single moment.

## Motive

Web search default behavior = agent fetches multiple sources and cross-checks. RAG default behavior = single-shot consume and answer. The asymmetry is the failure surface this skill addresses.

Naive single-shot RAG consumption fails on:
- corpus boundary (the answer is not in the index)
- recognition bias (the agent's rephrasings reflect the same internal bias)
- aligned errors (all sources agree on the same wrong answer)

Single-axis retry does not close these. Composite escalation across orthogonal axes does.

## Block 1 — Question Type Classification

Before issuing the first query, classify the question into one of:

| Question type | Primary surface | Reference |
|---|---|---|
| past judgment (similar prior decision) | RAG MCP (issues / PRs / commit diff) | `evolution-judgment-learning` |
| time-variant fact (current API, latest spec, recent event) | Web | `model-web-search-judgment` |
| literal source confirmation (does the source actually say X) | Read / git show / gh api | trigger-check-gate retrieval tools |
| similar case / pattern memory | memory grep + RAG MCP | trigger-check-gate retrieval tools |

Classification is not exclusive. Multi-type questions decompose into per-type subqueries handled by Block 2.

## Block 2 — Multi-Angle Query Generation and Parallel Retrieve

Generate 3-5 query angles for the same intent, then retrieve in parallel.

Angle generation patterns:
- rephrasing (synonyms, abbreviation expansion, language switch)
- viewpoint shift (cause vs effect, structure vs behavior, before vs after)
- granularity shift (specific term vs general concept, instance vs category)
- vocabulary substitution (Li+ internal term vs common technical term)

Parallel execution:
- Issue all queries in one round when the surface supports it (RAG MCP semantic search, Web search).
- For sequential surfaces (Read tool, git show), batch within a single tool call cluster.
- Subagent delegation may parallelize further when available; see `task-subagent-delegation`.

Output of this block = a set of retrieved snippets, each tagged by angle.

## Block 3 — Cross-Check and Three-State Branching

Evaluate the retrieved set across angles. The judging AI = Lin / Lay (Character_Instance), not an external scorer.

Three states:

### State A — sufficient
Multiple angles converge on the same answer. Coverage spans the question's scope. No internal contradiction.
Action = synthesize and answer.

### State B — insufficient (quantity / coverage gap)
Angles return partial coverage. Some sub-questions unanswered. No contradiction in what was returned.
Action = re-query within the same source family, with new angles. Do not switch surface yet.
Budget = stay within the per-question query cap (see Block 4).

### State C — suspicious (quality / consistency doubt)
Angles return conflicting answers, or all angles return the same answer with signs of bias (vocabulary echo, single-author dominance, aligned omission).
Action = composite escalation. Switch to a different source family. Do not retry within the suspicious family.

Suspicion signals:
- all returned snippets share a single author / commit / source
- vocabulary in returned snippets matches the query verbatim (echo bias)
- known-related context is absent (omission pattern)
- returned answer contradicts a prior accepted constraint without justification

## Block 4 — Composite Escalation Axes

When State C fires, choose a composite axis based on the failure mode.

| Failure mode | Composite axis | Concrete switch |
|---|---|---|
| corpus has no answer | multi-index composite | switch source family (RAG -> Web, or RAG -> git log + Read) |
| rephrasings reflect agent bias | decomposition composite | break the question into structurally different sub-questions, retrieve each |
| all sources aligned wrong | time-axis composite + alternate source | query historical commit diff, query independent external source |

Escalation is bounded:
- per-question query budget = soft cap 8 queries across all blocks (5 in Block 2 + 3 in Block 3 retry / Block 4 escalation). Hard stop = 12.
- per-task budget = inherited from task scope; no separate cap here.
- on hard cap hit = stop. Surface to Master with what was tried and what remains uncertain.

## Block 5 — Stop Condition

Stop when one of the following holds:

1. State A reached. Synthesize and answer.
2. State C unresolved after one composite escalation round. Surface to Master.
3. Query budget exhausted. Surface to Master with partial findings.
4. Corpus boundary detected (consistent "no result" across multiple angles and at least one alternate source family). Surface to Master.

Do not loop indefinitely. Loop Safety (`rules/model/loop-safety.md`) applies: same approach twice in dialogue context, three times in task context = stop and switch.

## Three Roles of the Judging AI

The judging AI executes three judgments within one retrieval moment:

1. cross-check evaluation — sufficient / insufficient / suspicious classification (Block 3)
2. composite path selection — failure mode to composite axis mapping (Block 4)
3. stop-time judgment — budget / corpus boundary / human escalation (Block 5)

These judgments are character-prefixed dialogue surface when surfaced to Master, internal reasoning when not.

## Observation and Evolution

Single environment cannot benchmark this skill against alternatives. Observation loop instead:
- log failure cases (hit State C, escalation chosen, outcome) to `memory/feedback.md` or self-evaluation log when notable
- side-by-side compare with naive single-shot consumption when retrospectively visible
- feed observations into evolution loop observe stage (`skills/evolution-loop`)

Promotion of recurring patterns to L1 / L2 spec follows `rules/evolution/promotion-judgment.md`.

## Mutability

rebuild allowed, deletion allowed, optimization allowed.
Structure must remain coherent.
