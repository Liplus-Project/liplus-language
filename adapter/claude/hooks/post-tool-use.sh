#!/bin/bash
# Source: adapter/claude/hooks/post-tool-use.sh ({LI_PLUS_TAG})
# Simplified post-tool-use hook: after adapter flattening (#1102),
# rules/* are always-loaded and skills/* auto-invoke by description match,
# so section-extraction injection is no longer needed.
# Retained: gh pr create → sub-issue refs auto-append to PR body.
# Added (#2047): Write / Edit / MultiEdit → stray-script scan of the written file.
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

# Cheap pre-filter on the raw payload, so a Bash call whose payload never
# mentions the command does not spawn node at all. (A payload that merely names
# it in passing — command output quoting it, say — still spawns node and is
# rejected by the parsed guards below.)
# This matches raw bytes, whereas the guards below match decoded
# JSON values, so the two are not equivalent in general: a payload that
# unicode-escapes the spaces inside the command string still decodes to a
# matching command, yet has no literal match here and would be dropped. The
# filter therefore rests on an assumption Li+ cannot verify from its own source:
# that Claude Code's payload serializer does not escape printable ASCII. Sound
# for real traffic on that assumption, not for arbitrary JSON.
#
# The Write / Edit / MultiEdit arms admit the file-writing tools to the
# stray-script scan below (#2047). A Bash payload that merely carries one of
# those quoted names spawns node and is rejected by the parsed guards.
case "$INPUT" in
  *"gh pr create"*|*"gh.exe pr create"*) ;;
  *'"Write"'*|*'"Edit"'*|*'"MultiEdit"'*) ;;
  *) exit 0 ;;
esac

# node absence must stay observable. A static JSON literal is used here because
# building it would otherwise require the very interpreter that is missing.
# Without node the payload cannot be parsed, so this branch cannot tell whether
# a PR was actually created — the pre-filter above only proves the raw text
# mentions the command. The message is therefore worded conditionally; asserting
# that refs were dropped would be false whenever the command merely named it.
if ! command -v node >/dev/null 2>&1; then
  case "$INPUT" in
    *"gh pr create"*|*"gh.exe pr create"*)
      printf '%s' '{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"post-tool-use.sh: `node` not found on PATH, so this hook cannot run. If a PR was just created, its sub-issue `Closes #NNN` refs were not auto-appended — add them manually. See adapter/claude/hooks/post-tool-use.sh."}}'
      ;;
    *)
      printf '%s' '{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"post-tool-use.sh: `node` not found on PATH, so this hook cannot run. If a file was just written by Write / Edit / MultiEdit, it was not scanned for stray-script characters. See adapter/claude/hooks/post-tool-use.sh."}}'
      ;;
  esac
  exit 0
fi

# Extract a dot-path field from the hook payload held in $INPUT.
# Empty output means absent or unparsable; every caller treats that as "skip".
# A second argument `string` narrows the read to a string value: any other type
# renders as empty, so a field of the wrong shape reads as absent rather than
# as its JSON text.
# Absence semantics match the `// empty` of the jq expressions this replaced:
# null, undefined and false all render as empty. Objects and arrays render as
# compact JSON text rather than via JS string coercion (`jq -r` pretty-prints
# them instead). That divergence is unreachable as long as the three fields read
# here stay string-typed — another assumption about Claude Code's payload shape
# that Li+ cannot verify from its own source.
json_field() {
  printf '%s' "$INPUT" | node -e '
    let raw = "";
    // setEncoding is load-bearing: without it each Buffer chunk is decoded on
    // its own, so a multi-byte character straddling a chunk boundary (payloads
    // past the ~64KB stream highWaterMark, e.g. a long `tool_response.stdout`)
    // decodes into U+FFFD. Reproduced at 3 replacement chars in a 192KB
    // Japanese payload before this line was added.
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
        if (process.argv[2] === "string" && typeof v !== "string") {
          return;
        }
        process.stdout.write(typeof v === "object" ? JSON.stringify(v) : String(v));
      } catch (e) {
        // leave stdout empty; caller treats it as an absent field
      }
    });
  ' "$1" "$2" 2>/dev/null
}

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

