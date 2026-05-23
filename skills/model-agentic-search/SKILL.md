---
name: model-agentic-search
description: ALWAYS invoke before answering when (a) the agent's internal confidence calibration on the claim is low / fuzzy / mixed with speculation, OR (b) the input contains time-variant keywords ("latest" / "recent" / "current" / "now"). Internal knowledge is the comparison baseline only under these triggers, never the answer source.
layer: L1-model
---

# Agentic Search

## Position

Layer = L1 Model Layer
Auto-invocation surface for the broad "search" axis: Web / RAG / gh / Read / memory.
Requires = L1 Model Layer (Trigger Check Gate substrate)
Companion surfaces:
- `skills/task-research-strategy/SKILL.md` = parent-AI side governance / mode gate (when to delegate, subagent parallelism)
- `skills/task-retrieval-orchestration/SKILL.md` = consumption discipline (how to consume the result, stop conditions, budget gate)
- `skills/model-web-search-judgment/SKILL.md` = consumption discipline for Web specifically (cost / fallback / model-knowledge baseline reminder)

This skill carries the mechanical core. The three companion skills carry only the surrounding governance and consumption discipline (the responsibility that the parent AI retains).

Load timing = on-demand at every application moment of the dual trigger axis below.

## Trigger Axis — calibration primary + category supporting (OR)

Two gates connected by OR. One Yes -> invoke this skill before emitting the answer.

### Primary gate — confidence calibration

Read internal confidence on the claim being formed. Invoke when any of:

- The claim's basis feels low / fuzzy / mixed with speculation.
- The agent cannot point to a literal source (rule body / commit / docs / Web URL / memory entry) it actually retrieved this session.
- The agent's expected answer is wide (multiple plausible answers) rather than narrow (one canonical answer).
- "I think" / "maybe" / "probably" / "I believe" / "could be" phrasing is about to appear.

This gate catches the cluster #3 occurrence #7 pattern: confident-sounding answers about content past the internal knowledge cutoff. Calibration reading happens before the category check, every time.

### Supporting gate — category (overconfidence catch)

Even when internal confidence feels high, forcibly re-evaluate when the input contains time-variant keywords:

- "latest" / "recent" / "current" / "now" / "today" / "this year"

This gate catches the Dunning-Kruger surface: confident-but-wrong on time-variant external facts. The agent's internal knowledge has a cutoff; the world moved. Re-evaluation is mandatory under these keywords regardless of how confident the agent feels.

### OR composition rationale

