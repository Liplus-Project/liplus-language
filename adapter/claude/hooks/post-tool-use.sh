#!/bin/bash
# Source: adapter/claude/hooks/post-tool-use.sh ({LI_PLUS_TAG})
# Simplified post-tool-use hook: after adapter flattening (#1102),
# rules/* are always-loaded and skills/* auto-invoke by description match,
# so section-extraction injection is no longer needed.
# Retained: gh pr create → sub-issue refs auto-append to PR body.
export PATH="$HOME/.local/bin:$PATH"
INPUT=$(cat)
TOOL_NAME=$(printf '%s' "$INPUT" | jq -r '.tool_name // empty' 2>/dev/null)
COMMAND=$(printf '%s' "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null)

[[ "$TOOL_NAME" == "Bash" ]] || exit 0
[ -n "$COMMAND" ] || exit 0

CMD_LINE=$(printf '%s' "$COMMAND" | head -1 | sed 's/<<.*$//')

PROJECT_ROOT="${CLAUDE_PROJECT_DIR:-.}"
LIPLUS_DIR="$PROJECT_ROOT/liplus-language"

emit_context() {
  local context="$1"
  [ -n "$context" ] || exit 0
  jq -n --arg ctx "$context" '{
    "hookSpecificOutput": {
      "hookEventName": "PostToolUse",
      "additionalContext": $ctx
    }
  }'
}

repo_from_origin() {
  git -C "$LIPLUS_DIR" remote get-url origin 2>/dev/null \
    | grep -oE '[^/@:]+/[^/]+$' \
    | sed 's/\.git$//' 2>/dev/null || echo ""
}

# on_pr: gh pr create → sub-issue auto-append to PR body (only remaining injection)
if echo "$CMD_LINE" | grep -qE 'gh(\.exe)? pr create'; then
  OUTPUT=$(printf '%s' "$INPUT" | jq -r '.tool_response.output // empty' 2>/dev/null)
  PR_NUMBER=$(echo "$OUTPUT" | grep -oE '/pull/[0-9]+' | grep -oE '[0-9]+' | head -1)
  [ -n "$PR_NUMBER" ] || exit 0

  REPO=$(repo_from_origin)
  [ -n "$REPO" ] || exit 0

  PR_BODY=$(gh api "repos/$REPO/pulls/$PR_NUMBER" --jq '.body' 2>/dev/null || echo "")
  [ -n "$PR_BODY" ] || exit 0

  PARENT_ISSUE=$(echo "$PR_BODY" | grep -oE '#[0-9]+' | head -1 | tr -d '#')
  [ -n "$PARENT_ISSUE" ] || exit 0

  SUB_ISSUE_NUMBERS=$(gh api "repos/$REPO/issues/$PARENT_ISSUE/sub_issues" \
    --jq '.[].number' 2>/dev/null || echo "")
  [ -n "$SUB_ISSUE_NUMBERS" ] || exit 0

  MISSING=()
  while IFS= read -r issue_num; do
    [ -z "$issue_num" ] && continue
    if ! echo "$PR_BODY" | grep -qE "#${issue_num}([^0-9]|$)"; then
      MISSING+=("$issue_num")
    fi
  done <<< "$SUB_ISSUE_NUMBERS"

  [ ${#MISSING[@]} -gt 0 ] || exit 0

  ADDITIONS=""
  for num in "${MISSING[@]}"; do
    ADDITIONS="${ADDITIONS}
Closes #${num}"
  done

  NEW_BODY="${PR_BODY}${ADDITIONS}"
  gh api "repos/$REPO/pulls/$PR_NUMBER" \
    --method PATCH -f body="$NEW_BODY" > /dev/null 2>&1

  APPEND_MSG="━━━ PR #${PR_NUMBER}: sub-issue refs auto-appended ━━━"
  for num in "${MISSING[@]}"; do
    APPEND_MSG="${APPEND_MSG}
  + Closes #${num}"
  done
  APPEND_MSG="${APPEND_MSG}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

  emit_context "$APPEND_MSG"
  exit 0
fi

exit 0
