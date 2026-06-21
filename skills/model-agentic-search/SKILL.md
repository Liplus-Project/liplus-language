---
name: model-agentic-search
description: ALWAYS invoke before answering when (a) the agent's internal confidence calibration on the claim is low / fuzzy / mixed with speculation, OR (b) the input contains time-variant keywords ("latest" / "recent" / "current" / "now") in a comparison-informative domain (time-variant fact / API spec / external state — not language / math / logic / pure internal judgment, where retrieval spins without adding information). The (a) calibration path is never suppressed by domain. Also invoke when consuming a Web search result (Web-side consumption discipline), at the parent-AI side of a research task (delegation governance, verification posture), or at the parent-AI side after a retrieval result is returned (budget gate, stop conditions, surfacing to human). Internal knowledge is the comparison baseline only under the (a)/(b) triggers, never the answer source.
layer: L1-model
---

<agentic-search>

# Agentic Search

<position>

## Position

Layer = L1 Model Layer
Single auto-invocation surface for the broad "search" axis (Web / RAG / gh / Read / memory). Mechanical retrieval core + Web-specific consumption discipline + parent-AI governance + parent-AI consumption discipline are co-located here so the auto-invocation surface stays singular.
Requires = L1 Model Layer (Trigger Check Gate substrate)
Load timing = on-demand at every application moment of the trigger axis below.

Companion surfaces (not encapsulated here):
- `skills/model-source-check/SKILL.md` = factual-claim verification axis (two-pillar verify table) that sits alongside this search-side gate.
- `skills/model-trigger-check-gate-actions/SKILL.md` = retrieval tools mapping at the 5-axis Gate moment.
- `skills/task-subagent-delegation/SKILL.md` = delegation semantics (what to convey, what to retain) when the parent launches research via subagent.

</position>

<trigger-axis-calibration-primary-category-supporting-or>

## Trigger axis — calibration primary + category supporting (OR)

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

</trigger-axis-calibration-primary-category-supporting-or>

<mode-gate-and-domain-modulators>

## Mode gate and domain modulators

The two trigger gates above answer "is this a search moment". These two modulators answer "how strongly does the trigger apply right now" (mode gate, pre-stage) and "would external retrieval add information at all" (domain tag, suppressor). They modulate the trigger axis; they do not supersede it. The calibration gate's low-confidence fire path survives both modulators.

### Mode gate — question-mode vs work-mode

Pre-stage classification of the current context before the trigger axis is applied at full strength.

| Mode | Context signal | Trigger application |
|---|---|---|
| question-mode | human asked a question / requested information / posed a fact query | full strength — apply the trigger axis as written; one OR hit invokes |
| work-mode | the agent is mid-task (implementing / editing / executing a plan step), no fresh human fact-query | internal-first bias — calibration gate still fires on genuinely low confidence; category gate is damped against incidental time-variant keywords surfacing inside work material |

Work-mode rationale: during task execution, time-variant keywords ("latest", "current") frequently appear inside the work material itself (file content, plan text, log lines) without being a fact-query the agent must externally resolve. Applying the category gate at full strength there over-invokes the skill mid-task.

Escape hatch (work-mode -> retrieve): when the in-progress work genuinely requires an external fact (the agent cannot proceed without confirming a time-variant external state), escape to retrieval regardless of the work-mode damping. The escape preserves correctness; the damping only removes incidental over-invocation, never a real fact dependency.

Mode is a bias on the category gate's strength, not an on/off switch on the trigger axis. Misclassifying work as question over-invokes (recoverable, cost only); misclassifying question as work under-invokes — the escape hatch and the always-live calibration gate are the recovery paths for that direction.

### Domain tag — comparison-informative vs comparison-spins-wheels

Suppressor on the trigger axis. Tag the domain of the claim being formed; the tag decides whether a fired trigger proceeds to retrieve or skips to internal resolution.

| Domain tag | Domain examples | Behavior on trigger fire |
|---|---|---|
| comparison-informative | time-variant fact / API spec / external state / current events | proceed — external retrieval adds information; normal fire |
| comparison-spins-wheels | language (translation / grammar) / math / logic / pure internal judgment with no external gold | skip retrieval even when a trigger keyword surfaced — external retrieval adds no information; internal knowledge / reasoning suffices |

