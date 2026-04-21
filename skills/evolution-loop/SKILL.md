---
name: evolution-loop
description: Invoke when executing any evolution loop stage (observe / evaluate / distill / reflect / improve / re-observe).
layer: L2-evolution
---

# Evolution Loop

Loop stages:
  observe    = memory entries + docs (spec, decision log, issue history)
  evaluate   = self-evaluation two-axis scoring, pattern detection
  distill    = extract spec-class signal from repeated patterns
  reflect    = update Li+ source (default target = L3 and later; L1 via gating)
  improve    = behavior shifts with the updated spec
  re-observe = next cycle starts from new memory/docs state

Execution mode:
  current    = partial automation; some stages still handed to human.
  target     = AI-sole execution of the full loop, with human as approver for L1 gate and release.

Stage responsibility:
  observe/evaluate = AI autonomous. No human prompt needed.
  distill          = AI autonomous. Externalize to issue when a pattern crosses the memo-level threshold.
  reflect          = AI drafts (PR). Human approves merge per operations/Li+github.md.
  improve          = AI executes under the updated spec.
  re-observe       = AI autonomous.
