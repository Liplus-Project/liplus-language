---
globs:
alwaysApply: true
layer: L5-notifications
---

<notifications>

# Notifications

Canonical for how events reach the main agent. Japanese specification: `docs/5.-Notifications.md`.
Actor = the main agent on every section below.

<delivery-shapes>

## Delivery shapes

Two ways of receiving, chosen by what the environment can run:
- channel (event-driven) = `LI_PLUS_WEBHOOK_DELIVERY=channel`. Events are pushed; nothing is polled. Use it where the host carries it.
- polling = the substitute where channel is not available: `poll` and `mcp_hook` for the webhook target, and GitHub Notifications.

Two targets are received:
- webhook events = Foreground webhook notification intake below.
- GitHub Notifications = GitHub Notifications below. It needs `GH_CLASSIC_TOKEN` only, no MCP, and is the polling base for an environment that has nothing else.

Every consumed webhook event is marked with mark_processed, whatever the delivery shape.

</delivery-shapes>

<foreground-webhook-notification-intake>

## Foreground webhook notification intake

Canonical. `skills/operations-foreground-webhook-intake/SKILL.md` holds the pointer.
Webhook target of Delivery shapes above.
Actor = the main agent only (the firing moment is the start of a user turn).

Do not search GitHub broadly for "maybe new comment" when a delivered event source already exists.

Use only in hosts that can run a local command before replying.

source priority:
  1 = mcp__github-webhook-mcp
  2 = local webhook store via bundled helper
  3 = GitHub Notifications (below), when `GH_CLASSIC_TOKEN` is present
  4 = none

delivery mode interaction (LI_PLUS_WEBHOOK_DELIVERY):
  poll (default) = each user turn, the on-user-prompt UserPromptSubmit hook injects the instruction
    to call mcp__github-webhook-mcp__get_pending_status, and the AI issues the call itself.
  channel        = MCP channel pushes events; AI does not poll, intake reads the channel surface.
  mcp_hook       = the type=mcp_tool UserPromptSubmit hook entry in the default
    settings.json template calls mcp__github-webhook-mcp__get_pending_status at hook time and
    injects the result into prompt context. The AI does not issue the call itself; foreground
    handling reads the injected status as if it had been polled.
    When github-webhook-mcp is not connected, the mcp_tool resolver returns plain `not connected`
    text per turn — harmless but visible noise.
  source priority above is unchanged across modes; only the *who initiates the call* axis
  differs. Relevance judgment and destructive consume rules apply identically.

local webhook store:
  precondition = LI_PLUS_MODE=clone
  helper path = {workspace_root}/liplus-language/scripts/check_webhook_notifications.py
  state dir resolution:
    a = LI_PLUS_WEBHOOK_STATE_DIR from Li+config.md (absolute or workspace_root-relative)
    b = {workspace_root}/github-webhook-mcp
    c = {workspace_root}/../github-webhook-mcp
  state dir shape check = a candidate that exists is a state dir only if it carries at least one of the
    names the helper reads (`events.json`, `notification-claims.json`, `trigger-events/`, `codex-runs/`).
    A candidate failing it is not resolved: move to the next candidate, and treat all candidates failing
    as unresolved. The directory name alone does not settle it. The name list is held in
    `scripts/check_webhook_notifications.py`.
  if helper missing or state dir unresolved = skip silently
  a silent skip is not an observation of the backlog. Do not report it as "no pending events" — on that
    axis say nothing, which is what the silent skip already is.
  helper output = inspect summary with foreground-matched items, notable items, and cleanup candidates
  helper default = inspect only; preserve unmatched backlog
  destructive actions = explicit `read` / `done` / `claim` / `cleanup-safe-success` calls only

foreground handling:
  each user turn start = inspect once before main reply
  mention only = foreground-matched items, exceptional notable items, or an event the hold exit
    below names
  if relevance cannot be judged cheaply = preserve and stay silent. An event held at ownership test
    step 4 is outside this line until the hold exit has named it.
  full payload = open only when deeper inspection is needed
  separate AI process launch = prohibited for this flow

own-operation arrival confirmation:
  webhook notifications include results of own operations (push, PR, issue, release).
  these serve as arrival confirmation = proof that the operation reached GitHub.
  mark_processed own-operation events promptly during the foreground check.
  do not accumulate own-operation events for bulk clearing later.
  external events (other users, bots) = preserve for foreground reporting or explicit handling.

  ownership test - run it; own / external is not judged by feel:
    1. head_branch = this session's working branch -> own.
    2. match the event against what this session wrote to. `wrote to` is the whole write set, not
       the creation; issue authorship is not the question. The write set includes what this
       session's write commands returned: the URL or number of each issue, PR and comment created.
       - workflow_run on any head_branch -> read `gh run view <id> --json displayTitle` and match it
         against the write set (event=issues carries the issue title, push the commit title,
         pull_request the PR title).
       - issue_comment / pull_request_review / issues / pull_request, sender = the account this
         session writes as -> own when the event's issue or PR number is in the write set.
    3. sender is another account -> external, preserve.
    4. nothing above settles it -> hold, and leave the event unprocessed. A sender that is the
       account this session writes as reaches here when 1 and 2 do not match it; step 3 does not
       take it.

    Hold exit: at the next foreground check, run the test again on every held event. An event still
    unsettled is named once, in that turn's reply, as held with its owner unknown. From then on it
    is preserved as step 3 preserves, and is not named again.

    Residual limit at step 2, accepted: two sessions writing to one issue each read both runs as own.
    Do not repair it by narrowing step 2 back to creation.

</foreground-webhook-notification-intake>

<github-notifications>

## GitHub Notifications

Canonical.
Read at the foreground check when source priority above reaches it, and whenever the Inbox is acted on directly.

Token = the `GH_CLASSIC_TOKEN` environment variable (classic PAT, scope = notifications). Pass it to `gh api` by reference to the variable, never as its value in the command string. Absent -> this target is unavailable; skip silently, as the local store does.

PATCH  /notifications/threads/{id}   -> 205  read (stays in Inbox)
PUT    /notifications {"read":true}  -> 205  mark all read
DELETE /notifications/threads/{id}  -> 204  done (removed from Inbox)
GET    /notifications?all=false      -> 200  check inbox

Foreground handling, the ownership test and the hold exit apply to Inbox threads as they apply to webhook events; `read` / `done` stand where mark_processed stands.

</github-notifications>

</notifications>
