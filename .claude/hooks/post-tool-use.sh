#\!/bin/bash
# PostToolUse hook: GitHub notification polling
# Checks unread notifications after GitHub-related Bash commands

INPUT=$(cat)
TOOL_NAME=$(printf '%s' "$INPUT" | jq -r '.tool_name // empty' 2>/dev/null)
COMMAND=$(printf '%s' "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null)

# Only for Bash tool + GitHub-related commands
[[ "$TOOL_NAME" == "Bash" ]] || exit 0
echo "$COMMAND" | grep -qE '(git push|gh pr|gh issue|gh api|gh run)' || exit 0

# Fetch unread notifications
NOTIFICATIONS=$(gh api notifications 2>/dev/null) || exit 0
COUNT=$(printf '%s' "$NOTIFICATIONS" | jq 'length' 2>/dev/null) || exit 0

[[ "$COUNT" -gt 0 ]] || exit 0

echo ""
echo "━━━ GitHub通知 ${COUNT}件 ━━━"
printf '%s' "$NOTIFICATIONS" | jq -r '.[] | "[\(.reason)] \(.repository.name): \(.subject.title)"'
echo "━━━━━━━━━━━━━━━━━━━━━"

# Mark all as read
gh api notifications -X PUT >/dev/null 2>&1 || true
