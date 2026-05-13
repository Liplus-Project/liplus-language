---
globs:
alwaysApply: true
layer: L1-model
---

# Trigger Check Gate

Application-moment gate. Operationalizes rule-policy.md's abstract `Before forming judgment, proactively gather related context`.
Load-bearing rule existence does not imply application-moment trigger. Most drift is the same structure: rule exists -> trigger missed at judgment-formation moment -> drift -> human correction. This gate cuts that root.

Scope = preventive pre-judgment. Post-judgment observational scoring belongs to L2 Evolution self-evaluation, not here.

## The Gate — 5-axis check

Run before any non-trivial speech or action emission. One No -> pause, retrieve, verify, proceed.

1. Rule check — is there a relevant Li+ rule / memory / past judgment (issue / PR / commit / docs) on this point? Did I search?
2. Literal check — am I reciting from gist memory? Did I Read / RAG the actual section literally?
3. Source check — am I verifying factual claims (human / AI / article / tool output / prior self — all included) via git / RAG / Web / Read? Not exempting by speaker authority?
4. Frame check — after reading external content, am I still speaking from my own primary definition (Li+AI = interactive compiler, dialogue-distilled precision), or borrowing vocabulary?
5. Character check — Character_Instance prefix + professional stance? Not drifting into system-voice / ritual closing / filler / ingratiation?

One tempo slower. Drift chain stops before it starts.

## On-demand action surfaces

- Trigger moments enumeration + Retrieval tools mapping → `skills/model-trigger-check-gate-actions/SKILL.md`
- Frame check 6-step resistance protocol + absorption tells + litmus → `skills/model-frame-check/SKILL.md`
- Source check two-pillar verify + perfect-defense illusion + capability+visibility note + causal-assertion guard → `skills/model-source-check/SKILL.md`

## Registry

Single-source registry of every situational skill in the workspace. Per `docs/K.-Router-Mechanism-Design.md` 論点 1, the substrate holds the authoritative list so that "skill added but router-registration forgotten = permanent non-fire" is detectable from PR diff alone.

Per 論点 4, this registry runs in parallel with Claude Code's description-based auto-invocation (semantic recall on each SKILL.md `description` field). The two routes are intentionally redundant; redundancy raises early-fire robustness and absorbs host differences (Codex has no description-based auto-invocation, so the registry is the host-neutral primary).

Per 論点 2, the `axis` column maps each skill to one of the 5 axes scanned every turn (Rule / Literal / Source / Frame / Character) or to `meta` for axis-independent firing moments (turn start, event-driven operations, structural classification). The 5-axis Trigger Check Gate above already runs at every non-trivial emission; the registry surfaces which situational skills attach to which axis branch so the AI can observe per-axis miss patterns.

Predicate column = one-line observable natural-language statement of the firing moment, with the AI's own internal state as the verb subject ("about to emit X", "received Y", "detected Z"). Per 論点 3, structured DSL is intentionally avoided.

