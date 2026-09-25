#!/bin/bash
# Source: adapter/codex/hooks/on-user-prompt.sh ({LI_PLUS_TAG})
# Codex UserPromptSubmit hook (portable POSIX fallback).
# Port of adapter/claude/hooks/on-user-prompt.sh; the Windows-native path is the
# sibling on-user-prompt.ps1 (wired via hooks.json commandWindows). This .sh is
# the `command` (non-Windows / POSIX shell) handler.
#
# Per-turn Trigger Check Gate re-arm + webhook reminder. The gate re-arm is the
# deterministic firing surface for rules/model/trigger-check-gate.md.
# Character_Instance is loaded via AGENTS.md (always-present root instruction),
# not re-notified per turn.
#
# Codex contract difference vs Claude: UserPromptSubmit context injection on
# Codex requires JSON on stdout (hookSpecificOutput.additionalContext). Claude
# accepts plain text; Codex does not. So this port wraps the gate text into the
# JSON envelope (jq if present, manual escape fallback otherwise).
export PATH="$HOME/.local/bin:$PATH"

# Read stdin payload (Codex passes JSON: session_id, cwd, hook_event_name, ...).
HOOK_INPUT=""
if [ ! -t 0 ]; then
  HOOK_INPUT=$(cat 2>/dev/null || true)
fi

# Resolve project root: prefer payload cwd, fall back to CODEX_PROJECT_DIR / PWD.
PROJECT_ROOT=""
if [ -n "$HOOK_INPUT" ] && command -v jq >/dev/null 2>&1; then
  PROJECT_ROOT=$(printf '%s' "$HOOK_INPUT" | jq -r '.cwd // empty' 2>/dev/null)
fi
[ -n "$PROJECT_ROOT" ] || PROJECT_ROOT="${CODEX_PROJECT_DIR:-$PWD}"

# --- Webhook delivery mode (poll / channel / mcp_hook) ---
WEBHOOK_DELIVERY=$(awk -F= '/^LI_PLUS_WEBHOOK_DELIVERY=/{print $2}' "$PROJECT_ROOT/Li+config.md" 2>/dev/null | tr -d '\r')

CONTEXT=""
append() { CONTEXT="${CONTEXT}$1
"; }

# --- Li+ update status re-emit (#1987) ---
# Mirrors the claude port, reading .codex/state/update-status.txt (written by
# on-session-start.sh / .ps1) and the sentinel tag in AGENTS.md. Same condition,
# same lines.
UPDATE_STATE=$(head -n 1 "$PROJECT_ROOT/.codex/state/update-status.txt" 2>/dev/null | tr -d '\r')
RECORDED_TARGET=$(printf '%s' "$UPDATE_STATE" | sed -n 's/^status=needed target=\([^ ]*\) adapter=\([^ ]*\)$/\1/p')
RECORDED_ADAPTER=$(printf '%s' "$UPDATE_STATE" | sed -n 's/^status=needed target=\([^ ]*\) adapter=\([^ ]*\)$/\2/p')
CURRENT_ADAPTER=$(sed -n 's/^# --- Li+ BEGIN (\([^)]*\)) ---.*/\1/p' "$PROJECT_ROOT/AGENTS.md" 2>/dev/null | head -n 1)
if [ -n "$RECORDED_TARGET" ] && [ "$CURRENT_ADAPTER" != "$RECORDED_TARGET" ] && [ "$CURRENT_ADAPTER" = "$RECORDED_ADAPTER" ]; then
  append ""
  append "━━━ Li+ update status ━━━"
  append "LI_PLUS_UPDATE_STATUS=needed reason=sentinel-tag(adapter=${CURRENT_ADAPTER:-unknown},target=$RECORDED_TARGET)"
  append "AI must read Li+config.md and execute Li+update.md walkthrough this session."
  append "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
fi

# Unknown-value surfacing (#1804). Rationale is in the claude port this one
# mirrors.
case "$WEBHOOK_DELIVERY" in
  ""|poll|channel|mcp_hook) ;;
  *)
    append ""
    append "━━━ Li+config: unrecognized value ━━━"
    append "LI_PLUS_WEBHOOK_DELIVERY=$WEBHOOK_DELIVERY is not one of: poll / channel / mcp_hook. Values are case-sensitive. Falling back to the default (poll)."
    append "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    ;;
esac

# The call half is poll-only; the handling half is unconditional. Rationale
# and the #1798 failure it repairs are in the claude port this one mirrors.
append ""
append "━━━ Webhook: check pending notifications ━━━"
if [ "$WEBHOOK_DELIVERY" != "channel" ] && [ "$WEBHOOK_DELIVERY" != "mcp_hook" ]; then
  append "Run mcp__github-webhook-mcp__get_pending_status silently."
fi
append "Report only foreground-relevant or notable items."
append "mark_processed every consumed event; own-operation arrivals promptly."
append "Intake detail: rules/operations/main-agent-procedures.md Foreground webhook notification intake; mark_processed mandate: rules/operations/operations.md Operations Rules (both always-on)."
append "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# --- Trigger Check Gate re-arm (every turn) ---
append ""
append "━━━ Trigger Check Gate ━━━"
append "Before any non-trivial speech or action, run the 5-axis check (one No -> pause, retrieve, verify):"
append "  Rule / Literal / Source / Frame / Character"
append "Situational routing: external content read -> Frame + Source. Asserting from internal memory -> Source. Applying a Li+ rule -> Rule + Literal."
append "Axis detail: rules/model/trigger-check-gate.md (always-on)."
append "━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Emit Codex JSON envelope.
if command -v jq >/dev/null 2>&1; then
  jq -n --arg ctx "$CONTEXT" '{
    "hookSpecificOutput": {
      "hookEventName": "UserPromptSubmit",
      "additionalContext": $ctx
    }
  }'
else
  # Manual JSON escape fallback (backslash, double-quote, newline, tab, CR).
  ESCAPED=$(printf '%s' "$CONTEXT" \
    | sed 's/\\/\\\\/g; s/"/\\"/g' \
    | awk 'BEGIN{ORS=""} {printf "%s\\n", $0}')
  printf '{"hookSpecificOutput":{"hookEventName":"UserPromptSubmit","additionalContext":"%s"}}\n' "$ESCAPED"
fi
