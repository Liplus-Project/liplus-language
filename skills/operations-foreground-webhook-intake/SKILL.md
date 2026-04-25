---
name: operations-foreground-webhook-intake
description: Invoke at each user turn start; inspect pending webhook events via MCP or local helper, report foreground-relevant or notable items only.
layer: L4-operations
---

# Foreground Webhook Notification Intake

Purpose:
Keep the active foreground thread lightweight.
Do not search GitHub broadly for "maybe new comment" when a delivered event source already exists.

Use only in hosts that can run a local command before replying.

source priority:
  1 = mcp__github-webhook-mcp
  2 = local webhook store via bundled helper
  3 = none

delivery mode interaction (LI_PLUS_WEBHOOK_DELIVERY):
  poll (default) = each user turn, the AI calls mcp__github-webhook-mcp__get_pending_status.
  channel        = MCP channel pushes events; AI does not poll, intake reads the channel surface.
  mcp_hook       = a type=mcp_tool UserPromptSubmit hook entry invokes
                   mcp__github-webhook-mcp__get_pending_status directly at hook time
                   and injects the result into prompt context. The AI does not
                   issue the call itself; foreground handling reads the injected
                   status as if it had been polled.
  source priority above is unchanged across modes; only the *who initiates the
  call* axis differs. Relevance judgment and destructive consume rules apply
  identically.

local webhook store:
  precondition = LI_PLUS_MODE=clone
  helper path = {workspace_root}/liplus-language/scripts/check_webhook_notifications.py
  state dir resolution:
    a = LI_PLUS_WEBHOOK_STATE_DIR from Li+config.md (absolute or workspace_root-relative)
    b = {workspace_root}/github-webhook-mcp
    c = {workspace_root}/../github-webhook-mcp
  if helper missing or state dir unresolved = skip silently
  helper output = inspect summary with foreground-matched items, notable items, and cleanup candidates
  helper default = inspect only; preserve unmatched backlog
  destructive actions = explicit `read` / `done` / `claim` / `cleanup-safe-success` calls only

foreground handling:
  each user turn start = inspect once before main reply
  mention only = foreground-matched items or exceptional notable items
  if relevance cannot be judged cheaply = preserve and stay silent
  full payload = open only when deeper inspection is needed
  separate AI process launch = prohibited for this flow

own-operation arrival confirmation:
  webhook notifications include results of own operations (push, PR, issue, release).
  these serve as arrival confirmation = proof that the operation reached GitHub.
  mark_processed own-operation events promptly during foreground check or after the triggering operation.
  do not accumulate own-operation events for bulk clearing later.
  external events (other users, bots) = preserve for foreground reporting or explicit handling.