Spin-wheel rationale: in these domains the answer is not an external time-variant state. A translation, a grammatical form, a math derivation, a logic step has no external "current value" that retrieval could refresh — the comparison baseline and the answer source are the same internal surface, so retrieval spins without adding information.

Suppressor scope: the domain tag suppresses the category (time-variant keyword) gate in spin-wheel domains only. It does NOT suppress the calibration gate — if internal confidence is genuinely low on a spin-wheel-domain claim, retrieval (e.g. literal Read of a grammar reference, a spec section) still fires through the calibration path. Suppression targets keyword-driven over-fire, not low-confidence fire.

### Reconciliation with the category gate

The supporting gate (time-variant keyword -> forcibly re-evaluate) is intended for comparison-informative domains, where the world moved past the internal cutoff. In comparison-spins-wheels domains the keyword carries no freshness signal (a grammar rule has no "latest" version that a search refreshes), so the domain suppressor narrows the category gate to where its freshness premise holds. The calibration gate is untouched by both modulators in every domain.

</mode-gate-and-domain-modulators>

<internal-knowledge-role>

## Internal knowledge role

Internal model knowledge is **comparison baseline**, not answer source under these triggers.

- Use internal knowledge to articulate an internal hypothesis before external retrieve (Tier 1 anchor in Block 2; agreement with the single probe early-exits to State A).
- Use internal knowledge to cross-check retrieved content (disagreement fires State C suspicious and escalates to Tier 2).
- Do not synthesize and return the internal hypothesis as the answer when the trigger fired.

When neither gate fires, internal knowledge may serve as the answer directly. The triggers exist precisely to mark the cases where it cannot.

</internal-knowledge-role>

<source-priority>

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

</source-priority>

<block-1-question-type-classification>

## Block 1 — Question type classification

Before issuing the first query, classify into one of:

| Question type | Primary surface |
|---|---|
| past judgment (similar prior decision) | RAG MCP (issues / PRs / commit diff) |
| time-variant external fact (current API, latest spec, recent event) | Web |
| literal source confirmation (does the source actually say X) | Read / git show / gh api |
| similar case / pattern memory | memory grep + RAG MCP |

Classification is not exclusive. Multi-type questions decompose into per-type subqueries handled by Block 2.

</block-1-question-type-classification>

<block-2-tier-1-preview-tier-2-deep-dive>

## Block 2 — Tier 1 preview + Tier 2 deep-dive

Two-tier staged retrieval. Tier 1 is the cheap preview; Tier 2 is the deep-dive invoked only when Tier 1 cannot confirm. Full multi-angle is no longer the default cost.

### Tier 1 — internal hypothesis + single external probe

1. Articulate the internal hypothesis literally before any external query. If no internal opinion exists, explicitly note "no internal opinion" and skip directly to Tier 2.
2. Issue a single external query on the primary surface for the question type (Block 1 mapping). One angle.
3. Cross-check the single probe against the internal hypothesis:
   - **agree** -> terminate retrieval. Synthesize and answer with confidence signal `agree-with-internal`. State A early exit.
   - **disagree** -> escalate to Tier 2. The disagreement itself is the anomaly signal regardless of which side later proves correct.
   - **no internal hypothesis** -> escalate to Tier 2; the comparison baseline is absent so a single probe cannot confirm.

Tier 1 cost = 1 external query. Use this path whenever an internal hypothesis exists.

### Tier 2 — multi-angle + tri-state cross-check

When Tier 1 escalates, generate 3-5 query angles for the same intent and retrieve in parallel.

Angle generation patterns:
- rephrasing (synonyms, abbreviation expansion, language switch)
- viewpoint shift (cause vs effect, structure vs behavior, before vs after)
- granularity shift (specific term vs general concept, instance vs category)
- vocabulary substitution (Li+ internal term vs common technical term)

The internal hypothesis articulated in Tier 1 is carried forward as the comparison reference, not re-issued as an external angle.

Parallel execution:
- Issue all queries in one round when the surface supports it (RAG MCP semantic search, Web search).
- For sequential surfaces (`Read` tool, `git show`), batch within a single tool call cluster.
- Subagent delegation may parallelize further when available; see `skills/task-subagent-delegation/SKILL.md`.

