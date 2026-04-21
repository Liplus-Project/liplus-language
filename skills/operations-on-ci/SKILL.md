---
name: operations-on-ci
description: Invoke immediately after PR creation or after fix-and-recommit; polls check-run conclusions via webhook or gh api until all complete.
layer: L4-operations
---

# CI Loop

CI loop starts immediately after PR creation or after fix-and-recommit.
CI loop is a separate task from PR creation. Do not skip.

step1 = get latest commit sha:
  gh pr view {pr} -R {owner}/{repo} --json headRefOid --jq '.headRefOid'
step2 = wait for all check-runs to complete:
  Prefer webhook over polling.
  if mcp__github-webhook-mcp available:
    poll get_pending_status every 60 seconds
    on check_run pending: list_pending_events -> get_event for check_run events -> verify sha match -> mark_processed
    collect conclusions until no in-flight check-runs remain
  else:
    gh api repos/{owner}/{repo}/commits/{sha}/check-runs --jq '.check_runs[] | {name,status,conclusion}'
    repeat with sleep until: all status=="completed"
step3 = conclusion judgment (refs #460):
  CI fail = any conclusion=="failure"
  CI pass = all conclusion in [success, skipped, neutral]
CI pass -> proceed to [PR Review].
CI fail -> fix and recommit (restart CI loop from step1).
CI loop safety (ref: Li+core.md#Loop Safety task/debug threshold):
If still failing = externalize to issue comment, escalate to human.
