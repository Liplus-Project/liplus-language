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

if [ "$WEBHOOK_DELIVERY" != "channel" ] && [ "$WEBHOOK_DELIVERY" != "mcp_hook" ]; then
  append ""
  append "━━━ Webhook: check pending notifications ━━━"
  append "Run mcp__github-webhook-mcp__get_pending_status silently."
  append "Report only foreground-relevant or notable items."
  append "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
fi

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