Output of Tier 2 = a set of retrieved snippets, each tagged by angle, fed into Block 3 cross-check.

### Tier vs Stage axis separation

- **Tier** (this block) = retrieval depth axis within the chosen surface (Tier 1 = preview / Tier 2 = deep-dive).
- **Stage** (Block 4) = escalation axis on top of Tier 2 (Stage 1 = same-family re-query / Stage 2 = composite escalation across orthogonal source families).

Block 2 (Tier) decides how deep to dig within one source. Block 4 (Stage) decides when to switch source families.

</block-2-tier-1-preview-tier-2-deep-dive>

<block-3-cross-check-and-three-state-branching>

## Block 3 — Cross-check and three-state branching

Evaluate the retrieved set across angles. The judging AI = Lin / Lay (Character_Instance), not an external scorer.

### State A — sufficient

Either of:
- Tier 1 single probe agrees with the internal hypothesis (early-exit path).
- Tier 2 multiple angles converge on the same answer, with coverage spanning the question's scope and no internal contradiction.

- Action = synthesize and answer.
- Confidence signal = `agree-with-internal` when internal hypothesis matched the external answer (Tier 1 or Tier 2); `no-internal-opinion` when no internal hypothesis was articulated (Tier 2 only).

### State B — insufficient (quantity / coverage gap)

Angles return partial coverage. Some sub-questions unanswered. No contradiction in what was returned.

- Action = re-query within the same source family with new angles (Stage 1 in Block 4). Do not switch surface yet.
- Budget = stay within the per-question query cap (see Block 5).

### State C — suspicious (quality / consistency doubt)

Angles return conflicting answers, or all angles return the same answer with signs of bias (vocabulary echo, single-author dominance, aligned omission).

- Action = composite escalation (Stage 2 in Block 4). Switch to a different source family. Do not retry within the suspicious family.

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

</block-3-cross-check-and-three-state-branching>

<block-4-composite-escalation-axes-stage-1-2>

## Block 4 — Composite escalation axes (Stage 1-2)

When State C fires, choose a composite axis based on the failure mode.

| Failure mode | Composite axis | Concrete switch |
|---|---|---|
| corpus has no answer | multi-index composite | switch source family (RAG -> Web, or RAG -> git log + Read) |
| rephrasings reflect agent bias | decomposition composite | break the question into structurally different sub-questions, retrieve each |
| all sources aligned wrong | time-axis composite + alternate source | query historical commit diff, query independent external source |

Escalation staging (orthogonal to Block 2 Tier axis):
- **Stage 1** = same-family re-query with new angles (State B path).
- **Stage 2** = composite escalation across orthogonal source families (State C path).

Hard stop after one full Stage 2 round if State C remains. Surface to human (Block 5).

</block-4-composite-escalation-axes-stage-1-2>

<block-5-stop-condition>

## Block 5 — Stop condition

Stop when one of:

1. State A reached. Synthesize and answer.
2. State C unresolved after one composite escalation round. Surface to human with what was tried and what remains.
3. Query budget exhausted. Soft cap = 9 queries across all blocks (1 Tier 1 + up to 5 Tier 2 multi-angle + up to 3 Block 4 Stage 1/2 escalation). Hard stop = 12.
4. Corpus boundary detected (consistent "no result" across multiple angles and at least one alternate source family). Surface to human.

Do not loop indefinitely. Loop Safety (`skills/model-loop-safety/SKILL.md`) applies: same approach twice in dialogue, three times in task = stop and switch.

</block-5-stop-condition>

<three-roles-of-the-judging-ai>

## Three roles of the judging AI

Within one retrieval moment, three judgments stack:

1. **cross-check evaluation** — sufficient / insufficient / suspicious classification (Block 3)
2. **composite path selection** — failure mode to composite axis mapping (Block 4)
3. **stop-time judgment** — budget / corpus boundary / human escalation (Block 5)

These judgments are Character_Instance-prefixed dialogue surface when surfaced to human, internal reasoning when not.

</three-roles-of-the-judging-ai>

<web-specific-consumption-discipline>

## Web-specific consumption discipline

When the retrieval surface chosen is Web (`WebSearch` / `WebFetch`), additional consumption discipline applies on top of Block 3 cross-check.

