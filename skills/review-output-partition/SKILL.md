---
name: review-output-partition
description: Invoke when producing review / critique / risk output (now / later / accepted classification).
layer: L1-model
---

# Review Output Partition

For review / critique / risk output:
  now      = blocks current action
  later    = valid but non-blocking follow-up
  accepted = human-accepted limitation or tradeoff

If human already placed a point in later or accepted:
  keep classification
  do not escalate without new fact
