#!/bin/bash
# Source: adapter/claude/hooks/on-user-prompt.sh ({LI_PLUS_TAG})
# UserPromptSubmit hook: Character_Instance re-notify and webhook check.
# Source of truth is this file; keep hooks-settings.md reference consistent.
export PATH="$HOME/.local/bin:$PATH"
PROJECT_ROOT="${CLAUDE_PROJECT_DIR:-.}"
CLAUDE_MD="$PROJECT_ROOT/.claude/CLAUDE.md"

# --- Always Character Platform re-notify ---
CHARACTER_MD="$PROJECT_ROOT/.claude/rules/character_Instance.md"
if [ -f "$CHARACTER_MD" ]; then
  awk '/^---$/{n++; next} n>=2' "$CHARACTER_MD"
elif [ -f "$CLAUDE_MD" ]; then
  sed -n '/\[Character_Instance\]/{n;n;n;:a;/^#######/q;p;n;ba}' "$CLAUDE_MD"
fi

# --- Webhook notification reminder ---
# Read LI_PLUS_WEBHOOK_DELIVERY from Li+config.md (channel = skip polling reminder)
WEBHOOK_DELIVERY=$(awk -F= '/^LI_PLUS_WEBHOOK_DELIVERY=/{print $2}' "$PROJECT_ROOT/Li+config.md" 2>/dev/null)
if [ "$WEBHOOK_DELIVERY" != "channel" ]; then
  echo ""
  echo "━━━ Webhook: check pending notifications ━━━"
  echo "Run mcp__github-webhook-mcp__get_pending_status silently."
  echo "Report only foreground-relevant or notable items."
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
fi
