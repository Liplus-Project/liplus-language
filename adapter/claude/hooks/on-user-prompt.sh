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

# --- Webhook notification re-arm ---
# The block carries two separable halves, and LI_PLUS_WEBHOOK_DELIVERY selects
# only the first: who calls the tool, never who handles what arrives.
#   call half     = "Run ... get_pending_status silently", emitted under poll
#                   (default / unset) alone. channel delivers events over the MCP
#                   channel and mcp_hook has a sibling type=mcp_tool entry invoke
#                   the tool directly, so both already replace this half; emitting
#                   it there is the double delivery described below.
#   handling half = the report filter and mark_processed. Nothing replaces it in
#                   any mode. Its firing moment is `each user turn start`
#                   (rules/operations/main-agent-procedures.md Foreground webhook
#                   notification intake), and a per-turn hook is the only surface
#                   that can fire a turn boundary - always-on residency is a load
#                   guarantee, not a firing one. Suppressing it alongside the call
#                   half is #1798: events arrived and no surface said what to do
#                   with them.
# The re-arm stays terse and points at the canonical instead of copying it, the
# same shape the Trigger Check Gate re-arm below uses.
#
# `tr -d '\r'` normalises a CRLF-saved Li+config.md, matching both codex ports
# (.sh does the same, .ps1 uses .Trim()). Without it the extracted value is
# `mcp_hook\r`, which fails the byte comparison below, so the reminder text is
# emitted every turn while the mcp_tool hook entry also fires — the double
# delivery hooks-settings.md's mcp_hook setting exists to prevent (#1632 F7).
# Latent rather than live: on a Windows/Git-Bash host both gawk and MSYS command
# substitution drop the CR on their own, so the miss needs a POSIX host.
WEBHOOK_DELIVERY=$(awk -F= '/^LI_PLUS_WEBHOOK_DELIVERY=/{print $2}' "$PROJECT_ROOT/Li+config.md" 2>/dev/null | tr -d '\r')
# Unknown-value surfacing (#1804). A value outside the known set is not a mode,
# and the comparison below silently treats it as poll. What is surfaced is the
# key name and the literal value, not a guess at what was meant: normalising
# `Mcp_Hook` would pass while `mcp-hook` still fell through, so naming the value
# is what closes the whole silent-fallback class rather than its mixed-case part.
# An empty value is not surfaced -- unset is the documented default (docs/B.-Configuration.md
# 未設定 / poll), and the default is the correct behaviour there.
case "$WEBHOOK_DELIVERY" in
  ""|poll|channel|mcp_hook) ;;
  *)
    echo ""
    echo "━━━ Li+config: unrecognized value ━━━"
    echo "LI_PLUS_WEBHOOK_DELIVERY=$WEBHOOK_DELIVERY is not one of: poll / channel / mcp_hook. Values are case-sensitive. Falling back to the default (poll)."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    ;;
esac

echo ""
echo "━━━ Webhook: check pending notifications ━━━"
if [ "$WEBHOOK_DELIVERY" != "channel" ] && [ "$WEBHOOK_DELIVERY" != "mcp_hook" ]; then
  echo "Run mcp__github-webhook-mcp__get_pending_status silently."
fi
echo "Report only foreground-relevant or notable items."
echo "mark_processed every consumed event; own-operation arrivals promptly."
echo "Intake detail: rules/operations/main-agent-procedures.md Foreground webhook notification intake; mark_processed mandate: rules/operations/operations.md Operations Rules (both always-on)."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# --- Trigger Check Gate re-arm (every turn) ---
echo ""
echo "━━━ Trigger Check Gate ━━━"
echo "Before any non-trivial speech or action, run the 5-axis check (one No -> pause, retrieve, verify):"
echo "  Rule / Literal / Source / Frame / Character"
echo "Situational routing: external content read -> Frame + Source. Asserting from internal memory -> Source. Applying a Li+ rule -> Rule + Literal."
echo "Axis detail: rules/model/trigger-check-gate.md (always-on)."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━"
