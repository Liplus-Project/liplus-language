---
name: model-review-output-partition
description: Invoke when review or critique or risk output is about to be produced. Provides the now, later and accepted classification partition.
layer: L1-model
---

<review-output-partition>

# Review Output Partition

For review / critique / risk output:
  now      = blocks current action
  later    = valid but non-blocking follow-up
  accepted = human-accepted limitation or tradeoff

If human already placed a point in later or accepted:
  keep classification
  do not escalate without new fact

</review-output-partition>
