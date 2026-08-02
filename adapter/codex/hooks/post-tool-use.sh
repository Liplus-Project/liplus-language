#!/bin/bash
# Source: adapter/codex/hooks/post-tool-use.sh ({LI_PLUS_TAG})
# Codex PostToolUse hook (portable POSIX fallback).
# Port of adapter/claude/hooks/post-tool-use.sh; the Windows-native path is the
# sibling post-tool-use.ps1 (wired via hooks.json commandWindows).
#
# After adapter flattening (#1102) the only remaining injection is:
#   gh pr create  ->  auto-append missing sub-issue `Closes #NNN` to the PR body.
# rules/* are always-present (AGENTS.md core + SessionStart rules injection) and
# skills/* auto-invoke by description, so section-extraction injection is gone.
#
# Codex PostToolUse stdin payload mirrors Claude: tool_name, tool_input.command,
# tool_response.output (per #1502 "events mirror Claude"). If a future Codex
# build renames these fields, update the extraction below.
#
# JSON read/write uses Node.js (`node -e`), not an external `jq` binary. This is
# the #1540 fix, which landed on adapter/claude/hooks/post-tool-use.sh and was
# left behind here (#1632 F4): the standalone `jq` calls had no `command -v`
# guard and no fallback, so on a POSIX host without jq the tool name came back
# empty, the guard below rejected it, and the hook became a silent no-op — the
# sub-issue `Closes #NNN` append never fired and left no trace, since a
# successful hook run with empty output is not persisted to the transcript.
# The sibling post-tool-use.ps1 uses ConvertFrom-Json and never had the
# dependency, so the two Codex ports disagreed on whether a jq-less host works.
#
# node is a strictly better assumption than jq, but NOT a guaranteed one, so its
# absence is handled explicitly below rather than assumed away — otherwise this
# change would merely re-key the same silent failure from `jq` to `node`.
#
# NOTE: the `gh api --jq` calls further down use gh's BUILT-IN jq expression
# engine, which ships inside the gh binary. Those are not an external
# dependency and must not be rewritten.
export PATH="$HOME/.local/bin:$PATH"
INPUT=$(cat)

# Cheap pre-filter on the raw payload, so a Bash call whose payload never
# mentions the command does not spawn node at all. Mirrors the claude port,
# including its caveat: this matches raw bytes while the guards below match
# decoded JSON values, so a payload that unicode-escapes the spaces inside the
# command string would be dropped here. Sound for real traffic, not for
# arbitrary JSON.
case "$INPUT" in
  *"gh pr create"*|*"gh.exe pr create"*) ;;
  *) exit 0 ;;
esac

# node absence must stay observable. A static JSON literal is used because
# building it would otherwise require the very interpreter that is missing.
if ! command -v node >/dev/null 2>&1; then
  printf '%s' '{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"post-tool-use.sh: `node` not found on PATH, so this hook cannot run. If a PR was just created, its sub-issue `Closes #NNN` refs were not auto-appended — add them manually. See adapter/codex/hooks/post-tool-use.sh (#1632)."}}'
  exit 0
fi

# Extract a dot-path field from the hook payload held in $INPUT.
# Empty output means absent or unparsable; every caller treats that as "skip".
# Absence semantics match the `// empty` of the jq expressions this replaced:
# null, undefined and false all render as empty.
json_field() {
  printf '%s' "$INPUT" | node -e '
    let raw = "";
    // setEncoding is load-bearing: without it each Buffer chunk is decoded on
    // its own, so a multi-byte character straddling a chunk boundary (payloads
    // past the ~64KB stream highWaterMark, e.g. a long `tool_response.output`)
    // decodes into U+FFFD (#1544).
    process.stdin.setEncoding("utf8");
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

PROJECT_ROOT=$(json_field 'cwd')
[ -n "$PROJECT_ROOT" ] || PROJECT_ROOT="${CODEX_PROJECT_DIR:-$PWD}"
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
