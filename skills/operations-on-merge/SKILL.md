---
name: operations-on-merge
description: Invoke after self-review + mode gate pass; mergeable state check, squash merge, parent auto-close on merge.
layer: L4-operations
---

# Merge

Merge executor is AI in every mode (trigger / semi_auto / auto).
AI runs `gh pr merge` after all preconditions pass (self-review + mode-specific human gate, and mergeable state check). GitHub auto-merge handoff is no longer used.

Pre-merge mergeable state check:
  gh pr view {pr} -R {owner}/{repo} --json mergeStateStatus --jq '.mergeStateStatus'
  CLEAN -> proceed to merge.
  BEHIND -> git fetch origin main && git rebase origin/main && git push --force-with-lease -> restart [CI Loop] from step1.
  CONFLICTING -> attempt rebase: git fetch origin main && git rebase origin/main
    if rebase succeeds: git push --force-with-lease -> restart [CI Loop] from step1
    if rebase fails: git rebase --abort -> comment on issue -> escalate to human
  BLOCKED or UNKNOWN -> wait and recheck (GitHub may still be computing)

Merge strategy:
  Default = squash (repo convention).
  All modes = AI runs: gh pr merge {pr} -R {owner}/{repo} --squash
  Deviation from squash = AI pauses and asks human.

Parent close condition: closed automatically on merge via issue reference.

Real device test:
Merge first. Then test on main. Not a merge gate.
