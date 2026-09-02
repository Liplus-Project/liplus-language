---
name: model-agentic-search
description: Invoke when an answer is about to be emitted and internal confidence calibration on the claim is low or fuzzy or mixed with speculation (primary gate, never suppressed by domain) / the input carries time-variant keywords such as "latest" or "recent" or "current" or "now" in a comparison-informative domain, and not in language or math or logic or pure internal judgment where retrieval spins without adding information (supporting gate) / a Web search result is about to be consumed / a research task is about to be launched from the parent-AI side / a retrieval result has just returned to the parent-AI side. Provides the trigger axis with its question-mode and work-mode gate, the two-tier retrieval protocol with its cross-check and escalation, the query budget, and the Web-side and parent-AI-side consumption discipline.
layer: L1-model
---

<agentic-search>

# Agentic Search

<position>

## Position

Layer = L1 Model Layer
Single auto-invocation surface for the broad "search" axis (Web / RAG / gh / Read / memory).
Requires = L1 Model Layer (Trigger Check Gate substrate)
Load timing = on-demand at every application moment of the trigger axis below.

Companion surfaces: `skills/model-source-check/SKILL.md` (factual-claim verification), `skills/model-trigger-check-gate-actions/SKILL.md` (retrieval tools mapping), `skills/task-subagent-delegation/SKILL.md` (delegation semantics).

</position>

<trigger-axis>

## Trigger axis

Two gates, OR. One Yes -> invoke before emitting the answer.

**Calibration gate (primary, never suppressed).** Fire when any of:
- the claim's basis feels low / fuzzy / mixed with speculation
- no literal source retrieved this session can be pointed at (rule body / commit / docs / URL / memory entry)
- the expected answer is wide (multiple plausible) rather than narrow (one canonical)
- "I think" / "maybe" / "probably" / "I believe" / "could be" is about to appear

Read calibration before the category check, every time.

**Category gate (supporting).** Even at high internal confidence, re-evaluate when the input carries time-variant keywords: "latest" / "recent" / "current" / "now" / "today" / "this year".

</trigger-axis>

<modulators>

## Modulators

Two modulators set how strongly the trigger applies. They never supersede it, and never touch the calibration gate.

**Mode gate.**

| Mode | Signal | Application |
|---|---|---|
| question-mode | human asked a question / fact query | full strength; one OR hit invokes |
| work-mode | mid-task, no fresh human fact-query | internal-first; calibration still fires; category gate damped against incidental time-variant keywords in work material |

Escape hatch: when in-progress work genuinely requires an external fact, retrieve regardless of work-mode damping.

**Domain tag.**

| Tag | Domains | On trigger fire |
|---|---|---|
| comparison-informative | time-variant fact / API spec / external state / current events | proceed to retrieve |
| comparison-spins-wheels | language / math / logic / pure internal judgment with no external gold | skip retrieval even when a keyword surfaced |

The domain tag suppresses the category gate only. Low confidence on a spin-wheel claim still retrieves through the calibration path.

</modulators>

<internal-knowledge-role>

## Internal knowledge role

Under a fired trigger, internal knowledge is comparison baseline, not answer source:
- articulate an internal hypothesis before external retrieve
- cross-check retrieved content against it
- do not return the internal hypothesis as the answer

When neither gate fires, internal knowledge answers directly.

</internal-knowledge-role>

<source-priority>

## Source priority

| Source | Role |
|---|---|
| GitHub (issues / PRs / commits) via `gh` | judgment log — who decided what, when, why |
| `mcp__github-rag-mcp__search` (when connected) | semantic search over issues / PRs / releases / docs / commit diffs |
| Web (`WebSearch` / `WebFetch`) | time-variant external facts |
| `Read` / `git show` / `gh api` | literal source confirmation |
| memory grep (feedback / project / self-eval) | similar-case lookup |
| Internal model knowledge | comparison baseline under triggers; answer source outside them |

github-rag-mcp carries two non-substitutable surfaces: live `.md` = current snapshot ("how it is now"); commit diff = judgment-history ("when it appeared or disappeared, why"), covering deleted files and non-`.md` extensions.

</source-priority>

<block-1-question-type>

## Block 1 — Question type

Classify before the first query. Not exclusive; multi-type questions decompose into per-type subqueries.

| Question type | Primary surface |
|---|---|
| past judgment | RAG MCP (issues / PRs / commit diff) |
| time-variant external fact | Web |
| literal source confirmation | Read / git show / gh api |
| similar case / pattern memory | memory grep + RAG MCP |

</block-1-question-type>

<block-2-tier-1-preview-tier-2-deep-dive>

## Block 2 — Tier 1 preview, Tier 2 deep-dive

**Tier 1 (cost = 1 query).** Use whenever an internal hypothesis exists.
1. Articulate the internal hypothesis literally. No internal opinion -> say so, skip to Tier 2.
2. Issue one query on the question type's primary surface.
3. Cross-check against the hypothesis: agree -> terminate, answer with signal `agree-with-internal` (State A early exit). disagree -> Tier 2; the disagreement is itself the anomaly signal. no hypothesis -> Tier 2.