# Stray-script scan (#2047). Prints the report text for one written file, or
# nothing. Reports every run of Cyrillic, Hangul, Arabic, Hebrew, Thai,
# Devanagari, Armenian or Georgian letters whose preceding or following
# character is a Latin letter, kana, kanji or the prolonged sound mark (U+30FC,
# U+FF70), with file, line number and the run bracketed in its surrounding text.
# A run bounded on both sides by whitespace, punctuation or line ends is not
# reported. Skips a path that is not a regular file, a file over 1 MiB, and a
# file holding a NUL byte. Reads only: never rewrites the file.
scan_stray_script() {
  node -e '
    const fs = require("fs");
    const file = process.argv[1];
    const SIZE_LIMIT = 1024 * 1024;
    const MAX_REPORTED = 20;
    const CONTEXT = 8;
    const SCRIPTS = [
      ["Cyrillic", /\p{sc=Cyrillic}/u],
      ["Hangul", /\p{sc=Hangul}/u],
      ["Arabic", /\p{sc=Arabic}/u],
      ["Hebrew", /\p{sc=Hebrew}/u],
      ["Thai", /\p{sc=Thai}/u],
      ["Devanagari", /\p{sc=Devanagari}/u],
      ["Armenian", /\p{sc=Armenian}/u],
      ["Georgian", /\p{sc=Georgian}/u],
    ];
    const STRAY = /[\p{sc=Cyrillic}\p{sc=Hangul}\p{sc=Arabic}\p{sc=Hebrew}\p{sc=Thai}\p{sc=Devanagari}\p{sc=Armenian}\p{sc=Georgian}]+/gu;
    const NEIGHBOUR = /^[\p{sc=Latin}\p{sc=Hiragana}\p{sc=Katakana}\p{sc=Han}ーｰ]$/u;
    function main() {
      let buf;
      try {
        const st = fs.statSync(file);
        if (!st.isFile() || st.size > SIZE_LIMIT) return "";
        buf = fs.readFileSync(file);
      } catch (e) {
        return "";
      }
      if (buf.includes(0)) return "";
      const reported = [];
      let total = 0;
      buf.toString("utf8").split("\n").forEach((raw, i) => {
        const line = raw.endsWith("\r") ? raw.slice(0, -1) : raw;
        for (const m of line.matchAll(STRAY)) {
          const end = m.index + m[0].length;
          const before = Array.from(line.slice(Math.max(0, m.index - 4 * CONTEXT), m.index));
          const after = Array.from(line.slice(end, end + 4 * CONTEXT));
          const prev = before.length ? before[before.length - 1] : "";
          const next = after.length ? after[0] : "";
          if (!NEIGHBOUR.test(prev) && !NEIGHBOUR.test(next)) continue;
          total += 1;
          if (reported.length >= MAX_REPORTED) continue;
          const found = SCRIPTS.find(([, re]) => re.test(m[0]));
          const script = found ? found[0] : "non-Latin";
          reported.push(`  line ${i + 1} (${script}): ${before.slice(-CONTEXT).join("")}[${m[0]}]${after.slice(0, CONTEXT).join("")}`);
        }
      });
      if (total === 0) return "";
      const lines = [
        `post-tool-use: stray-script check: ${total} run(s) of non-Latin, non-Japanese letters touch a Latin letter, kana or kanji with no whitespace between, in ${file}. The file was not changed; fix any run that was not meant to be there.`,
        ...reported,
      ];
      if (total > reported.length) lines.push(`  ... and ${total - reported.length} more`);
      return lines.join("\n");
    }
    process.stdout.write(main());
  ' "$1" 2>/dev/null
}

TOOL_NAME=$(json_field 'tool_name')

# Write / Edit / MultiEdit: scan the written file, then stop. Case-sensitive,
# like the Bash guard below.
case "$TOOL_NAME" in
  Write|Edit|MultiEdit)
    FILE_PATH=$(json_field 'tool_input.file_path' string)
    [ -n "$FILE_PATH" ] || exit 0
    emit_context "$(scan_stray_script "$FILE_PATH")"
    exit 0
    ;;
esac

COMMAND=$(json_field 'tool_input.command')

[[ "$TOOL_NAME" == "Bash" ]] || exit 0
[ -n "$COMMAND" ] || exit 0

CMD_LINE=$(printf '%s' "$COMMAND" | head -1 | sed 's/<<.*$//')

PROJECT_ROOT="${CLAUDE_PROJECT_DIR:-.}"
LIPLUS_DIR="$PROJECT_ROOT/liplus-language"

repo_from_origin() {
  git -C "$LIPLUS_DIR" remote get-url origin 2>/dev/null \
    | grep -oE '[^/@:]+/[^/]+$' \
    | sed 's/\.git$//' 2>/dev/null || echo ""
}

# Firing trace (#1710). Once the command has matched `gh pr create`, every exit
# below emits exactly one line naming how the run ended; calls that never
# matched stay silent. Emit it only as `hookSpecificOutput.additionalContext`
# on exit 0, not on plain stdout, stderr or exit 2. docs/6.-Adapter.md
# post-tool-use.sh holds the per-line table and the channel evidence.
emit_trace() {
  emit_context "post-tool-use: $1"
  exit 0
}