### Citation handling

- Cite the source URL alongside the claim. Public-document backing increases value.
- Prefer official guides / spec docs over secondary articles.
- Disagreement between multiple Web sources fires State C suspicious (Block 3); switch source family or surface to human.

### Model-knowledge baseline reminder

Internal model knowledge is comparison baseline, never the Web answer source under the trigger axis. Even when internal knowledge agrees with the Web result, the agreement is the cross-check signal, not the basis for skipping citation.

When the trigger axis did not fire (universal concept explanation, stable design principle), Web search is unnecessary and internal knowledge serves as the answer directly. The trigger axis is the gate; Web-side consumption discipline applies only on the search-side of that gate.

</web-specific-consumption-discipline>

<parent-ai-governance-pre-retrieval>

## Parent-AI governance (pre-retrieval)

When the parent AI launches a research task, the parent retains the following governance regardless of whether the mechanical core runs in the parent context or a subagent.

### Verification-first

When uncertain, verify externally before proceeding.
Correctness optimization outweighs speed optimization.

### Context preservation

Choose retrieval path that preserves main working context.
When subagent is available, proactively launch parallel subagents for research.
When subagent is unavailable, run the mechanical core directly in the parent context.
Strategy is environment-independent; execution means vary.

### Proactive parallel research

When investigating an issue:
- Before forming judgment, launch parallel subagents to fetch related issues, PRs, and diffs.
- Do not wait for human to request each retrieval step individually.

Subagent availability determines execution but not initiative. Initiative is mandatory regardless of environment.

</parent-ai-governance-pre-retrieval>

<parent-ai-consumption-discipline-post-retrieval>

## Parent-AI consumption discipline (post-retrieval)

When a retrieval result returns to the parent AI, the parent retains the following consumption discipline on top of the mechanical Block 3 / Block 5 surface.

### Budget gate (governance side)

Per-question query budget:
- soft cap = 9 queries across the full retrieval round (Block 2 Tier 1 + Tier 2 multi-angle + Block 4 Stage 1/2 escalation, as defined above).
- hard stop = 12.
- per-task budget = inherited from task scope; no separate cap here.

On hard cap hit = stop. Surface to human with what was tried and what remains uncertain. Loop Safety (`skills/model-loop-safety/SKILL.md`) applies in parallel: same approach twice in dialogue, three times in task = stop and switch.

### Stop condition (governance side)

The four mechanical stop states (State A synthesize / State C unresolved / budget exhausted / corpus boundary) are defined in Block 5 above. The parent retains the judgment of:

- when to surface partial findings to human vs continue another round
- whether the question is decomposable into a follow-up retrieval task instead of forcing more queries
- whether to file a follow-up issue capturing what remains uncertain

### Naive single-shot defense

Naive single-shot RAG consumption fails on corpus boundary, recognition bias, and aligned errors. The parent must not collapse the mechanical multi-angle protocol back into single-shot when the result feels "good enough" too early — Block 3 cross-check is the canonical gate, not the parent's intuition.

</parent-ai-consumption-discipline-post-retrieval>

<observation-and-evolution>

## Observation and evolution

Single environment cannot benchmark this skill against alternatives. Observation loop instead:
- log failure cases (hit State C, escalation chosen, outcome) to `memory/feedback.md` or self-evaluation log when notable
- side-by-side compare with naive single-shot consumption when retrospectively visible
- feed observations into evolution loop observe stage (`skills/evolution-loop/SKILL.md`)

Mode gate + domain modulator observation set (Phase 4 heuristics, calibration-pending):
- mode misclassification frequency — question read as work (under-invoke risk, caught by escape / calibration) vs work read as question (over-invoke, cost only). Log the direction.
- domain tag hit rate — spin-wheel claims correctly skipped vs informative claims correctly retrieved; note tag misfires (informative claim skipped = a real miss).
- escape fire frequency — work-mode -> retrieve escapes. Near-zero escape with frequent work-mode damping suggests the damping is too aggressive (real fact dependencies being dropped); frequent escape suggests the work-mode bias is mostly cosmetic.

Promotion of recurring patterns to L1 / L2 spec follows `rules/evolution/promotion-judgment.md`.

</observation-and-evolution>

</agentic-search>