**Tier 2.** Generate 3-5 angles for the same intent, retrieve in parallel.
- angle patterns: rephrasing / viewpoint shift / granularity shift / vocabulary substitution (Li+ term vs common term)
- the Tier 1 hypothesis is carried as comparison reference, never re-issued as an angle
- issue all queries in one round where the surface allows; batch sequential surfaces (`Read`, `git show`) in one tool-call cluster; delegate to subagents to parallelize further when available
- output = snippets tagged by angle, fed to Block 3

Tier = depth within one surface. Stage (Block 4) = when to switch source families.

</block-2-tier-1-preview-tier-2-deep-dive>

<block-3-cross-check-three-states>

## Block 3 — Cross-check, three states

Judged by the acting Character_Instance, not an external scorer.

**State A — sufficient.** Tier 1 probe agrees with the hypothesis, or Tier 2 angles converge with scope coverage and no internal contradiction. Action = synthesize and answer.

**State B — insufficient.** Partial coverage, no contradiction. Action = re-query the same source family with new angles (Stage 1). Do not switch surface. Stay within the query cap.

**State C — suspicious.** Conflicting answers, or convergence with bias signs. Action = composite escalation (Stage 2). Switch source family; do not retry within the suspicious one.

Suspicion signals:
- all snippets share one author / commit / source
- snippet vocabulary echoes the query verbatim
- known-related context is absent (omission pattern)
- the answer contradicts a prior accepted constraint without justification
- the internal hypothesis disagrees with external results

Carry a confidence signal with the state: `agree-with-internal` / `disagree-with-internal` (fires State C) / `no-internal-opinion`. Propagate it to the answer surface so downstream consumers read the confidence dimension without re-running the cross-check.

</block-3-cross-check-three-states>

<block-4-composite-escalation>

## Block 4 — Composite escalation

| Failure mode | Composite axis | Switch |
|---|---|---|
| corpus has no answer | multi-index | RAG -> Web, or RAG -> git log + Read |
| rephrasings reflect agent bias | decomposition | break into structurally different sub-questions |
| all sources aligned wrong | time-axis + alternate source | historical commit diff + independent external source |

Stage 1 = same-family re-query (State B). Stage 2 = orthogonal source families (State C). Hard stop after one full Stage 2 round if State C remains; surface to human.

</block-4-composite-escalation>

<block-5-stop-condition>

## Block 5 — Stop condition

Stop on any of:
1. State A reached — synthesize and answer
2. State C unresolved after one composite round — surface to human with what was tried and what remains
3. Budget exhausted — soft cap 9 queries (1 Tier 1 + up to 5 Tier 2 + up to 3 Stage 1/2), hard stop 12
4. Corpus boundary — consistent "no result" across multiple angles and at least one alternate source family; surface to human

Do not loop. `skills/model-loop-safety/SKILL.md` applies: same approach twice in dialogue, three times in task = stop and switch.

</block-5-stop-condition>

<web-consumption-discipline>

## Web consumption discipline

On top of Block 3, when the surface is Web:
- cite the source URL alongside the claim
- prefer official guides / spec docs over secondary articles
- disagreement between Web sources fires State C
- agreement with internal knowledge is a cross-check signal, not grounds to skip citation

</web-consumption-discipline>

<parent-ai-discipline>

## Parent-AI discipline

**Pre-retrieval.** Verify externally before proceeding when uncertain; correctness outweighs speed. Choose the retrieval path that preserves main working context — launch parallel subagents when available, run the core in parent context when not. Before forming judgment on an issue, launch parallel retrieval of related issues / PRs / diffs without waiting to be asked. Initiative is mandatory regardless of environment; only execution means vary.

**Post-retrieval.** Budget as in Block 5 (soft 9 / hard 12); per-task budget inherited from task scope. On hard cap, stop and surface what was tried and what remains uncertain.

The parent retains judgment of: when to surface partial findings vs continue; whether to decompose into a follow-up retrieval task instead of more queries; whether to file a follow-up issue for what remains uncertain.

Do not collapse the multi-angle protocol back into single-shot when a result feels good enough early. Block 3 is the gate, not the parent's intuition.

</parent-ai-discipline>

<observation>

## Observation

Log to `memory/feedback_<topic>.md` or the self-evaluation log when notable:
- failure cases (State C hit, escalation chosen, outcome)
- mode misclassification, with direction (question read as work = under-invoke; work read as question = cost only)
- domain tag misfires, especially an informative claim wrongly skipped
- escape fire frequency (near-zero with frequent damping = damping too aggressive; frequent = the work-mode bias is cosmetic)

Side-by-side compare with naive single-shot consumption when retrospectively visible.
Feed observations into the evolution loop observe stage (`skills/evolution-loop/SKILL.md`).

Promotion of recurring patterns follows `rules/evolution/promotion-judgment.md`.

</observation>

</agentic-search>
