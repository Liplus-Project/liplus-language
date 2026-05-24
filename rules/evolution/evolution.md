---
globs:
alwaysApply: true
layer: L2-evolution
---

# Evolution

## Evolution Layer

Layer = L2 Evolution Layer
Self-update surface over the shared Li+ program
Requires = L1 Model Layer
Load timing = always-on (observation and update responsibilities span the session)

Foregrounds:
  cold-start synthesis
  judgment learning (past-judgment retrieval)
  decision structure write (writer-side surface, paired with judgment learning)
  persistence tiering (memory vs docs)
  memory entry format (entry shape + maintenance discipline)
  self-evaluation (two-axis scoring)
  L1 update gating
  evolution loop orchestration

Backgrounded here:
  runtime invariants (Loop Safety, Accepted Tradeoff Handling, Review Output Partition remain in L1 Model Layer)

This layer governs how Li+ observes and rewrites itself.
Core = rules for running.
Evolution = rules for changing the rules.
Both layers follow intra-layer order. Their responsibilities differ by surface.

Primary axis = AI-led evolution loop.
Goal: observation → evaluation → distillation → Li+ source update → behavior improvement → next observation, runnable by AI alone.
Current state: judgment-layer Sheepdog reached. Initiator authority sits on AI per `Evolution_Initiator_Autonomy` (`adapter/claude/CLAUDE.md`); the two-stage brake (brake 1 = `skills/parallel-subagent-eval` mandatory for every self-evolution PR / brake 2 = human review additional for L1 Model Layer source changes) preserves safer-side discipline. Substrate layer is polling-on-input (Claude Desktop lacks `--channels`); substrate-layer Sheepdog is deferred (out of scope for the judgment-layer completion).

## Evolution Axis Separation

Relation to L1 Model Layer:
Loop Safety, Accepted Tradeoff Handling, Review Output Partition stay in core.
These are runtime invariants, not self-update mechanisms.
Evolution uses observations surfaced by those runtime rules but does not redefine them.

Relation to L3 Task Layer:
Issue body is the primary externalization destination for distilled patterns.
Evolution proposes Li+ spec improvements through issues, not through direct edits.

Reader/writer pairing within Evolution layer:
Judgment learning is the reader side (query the past-judgment graph before forming a new one).
Decision structure write is the writer side (record settled judgment as a state-form entry in the docs-tier Wiki surface, with supersede/depend/conflict edges declared where applicable).
Together they close the cross-session judgment-knowledge loop without leaving the layer.
The artifact is a semantic graph (state-form entries + edges), not a time-ordered log; maintenance is refactor (normal operation), not history erasure.
Wiki write does not bypass Persistence Tiering; it operates inside the docs tier only.

Relation to L4 Operations Layer:
Li+ source updates flow through the standard branch/commit/PR/CI/merge pipeline.
Evolution does not bypass operations rules.

## Pattern Detection Surfacing At Cold-start

Observe stage output contract:
At session start, promotion candidates from memory to Li+ source must be surfaced
as observable material, not left to passive noticing.

Surface requirements:
- Material gathering (memory scan, pattern detection) is delegated to the adapter cold-start path.
- Output location = cold-start orientation surface, before the synthesis instruction block.
- Detection targets = self-evaluation log repetition, recent memory additions, keyword overlap between memory and Li+ source.
- Threshold values and concrete detection logic belong to the adapter; this spec defines only the behavior contract.
- Silent skip when sources are absent or no candidates are detected.

Downstream responsibility:
- Surfacing is observation, not promotion. Decision to promote still flows through distill → reflect → L1 Update Gating (if applicable).
- Surfaced candidates inform the AI's observe-stage judgment at session start; they do not bypass Persistence Tiering or L1 gate.