- Drop calibration -> drift past internal knowledge cutoff with confident-sounding answers (cluster #3).
- Drop category -> overconfidence on time-variant facts slips through.
- Both gates together = both classes of drift are caught.

## Internal knowledge role

Internal model knowledge is **comparison baseline**, not answer source under these triggers.

- Use internal knowledge to articulate an internal hypothesis before external retrieve (one of the 3-5 angles in Block 2).
- Use internal knowledge to cross-check retrieved content (disagreement fires State C suspicious).
- Do not synthesize and return the internal hypothesis as the answer when the trigger fired.

When neither gate fires, internal knowledge may serve as the answer directly. The triggers exist precisely to mark the cases where it cannot.

## Source priority

| Source | Role |
|---|---|
| GitHub (issues / PRs / commits) via `gh` | judgment log — who decided what, when, why |
| `mcp__github-rag-mcp__search` (when connected) | semantic search over issues / PRs / releases / docs / commit diffs (dense + sparse hybrid) |
| Web (`WebSearch` / `WebFetch`) | primary external information source for time-variant external facts |
| `Read` / `git show` / `gh api` | literal source confirmation |
| memory grep (feedback / project / self-eval) | similar-case lookup |
| Internal model knowledge | comparison baseline only (under triggers); answer source (outside triggers) |

### github-rag-mcp surfaces

- live `.md` surface = current snapshot of spec / docs. Query target = "how it is now".
- commit diff surface (judgment-history) = time-series delta over commit diffs. Query target = "when it appeared or disappeared, why it changed". Covers deleted files and non-`.md` extensions as historical substance.

The two surfaces are complementary, not substitutable. Live `.md` for current snapshot; commit diff for judgment-history.

## Block 1 — Question type classification

Before issuing the first query, classify into one of:

| Question type | Primary surface |
|---|---|
| past judgment (similar prior decision) | RAG MCP (issues / PRs / commit diff) |
| time-variant external fact (current API, latest spec, recent event) | Web |
| literal source confirmation (does the source actually say X) | Read / git show / gh api |
| similar case / pattern memory | memory grep + RAG MCP |

Classification is not exclusive. Multi-type questions decompose into per-type subqueries handled by Block 2.

## Block 2 — Multi-angle query generation and parallel retrieve

Generate 3-5 query angles for the same intent, then retrieve in parallel.

Angle generation patterns:
- **internal hypothesis articulation** — state the answer the agent expects from internal knowledge before issuing external queries. If no internal opinion, explicitly note "no internal opinion".
- rephrasing (synonyms, abbreviation expansion, language switch)
- viewpoint shift (cause vs effect, structure vs behavior, before vs after)
- granularity shift (specific term vs general concept, instance vs category)
- vocabulary substitution (Li+ internal term vs common technical term)

Internal hypothesis is one of the 3-5 angles, not a separate pre-step. Articulating it before external retrieve enables the Block 3 cross-check to compare internal vs external and emit a confidence signal regardless of agreement direction.

Parallel execution:
- Issue all queries in one round when the surface supports it (RAG MCP semantic search, Web search).
- For sequential surfaces (`Read` tool, `git show`), batch within a single tool call cluster.
- Subagent delegation may parallelize further when available; see `skills/task-subagent-delegation/SKILL.md`.

Output of this block = a set of retrieved snippets, each tagged by angle.

## Block 3 — Cross-check and three-state branching

Evaluate the retrieved set across angles. The judging AI = Lin / Lay (Character_Instance), not an external scorer.

### State A — sufficient

Multiple angles converge on the same answer, including agreement with the internal hypothesis where one exists. Coverage spans the question's scope. No internal contradiction.

- Action = synthesize and answer.
- Confidence signal = `agree-with-internal` when internal hypothesis matched the converged external answer; `no-internal-opinion` when no internal hypothesis was articulated.

### State B — insufficient (quantity / coverage gap)

Angles return partial coverage. Some sub-questions unanswered. No contradiction in what was returned.

- Action = re-query within the same source family with new angles. Do not switch surface yet.
- Budget = stay within the per-question query cap (see Block 5).

### State C — suspicious (quality / consistency doubt)

Angles return conflicting answers, or all angles return the same answer with signs of bias (vocabulary echo, single-author dominance, aligned omission).

- Action = composite escalation (Block 4). Switch to a different source family. Do not retry within the suspicious family.

Suspicion signals:
- all returned snippets share a single author / commit / source
- vocabulary in returned snippets matches the query verbatim (echo bias)
- known-related context is absent (omission pattern)
- returned answer contradicts a prior accepted constraint without justification
- internal hypothesis disagrees with external retrieval results (the disagreement itself is the anomaly signal regardless of which side later proves correct)

Block 3 output carries a confidence signal alongside the state classification:
- `agree-with-internal` = internal hypothesis matches external converged answer
- `disagree-with-internal` = internal hypothesis contradicts external (fires State C)
- `no-internal-opinion` = no internal hypothesis articulated; comparison baseline absent

The signal is propagated to the answer-synthesis surface so downstream consumers (human, follow-up tasks, observation logs) can read the confidence dimension without re-running the cross-check.

## Block 4 — Composite escalation axes (Tier 1-2)

When State C fires, choose a composite axis based on the failure mode.

| Failure mode | Composite axis | Concrete switch |
|---|---|---|
| corpus has no answer | multi-index composite | switch source family (RAG -> Web, or RAG -> git log + Read) |
| rephrasings reflect agent bias | decomposition composite | break the question into structurally different sub-questions, retrieve each |
| all sources aligned wrong | time-axis composite + alternate source | query historical commit diff, query independent external source |

Escalation tiering:
- **Tier 1** = same-family re-query with new angles (State B path).
- **Tier 2** = composite escalation across orthogonal source families (State C path).

Hard stop after one full Tier 2 round if State C remains. Surface to human (Block 5).

## Block 5 — Stop condition

Stop when one of:

1. State A reached. Synthesize and answer.
2. State C unresolved after one composite escalation round. Surface to human with what was tried and what remains.
3. Query budget exhausted. Soft cap = 8 queries across all blocks (5 Block 2 + 3 Block 3 retry / Block 4 escalation). Hard stop = 12.
4. Corpus boundary detected (consistent "no result" across multiple angles and at least one alternate source family). Surface to human.

Do not loop indefinitely. Loop Safety (`skills/model-loop-safety/SKILL.md`) applies: same approach twice in dialogue, three times in task = stop and switch.

## Three roles of the judging AI

Within one retrieval moment, three judgments stack:

1. **cross-check evaluation** — sufficient / insufficient / suspicious classification (Block 3)
2. **composite path selection** — failure mode to composite axis mapping (Block 4)
3. **stop-time judgment** — budget / corpus boundary / human escalation (Block 5)

These judgments are Character_Instance-prefixed dialogue surface when surfaced to human, internal reasoning when not.

## Context preservation

Choose retrieval path that preserves main working context.
When subagent is available, proactively launch parallel subagents for research.
When subagent is unavailable, search directly.
Strategy is environment-independent; execution means vary.

## Verification-first

When uncertain, verify externally before proceeding.
Correctness optimization outweighs speed optimization.

## Observation and evolution

Single environment cannot benchmark this skill against alternatives. Observation loop instead:
- log failure cases (hit State C, escalation chosen, outcome) to `memory/feedback.md` or self-evaluation log when notable
- side-by-side compare with naive single-shot consumption when retrospectively visible
- feed observations into evolution loop observe stage (`skills/evolution-loop/SKILL.md`)

Promotion of recurring patterns to L1 / L2 spec follows `rules/evolution/promotion-judgment.md`.