# on_pr: gh pr create → sub-issue auto-append to PR body (only remaining injection)
if echo "$CMD_LINE" | grep -qE 'gh(\.exe)? pr create'; then
  # Claude Code's Bash tool_response is an object carrying `stdout`, `stderr`,
  # `interrupted` and `isImage`, with no `output` field: the hooks reference
  # gives that shape for a PostToolUse `updatedToolOutput` replacing a Bash
  # result, and transcripts record the same object as `toolUseResult`.
  # `gh pr create` prints the PR URL on stdout. The Codex ports read a
  # different shape (#2060).
  OUTPUT=$(json_field 'tool_response.stdout' string)
  [ -n "$OUTPUT" ] || emit_trace "gh pr create matched, but tool_response.stdout is absent, empty or not a string; no sub-issue refs appended."
  PR_NUMBER=$(echo "$OUTPUT" | grep -oE '/pull/[0-9]+' | grep -oE '[0-9]+' | head -1)
  [ -n "$PR_NUMBER" ] || emit_trace "gh pr create matched, but tool_response.stdout carries no /pull/<number> URL; no sub-issue refs appended."

  REPO=$(repo_from_origin)
  # No clone to ask (api mode, #2031): read the repository out of the PR URL
  # `gh pr create` printed.
  [ -n "$REPO" ] || REPO=$(echo "$OUTPUT" | grep -oE '[^/[:space:]]+/[^/[:space:]]+/pull/[0-9]+' | head -1 | sed 's#/pull/[0-9]*$##')
  [ -n "$REPO" ] || emit_trace "PR #${PR_NUMBER}: repository could not be resolved; no sub-issue refs appended."

  PR_BODY=$(gh api "repos/$REPO/pulls/$PR_NUMBER" --jq '.body' 2>/dev/null || echo "")
  [ -n "$PR_BODY" ] || emit_trace "PR #${PR_NUMBER}: body could not be read or is empty; no sub-issue refs appended."

  # Parent = the first `#<n>` that directly follows a GitHub closing keyword
  # (close / closes / closed / fix / fixes / fixed / resolve / resolves /
  # resolved, any case, optionally followed by a colon). A bare `#<n>` with no
  # keyword before it is never taken as the parent.
  PARENT_ISSUE=$(echo "$PR_BODY" \
    | grep -oiE '(^|[^A-Za-z0-9_])(close[sd]?|fix(e[sd])?|resolve[sd]?):?[[:blank:]]+#[0-9]+' \
    | head -1 | grep -oE '[0-9]+$')
  [ -n "$PARENT_ISSUE" ] || emit_trace "PR #${PR_NUMBER}: body carries no closing #<issue> reference; no sub-issue refs appended."

  SUB_ISSUE_NUMBERS=$(gh api "repos/$REPO/issues/$PARENT_ISSUE/sub_issues" \
    --jq '.[].number' 2>/dev/null || echo "")
  [ -n "$SUB_ISSUE_NUMBERS" ] || emit_trace "PR #${PR_NUMBER}: parent #${PARENT_ISSUE} has no sub-issues, or they could not be read; nothing to append."

  MISSING=()
  while IFS= read -r issue_num; do
    [ -z "$issue_num" ] && continue
    if ! echo "$PR_BODY" | grep -qE "#${issue_num}([^0-9]|$)"; then
      MISSING+=("$issue_num")
    fi
  done <<< "$SUB_ISSUE_NUMBERS"

  [ ${#MISSING[@]} -gt 0 ] || emit_trace "PR #${PR_NUMBER}: every sub-issue of parent #${PARENT_ISSUE} is already referenced; nothing to append."

  ADDITIONS=""
  REFS=""
  for num in "${MISSING[@]}"; do
    ADDITIONS="${ADDITIONS}
Closes #${num}"
    REFS="${REFS:+${REFS}, }Closes #${num}"
  done

  NEW_BODY="${PR_BODY}${ADDITIONS}"
  # The exit status decides which line is emitted: an append is reported only
  # when the PATCH itself succeeded.
  if gh api "repos/$REPO/pulls/$PR_NUMBER" \
    --method PATCH -f body="$NEW_BODY" > /dev/null 2>&1; then
    emit_trace "PR #${PR_NUMBER}: sub-issue refs auto-appended (parent #${PARENT_ISSUE}): ${REFS}."
  fi
  emit_trace "PR #${PR_NUMBER}: PATCH of the body failed; sub-issue refs NOT appended (parent #${PARENT_ISSUE}): ${REFS}."
fi

exit 0
