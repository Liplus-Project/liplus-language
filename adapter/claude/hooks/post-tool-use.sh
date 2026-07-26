#!/bin/bash
# Source: adapter/claude/hooks/post-tool-use.sh ({LI_PLUS_TAG})
# Simplified post-tool-use hook: after adapter flattening (#1102),
# rules/* are always-loaded and skills/* auto-invoke by description match,
# so section-extraction injection is no longer needed.
# Retained: gh pr create → sub-issue refs auto-append to PR body.
#
# JSON read/write uses Node.js (`node -e`), not an external `jq` binary —
# this mirrors the #1519 fix applied to on-session-start.sh.
# Before #1540 this hook parsed stdin with a standalone `jq`; on any host
# without jq installed (not shipped by default on Windows, macOS, or most
# Linux distributions) the parse yielded an empty tool name, the guard below
# rejected it, and the hook became a silent no-op — no fallback, and no
# observable trace, since a successful hook run with empty output is not
# persisted to the transcript.
#
# node is a strictly better assumption than jq, but NOT a guaranteed one:
# Claude Code ships as a packaged executable and does not contract to place a
# `node` binary on a hook subprocess's PATH. So node absence is handled
# explicitly below rather than assumed away — otherwise this change would
# merely re-key the same silent failure from `jq` to `node`.
#
# NOTE: the `gh api --jq` calls further down use gh's BUILT-IN jq expression
# engine, which ships inside the gh binary. Those are not an external
# dependency and must not be rewritten.
export PATH="$HOME/.local/bin:$PATH"
INPUT=$(cat)

# Cheap pre-filter on the raw payload, so an unrelated Bash call does not spawn
# node at all. This matches raw bytes, whereas the guards below match decoded
# JSON values, so the two are not equivalent in general: a payload that
# unicode-escapes the spaces inside the command string still decodes to a
# matching command, yet has no literal match here and would be dropped. That
# input is not reachable from Claude Code, whose payload serializer never
# escapes printable ASCII — the filter is sound for real traffic, not for
# arbitrary JSON.
case "$INPUT" in
  *"gh pr create"*|*"gh.exe pr create"*) ;;
  *) exit 0 ;;
esac

# node absence must stay observable. A static JSON literal is used here because
# building it would otherwise require the very interpreter that is missing.
# Without node the payload cannot be parsed, so this branch cannot tell whether
# a PR was actually created — the pre-filter above only proves the raw text
# mentions the command. The message is therefore worded conditionally; asserting
# that refs were dropped would be false whenever the command merely named it.
if ! command -v node >/dev/null 2>&1; then
  printf '%s' '{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"post-tool-use.sh: `node` not found on PATH, so this hook cannot run. If a PR was just created, its sub-issue `Closes #NNN` refs were not auto-appended — add them manually. See adapter/claude/hooks/post-tool-use.sh (#1540)."}}'
  exit 0
fi

# Extract a dot-path field from the hook payload held in $INPUT.
# Empty output means absent or unparsable; every caller treats that as "skip".
# Absence semantics match the `// empty` of the jq expressions this replaced:
# null, undefined and false all render as empty. Objects and arrays render as
# compact JSON text rather than via JS string coercion (`jq -r` pretty-prints
# them instead, but no field this hook reads is ever a composite value).
json_field() {
  printf '%s' "$INPUT" | node -e '
    let raw = "";
    process.stdin.on("data", (d) => { raw += d; });
    process.stdin.on("end", () => {
      try {
        let v = JSON.parse(raw);
        for (const key of process.argv[1].split(".")) {
          v = (v === null || v === undefined) ? undefined : v[key];
        }
        if (v === null || v === undefined || v === false) {
          return;
        }
        process.stdout.write(typeof v === "object" ? JSON.stringify(v) : String(v));
      } catch (e) {
        // leave stdout empty; caller treats it as an absent field
      }
    });
  ' "$1" 2>/dev/null
}

TOOL_NAME=$(json_field 'tool_name')
COMMAND=$(json_field 'tool_input.command')

[[ "$TOOL_NAME" == "Bash" ]] || exit 0
[ -n "$COMMAND" ] || exit 0

CMD_LINE=$(printf '%s' "$COMMAND" | head -1 | sed 's/<<.*$//')

PROJECT_ROOT="${CLAUDE_PROJECT_DIR:-.}"
LIPLUS_DIR="$PROJECT_ROOT/liplus-language"

emit_context() {
  local context="$1"
  [ -n "$context" ] || exit 0
  # Indent 2 plus the trailing newline reproduce jq -n's default output byte for
  # byte, matching the sample in docs/6.-Adapter.md. JSON.stringify emits
  # neither on its own.
  node -e '
    process.stdout.write(JSON.stringify({
      hookSpecificOutput: {
        hookEventName: "PostToolUse",
        additionalContext: process.argv[1]
      }
    }, null, 2) + "\n");
  ' "$context"
}

repo_from_origin() {
  git -C "$LIPLUS_DIR" remote get-url origin 2>/dev/null \
    | grep -oE '[^/@:]+/[^/]+$' \
    | sed 's/\.git$//' 2>/dev/null || echo ""
}

# on_pr: gh pr create → sub-issue auto-append to PR body (only remaining injection)
if echo "$CMD_LINE" | grep -qE 'gh(\.exe)? pr create'; then
  OUTPUT=$(json_field 'tool_response.output')
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