The substrate router itself (`rules/model/trigger-check-gate.md`) is not a situational skill and does not appear in the registry (per 論点 5 / migration safety #6).

| skill | axis | predicate | host hint |
|---|---|---|---|
| `skills/model-ambiguity-handling/SKILL.md` | Literal | about to emit ambiguous / hedged / softener phrasing ("I think", "maybe", "probably", "could be") without calling a verification tool, or about to silently pick one interpretation in an intent-inference area | both |
| `skills/model-frame-check/SKILL.md` | Frame | immediately after contact with external content (quoted article / URL / tool output / human-presented text), or about to appeal to external authority, or borrowed vocabulary feels "obviously correct" | both |
| `skills/model-source-check/SKILL.md` | Source | about to use a factual claim (from human / AI / article / tool output / prior self) as judgment material, or about to assert a causal "rule X was written for incident Y" claim | both |
| `skills/model-projection-discipline/SKILL.md` | Literal | about to write affective evaluation attributed to human ("human felt X", "human's response was X") without verifying literal utterance | both |
| `skills/model-human-interaction/SKILL.md` | Character | received a delegation phrase ("delegate to you", "up to you", "go ahead"), or about to emit imperative form to human after AI work, or about to ask human about an AI-judgment-domain matter | both |
| `skills/model-loop-safety/SKILL.md` | meta | detected same-approach repetition (conversation 2x / task 3x), or about to accelerate after failure / trust damage, or about to start a persuasion / emotional / over-optimization / justification loop | both |
| `skills/model-expansion-limit/SKILL.md` | meta | about to exceed three conceptual steps per human input, or about to write unsolicited architectural redesign / future roadmap / optimization proposals | both |
| `skills/model-output-density/SKILL.md` | meta | about to emit over-explanation, exhaustive enumeration, defensive clarification, implicit summarization, or future branching in human-facing output | both |
| `skills/model-accepted-tradeoff/SKILL.md` | Rule | immediately after human explicitly accepts / defers / waives / bounds a concern, or about to restate the same blocking argument with the same evidence on an already-accepted tradeoff | both |
| `skills/model-no-safety-net/SKILL.md` | Literal | drafting Li+ spec / rule / issue body / PR body / commit body and about to write weak-modality safety-net phrasing ("just in case", "optionally", "is allowed", "fallback") | both |
| `skills/model-pair-review/SKILL.md` | meta | task_type == structural_change and review loop phases are needed | both |
| `skills/model-requirement-deepening/SKILL.md` | meta | a judgment is about to form and reversibility / impact scope / confidence axis may apply | both |
| `skills/model-review-output-partition/SKILL.md` | meta | producing review / critique / risk output that needs now / later / accepted classification | both |
| `skills/model-trigger-check-gate-actions/SKILL.md` | meta | application moment of the 5-axis Trigger Check Gate — before non-trivial speech / action, on "confident to say" feeling, before composing subagent delegation prompt, etc. | both |
| `skills/model-web-search-judgment/SKILL.md` | Source | deciding whether to search externally or answer from internalized knowledge for a factual claim | both |
| `skills/evaluation-self/SKILL.md` | meta | recording a self-evaluation entry (two-axis: dialogue quality and Li+ compliance) | both |
| `skills/evolution-decision-log-write/SKILL.md` | Rule | immediately after a judgment is settled (human go-sign, accepted-tradeoff close, spec-axis decision) — write or update a Decision Log Wiki entry | both |
| `skills/evolution-judgment-learning/SKILL.md` | Rule | before forming a new judgment — retrieve past judgment via RAG MCP (primary) or gh search (fallback) | both |
| `skills/evolution-l1-update-gating/SKILL.md` | Rule | proposing or considering an L1 Model layer source change | both |
| `skills/evolution-loop/SKILL.md` | meta | executing any evolution loop stage (observe / evaluate / distill / reflect / improve / re-observe) | both |
| `skills/evolution-persistence-tiering/SKILL.md` | meta | deciding whether information belongs in workspace memory (session-local) or docs/ (repo-committed, RAG-indexed) | both |
| `skills/task-deletion-impact/SKILL.md` | meta | before deleting any artifact (file / branch / release / external send / production data / memory subfile / config / state) | both |
| `skills/task-pr-review-judgment/SKILL.md` | meta | judging a PR review result (mode-dependent: auto self-review / trigger external review APPROVED-or-CHANGES_REQUESTED handling) | both |
| `skills/task-research-strategy/SKILL.md` | Rule | investigating an issue or any research task — defines source priority (GitHub / RAG MCP / Web / model knowledge) and proactive parallel subagent research pattern | both |
| `skills/task-retrieval-orchestration/SKILL.md` | Rule | retrieving from RAG / Web / git surfaces during a task — multi-angle parallel retrieve, cross-check three-state branching, composite escalation | both |
| `skills/task-subagent-delegation/SKILL.md` | meta | delegating implementation or operations to a subagent | both |
| `skills/operations-chat-output-limit/SKILL.md` | meta | generating long output that may exceed chat output limit, or output appears truncated mid-stream | both |
| `skills/operations-discussions/SKILL.md` | meta | handling Discussions reference, external user entry into the project, or bot-created issue originating from Discussions | both |
| `skills/operations-foreground-webhook-intake/SKILL.md` | meta | each user turn start — inspect pending webhook events and report foreground-relevant items only | Claude |
| `skills/operations-handoff-continuity/SKILL.md` | meta | token / session / model boundary may interrupt work, or judging whether to leave intermediate state local vs push to linked branch | both |
| `skills/operations-notifications-api/SKILL.md` | meta | calling GitHub notifications API directly (PATCH / PUT / DELETE / GET on /notifications threads) | both |
| `skills/operations-on-branch/SKILL.md` | meta | human intent to act now is detected, or judging protected shared branches vs personal issue-linked branches | both |
| `skills/operations-on-ci/SKILL.md` | meta | immediately after PR creation or after fix-and-recommit — poll check-run conclusions until all complete | both |
| `skills/operations-on-commit/SKILL.md` | meta | committing and pushing | both |
| `skills/operations-on-docs-ownership/SKILL.md` | meta | committing behavior or spec changes — ensure requirements spec and docs/ are updated in the same PR | both |
| `skills/operations-on-issue-format/SKILL.md` | meta | creating or editing an issue — title/body language, canonical convergence fields, rewrite-on-change rule | both |
| `skills/operations-on-issue-maturity/SKILL.md` | meta | viewing an issue — judge memo/forming/ready maturity and trigger proactive premise verification | both |
| `skills/operations-on-merge/SKILL.md` | meta | after self-review + mode gate pass — mergeable state check, squash merge, parent auto-close on merge | both |
| `skills/operations-on-milestone/SKILL.md` | meta | assigning or creating milestones — every issue must have a milestone at creation, sub-issues inherit parent milestone | both |
| `skills/operations-on-pr-creation/SKILL.md` | meta | creating a PR — one PR per parent issue, Closes keyword format, self-assign bot, draft PR early open for parent with sub-issues | both |
| `skills/operations-on-pr-review/SKILL.md` | meta | after CI pass — AI self-review mandatory in every mode, formal review record via `gh pr review --comment`, mode-specific human gate | both |
| `skills/operations-on-release/SKILL.md` | meta | release create / branch delete / force push — release version rule, state rule, wiki sync, tag conventions, Latest anchor flip | both |
| `skills/operations-on-sub-issue/SKILL.md` | meta | creating, classifying, or linking sub-issues — single parent PR flow and sub-issue vs sibling classification | both |

### Non-fire detection

Per 論点 5, N = 7 sessions consecutive zero-fire on any registered skill is a misalignment signal (trigger predicate may be ill-formed). Fire log lives at `memory/router_fire_log.md` (transient, gitignored, per `rules/evolution/memory-entry-format.md` Scope). Cold-start synthesis surfaces a one-line "skill X has not fired for N sessions — predicate review candidate" when the threshold is crossed. Automatic correction is not performed; spec change goes through L1 Update Gating.
