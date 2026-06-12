#!/bin/bash
# Source: adapter/claude/hooks/on-user-prompt.sh ({LI_PLUS_TAG})
# UserPromptSubmit hook: per-turn Trigger Check Gate re-arm + webhook check.
# The gate re-arm is the deterministic firing surface for
# rules/model/trigger-check-gate.md (replaces the retired state-declaration
# substrate; #1493 implements #1413 candidate A).
# Character_Instance is loaded via Claude Code output-styles (system prompt
# residency) and no longer re-notified per turn.
# Source of truth is this file; keep hooks-settings.md reference consistent.
export PATH="$HOME/.local/bin:$PATH"
PROJECT_ROOT="${CLAUDE_PROJECT_DIR:-.}"

# --- Webhook notification reminder ---
# Read LI_PLUS_WEBHOOK_DELIVERY from Li+config.md
#   poll (default / unset) = emit reminder text so Claude calls the MCP tool
#   channel                = MCP channel delivers events directly; skip reminder
#   mcp_hook               = a sibling type=mcp_tool hook entry invokes the MCP
#                            tool directly without going through Claude; skip reminder
WEBHOOK_DELIVERY=$(awk -F= '/^LI_PLUS_WEBHOOK_DELIVERY=/{print $2}' "$PROJECT_ROOT/Li+config.md" 2>/dev/null)
if [ "$WEBHOOK_DELIVERY" != "channel" ] && [ "$WEBHOOK_DELIVERY" != "mcp_hook" ]; then
  echo ""
  echo "━━━ Webhook: check pending notifications ━━━"
  echo "Run mcp__github-webhook-mcp__get_pending_status silently."
  echo "Report only foreground-relevant or notable items."
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
fi

# --- Trigger Check Gate re-arm (every turn) ---
echo ""
echo "━━━ Trigger Check Gate ━━━"
echo "Before any non-trivial speech or action, run the 5-axis check (one No -> pause, retrieve, verify):"
echo "  Rule / Literal / Source / Frame / Character"
echo "Situational routing: external content read -> Frame + Source. Asserting from internal memory -> Source. Applying a Li+ rule -> Rule + Literal."
echo "Axis detail: rules/model/trigger-check-gate.md (always-on)."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━"
