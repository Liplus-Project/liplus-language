#!/bin/bash
# Source: adapter/codex/hooks/on-session-start.sh ({LI_PLUS_TAG})
# Codex SessionStart hook (portable POSIX fallback). The Windows-native PRIMARY
# path is the sibling on-session-start.ps1 (wired via hooks.json commandWindows).
# Port of adapter/claude/hooks/on-session-start.sh.
#
# Three responsibilities (the first is Codex-specific):
#   1. RULES INJECTION (Codex-only): read rules/*.md from the LI_PLUS_REPO clone
#      and emit them as additionalContext (Codex has no .claude/rules/ always-on
#      folder). #1502 verified design.
#   2. Update-status verification (sentinel tag / config schema / language
#      contract) -> LI_PLUS_UPDATE_STATUS marker.
#   3. Cold-start material gathering with diff-only emission.
#
# Codex contract difference vs Claude: SessionStart context injection requires
# JSON on stdout (hookSpecificOutput.additionalContext). So this port accumulates
# the WHOLE emission into $BUFFER and wraps it once at the end.
#
# Matchers: startup / resume / clear / compact. resume/clear/compact = rules
# re-injection + cold-start anchor only (no diff eval, no update-status re-check).
#
# JSON handling (output wrapping, HOOK_INPUT field extraction, cold-start
# diff-only state read/write) uses Node.js (`node -e`), not an external `jq`
# binary — node is a runtime dependency Codex CLI (like Claude Code) already
# has, so it is a safe assumption. Ported from adapter/claude/hooks/on-session-start.sh
# (#1519); on-session-start.ps1 (Windows-native primary) never depended on jq
# in the first place (PowerShell-native ConvertFrom-Json/ConvertTo-Json). #1526.
export PATH="$HOME/.local/bin:$PATH"

BUFFER=""
emit() { BUFFER="${BUFFER}$1
"; }
emit_section() {
  local banner="$1" body="$2"
  [ -n "$body" ] || return 0
  emit "━━━ $banner ━━━"
  emit "$body"
  emit "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  emit ""
}
flush_json() {
  if command -v node >/dev/null 2>&1; then
    BUFFER="$BUFFER" node -e '
      process.stdout.write(JSON.stringify({
        hookSpecificOutput: { hookEventName: "SessionStart", additionalContext: process.env.BUFFER || "" }
      }) + "\n");
    ' 2>/dev/null && return
  fi
  local esc
  esc=$(printf '%s' "$BUFFER" | sed 's/\\/\\\\/g; s/"/\\"/g' | awk 'BEGIN{ORS=""} {printf "%s\\n", $0}')
  printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"%s"}}\n' "$esc"
}
sha256_of() {
  local input="$1"
  if command -v sha256sum >/dev/null 2>&1; then
    printf '%s' "$input" | sha256sum | awk '{print $1}'
  elif command -v shasum >/dev/null 2>&1; then
    printf '%s' "$input" | shasum -a 256 | awk '{print $1}'
  else
    printf ''
  fi
}

# --- stdin / paths ---
HOOK_INPUT=""
if [ ! -t 0 ]; then HOOK_INPUT=$(cat 2>/dev/null || true); fi
PROJECT_ROOT=""
if [ -n "$HOOK_INPUT" ] && command -v node >/dev/null 2>&1; then
  PROJECT_ROOT=$(printf '%s' "$HOOK_INPUT" | node -e '
    let raw = "";
    // Without setEncoding each Buffer chunk is decoded on its own, so a
    // multi-byte character straddling a chunk boundary becomes U+FFFD (#1544).
    process.stdin.setEncoding("utf8");
    process.stdin.on("data", (d) => { raw += d; });
    process.stdin.on("end", () => {
      try {
        const payload = JSON.parse(raw);
        process.stdout.write(String(payload.cwd || ""));
      } catch (e) {
        // leave stdout empty; caller falls back to CODEX_PROJECT_DIR/PWD
      }
    });
  ' 2>/dev/null)
fi
[ -n "$PROJECT_ROOT" ] || PROJECT_ROOT="${CODEX_PROJECT_DIR:-$PWD}"

LIPLUS_DIR="$PROJECT_ROOT/liplus-language"
COLDSTART_MD="$LIPLUS_DIR/rules/evolution/cold-start-synthesis.md"
DECISION_STRUCTURE="$LIPLUS_DIR/docs/Decision-Structure.md"
STATE_DIR="$PROJECT_ROOT/.codex/state"
STATE_FILE="$STATE_DIR/last-cold-start-emit.json"
ADAPTER_FILE="$PROJECT_ROOT/AGENTS.md"
CONFIG_FILE="$PROJECT_ROOT/Li+config.md"
RULES_ROOT="$LIPLUS_DIR/rules"

# --- matcher resolution ---
MATCHER="startup"
if [ -n "$HOOK_INPUT" ]; then
  EXTRACTED=""
  if command -v node >/dev/null 2>&1; then
    EXTRACTED=$(printf '%s' "$HOOK_INPUT" | node -e '
      let raw = "";
      // Without setEncoding each Buffer chunk is decoded on its own, so a
      // multi-byte character straddling a chunk boundary becomes U+FFFD (#1544).
      process.stdin.setEncoding("utf8");
      process.stdin.on("data", (d) => { raw += d; });
      process.stdin.on("end", () => {
        try {
          const payload = JSON.parse(raw);
          const v = payload.matcher || payload.source || payload.session_source || "";
          process.stdout.write(String(v));
        } catch (e) {
          // leave stdout empty; caller falls back to regex extraction
        }
      });
    ' 2>/dev/null)
  fi
  if [ -z "$EXTRACTED" ]; then
    EXTRACTED=$(printf '%s' "$HOOK_INPUT" | sed -n 's/.*"\(matcher\|source\)"[[:space:]]*:[[:space:]]*"\([a-z]*\)".*/\2/p' | head -n 1)
  fi
  case "$EXTRACTED" in
    startup|resume|clear|compact) MATCHER="$EXTRACTED" ;;
  esac
fi

# --- guard: liplus source not resolved yet ---
if [ ! -d "$LIPLUS_DIR" ]; then
  emit "━━━ Li+ update status ━━━"
  emit "LI_PLUS_UPDATE_STATUS=needed reason=liplus-source-unresolved"
  emit "liplus-language clone not found under workspace root. Run the Li+config / Li+update walkthrough."
  emit "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  flush_json
  exit 0
fi

# ===================================================================
# RULES INJECTION (Codex-only; substitute for Claude .claude/rules/)
# Runs on EVERY matcher (Codex has no folder-level persistence).
# ===================================================================
if [ -d "$RULES_ROOT" ]; then
  RULE_FILES=$(cd "$LIPLUS_DIR" && find rules -type f -name '*.md' 2>/dev/null | sort)
  if [ -n "$RULE_FILES" ]; then
    emit "━━━ Li+ rules (always-on; injected because Codex has no .claude/rules equivalent) ━━━"
    while IFS= read -r rel; do
      [ -n "$rel" ] || continue
      emit "----- $rel -----"
      emit "$(cat "$LIPLUS_DIR/$rel" 2>/dev/null)"
      emit ""
    done <<< "$RULE_FILES"
    emit "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    emit ""
  fi
fi

# ===================================================================
# Language contract values (every matcher)
# ===================================================================
# Issue #1575. Extracted here rather than inside the startup-only block below
# because the values must be in context on every session entry point, the same
# way the always-on rules above are re-injected on every matcher. The
# startup-only axis 3 check reuses what this block resolved.
BASE_LANG=""; PROJ_LANG=""
if [ -f "$CONFIG_FILE" ]; then
  BASE_LANG=$(sed -n 's/^[[:space:]]*LI_PLUS_BASE_LANGUAGE[[:space:]]*=[[:space:]]*\(.*\)$/\1/p' "$CONFIG_FILE" | head -n 1 | tr -d '\r' | sed 's/[[:space:]]*$//')
  PROJ_LANG=$(sed -n 's/^[[:space:]]*LI_PLUS_PROJECT_LANGUAGE[[:space:]]*=[[:space:]]*\(.*\)$/\1/p' "$CONFIG_FILE" | head -n 1 | tr -d '\r' | sed 's/[[:space:]]*$//')
fi

# ===================================================================
# Update sentinel-skip verification (startup only)
# ===================================================================
if [ "$MATCHER" = "startup" ]; then
  UPDATE_REASONS=()

  # axis 1: adapter sentinel tag vs target tag
  ADAPTER_TAG=""
  if [ -f "$ADAPTER_FILE" ]; then
    ADAPTER_TAG=$(sed -n 's/^# --- Li+ BEGIN (\([^)]*\)) ---.*/\1/p' "$ADAPTER_FILE" | head -n 1)
  fi
  LI_PLUS_CHANNEL_VAL=""
  if [ -f "$CONFIG_FILE" ]; then
    LI_PLUS_CHANNEL_VAL=$(sed -n 's/^[[:space:]]*LI_PLUS_CHANNEL[[:space:]]*=[[:space:]]*\(.*\)$/\1/p' "$CONFIG_FILE" | head -n 1 | tr -d '\r')
  fi
  [ -n "$LI_PLUS_CHANNEL_VAL" ] || LI_PLUS_CHANNEL_VAL="release"
  TARGET_TAG=""
  case "$LI_PLUS_CHANNEL_VAL" in
    latest)  TARGET_TAG=$(gh release view --repo Liplus-Project/liplus-language --json tagName --jq '.tagName' 2>/dev/null) ;;
    release) TARGET_TAG=$(gh release list --repo Liplus-Project/liplus-language --limit 1 --json tagName --jq '.[0].tagName' 2>/dev/null) ;;
    tag)
      TARGET_TAG=$(git -C "$LIPLUS_DIR" ls-remote --tags --sort=-creatordate origin 2>/dev/null \
        | awk -F'refs/tags/' 'NF==2 {print $2}' | sed 's/\^{}$//' | head -n 1) ;;
  esac
  if [ -z "$ADAPTER_TAG" ] || [ -z "$TARGET_TAG" ] || [ "$ADAPTER_TAG" != "$TARGET_TAG" ]; then
    UPDATE_REASONS+=("sentinel-tag(adapter=${ADAPTER_TAG:-unknown},target=${TARGET_TAG:-unknown})")
  fi

  # axis 2: config schema canonical
  LEGACY_HIT=""
  if [ -f "$CONFIG_FILE" ]; then
    LEGACY_HIT=$(grep -E '^[[:space:]]*(LI_PLUS_REPOSITORY|USER_REPOSITORY|USER_REPOSITORY_EXECUTION_MODE)[[:space:]]*=|^[[:space:]]*[^#[:space:]][^=]*_EXECUTION_MODE[[:space:]]*=' "$CONFIG_FILE" 2>/dev/null | head -n 3)
  fi
  [ -n "$LEGACY_HIT" ] && UPDATE_REASONS+=("legacy-schema-keys-present")

  # axis 3: language contract resolved (values extracted above, every matcher)
  if [ -z "$BASE_LANG" ] || [ -z "$PROJ_LANG" ]; then
    UPDATE_REASONS+=("language-contract-unresolved(base=${BASE_LANG:-unset},project=${PROJ_LANG:-unset})")
  fi

  if [ "${#UPDATE_REASONS[@]}" -eq 0 ]; then
    emit "━━━ Li+ update status ━━━"
    emit "LI_PLUS_UPDATE_STATUS=unnecessary tag=$TARGET_TAG channel=$LI_PLUS_CHANNEL_VAL"
    emit "Sentinel-skip applies: AI skips Li+update.md re-execution this session. Li+config.md spot read (Read for value lookup, do not execute contents) is permitted."
    emit "Override: Master input containing \"Li+configを実行\" / \"Li+config を実行\" forces the full walkthrough."
    emit "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    emit ""
  else
    REASON_STR=$(printf '%s,' "${UPDATE_REASONS[@]}"); REASON_STR="${REASON_STR%,}"
    emit "━━━ Li+ update status ━━━"
    emit "LI_PLUS_UPDATE_STATUS=needed reason=$REASON_STR"
    emit "AI must read Li+config.md and execute Li+update.md walkthrough this session."
    emit "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    emit ""
  fi
fi

# --- emit language contract values (every matcher) ---
# Issue #1575: the contract text is always in context (adapter AGENTS.md) but
# its values were not, because resolving them was written as "read
# Li+config.md" and that file is not auto-loaded. Emitting the values the hook
# already holds removes the read step without baking anything into a generated
# file. Emitted on every path that reaches here, with an unresolved value
# rendered as "unset", so inside a bootstrapped session the block's absence
# never has to be distinguished from an unresolved value. The unresolved-source
# guard exits well before this point and emits no language marker at all; the
# adapter Workspace_Language_Contract routes that state to the same ask-human
# branch as "unset".
emit "━━━ Li+ language contract ━━━"
emit "LI_PLUS_BASE_LANGUAGE=${BASE_LANG:-unset}"
emit "LI_PLUS_PROJECT_LANGUAGE=${PROJ_LANG:-unset}"
emit "Resolved from Li+config.md at session start. Definitions, scope and precedence: Workspace_Language_Contract (adapter AGENTS.md)."
emit "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
emit ""

# ===================================================================
# Cold-start material gathering
# ===================================================================
COLDSTART_LITERAL=""
if [ -f "$COLDSTART_MD" ]; then
  COLDSTART_LITERAL=$(awk '/^---$/{n++; next} n>=2' "$COLDSTART_MD" | sed '1{/^# /d;}' | sed '/./,$!d')
fi
emit_section "Cold-start Synthesis (rules/evolution/cold-start-synthesis.md literal)" "$COLDSTART_LITERAL"

if [ "$MATCHER" != "startup" ]; then
  emit "━━━ Cold-start Synthesis: instruction ━━━"
  emit "Matcher = ${MATCHER}. Session is continuous (resume/clear/compact). Rules were"
  emit "reinjected and the cold-start rule literal re-anchored above. Treat the prior"
  emit "session's in-context state as authoritative; do not re-orient from scratch."
  emit "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  flush_json
  exit 0
fi

# --- register diff-only sections ---
SECTION_KEYS=(); SECTION_BANNERS=(); SECTION_BODIES=()
register_section() { SECTION_KEYS+=("$1"); SECTION_BANNERS+=("$2"); SECTION_BODIES+=("$3"); }

DECISION_HEAD=""
[ -f "$DECISION_STRUCTURE" ] && DECISION_HEAD=$(head -n 20 "$DECISION_STRUCTURE")
register_section "decision_structure_head" "Decision structure index (docs/Decision-Structure.md head)" "$DECISION_HEAD"

RULES_TREE=""
[ -d "$RULES_ROOT" ] && RULES_TREE=$(cd "$LIPLUS_DIR" && find rules -type f -name '*.md' 2>/dev/null | sort)
register_section "rules_tree" "Rules tree (fetch address table for rules/ cache)" "$RULES_TREE"

LATEST_RELEASE=$(gh release list -R Liplus-Project/liplus-language --limit 3 2>/dev/null | head -n 3)
register_section "recent_releases" "Recent releases (includes prereleases)" "$LATEST_RELEASE"

OPEN_ISSUES=$(gh issue list -R Liplus-Project/liplus-language --state open --label in-progress --limit 5 \
  --json number,title,labels \
  --jq '.[] | "#\(.number) \(.title) [\(.labels | map(.name) | join(","))]"' 2>/dev/null)
register_section "open_in_progress_issues" "Open in-progress issues (max 5)" "$OPEN_ISSUES"

# Self-eval head: Codex has no ~/.claude/projects memory; use workspace-local memory/.
SELFEVAL_FOUND=""
for candidate in "$PROJECT_ROOT/memory/self-evaluation_log.md" "$LIPLUS_DIR/memory/self-evaluation_log.md"; do
  [ -f "$candidate" ] && { SELFEVAL_FOUND="$candidate"; break; }
done
SELFEVAL_HEAD=""
[ -n "$SELFEVAL_FOUND" ] && [ -f "$SELFEVAL_FOUND" ] && SELFEVAL_HEAD=$(head -n 15 "$SELFEVAL_FOUND")
register_section "self_eval_head" "Self-evaluation log head (most recent)" "$SELFEVAL_HEAD"

# promotion candidates
THRESHOLD_N=2
# A candidate qualifies as MEMORY_DIR only when it holds at least one file that
# some MEMORY_DIR consumer reads. Directory existence alone is not the criterion:
# an empty higher-precedence directory would otherwise shadow a populated
# lower-precedence one and silence every consumer at once.
# The marker set is the files MEMORY_DIR consumers read (feedback / project
# detectors, self-evolution observation surface), plus self-evaluation_log.md so
# that both resolution paths agree on what counts as a memory directory. That
# added member never decides a case in practice: the self-eval lookup above
# scans the same candidate directories, so whenever that file exists the primary
# path has already claimed the directory before this check runs.
memory_dir_populated() {
  for markerfile in \
    self-evaluation_log.md \
    feedback.md \
    project.md \
    self-evolution-observation.md; do
    [ -f "$1/$markerfile" ] && return 0
  done
  return 1
}

# Probe the directory directly when self-evaluation_log.md is absent: the other
# MEMORY_DIR readers (feedback/project detectors, self-evolution observation
# surface) must not be silenced by the absence of an unrelated file.
MEMORY_DIR=""
if [ -n "$SELFEVAL_FOUND" ]; then
  MEMORY_DIR=$(dirname "$SELFEVAL_FOUND")
else
  for memcandidate in "$PROJECT_ROOT/memory" "$LIPLUS_DIR/memory"; do
    memory_dir_populated "$memcandidate" && { MEMORY_DIR="$memcandidate"; break; }
  done
fi
PROMOTION_BODY=""

if [ -n "$SELFEVAL_FOUND" ] && [ -f "$SELFEVAL_FOUND" ]; then
  PAIR_DUPES=$(awk -v n="$THRESHOLD_N" '
    /^[[:space:]]*root_cause:[[:space:]]*/ { sub(/^[[:space:]]*root_cause:[[:space:]]*/, ""); rc=$0; next }
    /^[[:space:]]*tags:[[:space:]]*/ && rc != "" {
      sub(/^[[:space:]]*tags:[[:space:]]*/, ""); split($0, t, /,[[:space:]]*/); tag=t[1]
      gsub(/[[:space:]]+$/, "", tag)
      if (tag != "") { key=rc "|" tag; count[key]++ }
      rc=""
    }
    END { for (k in count) if (count[k] >= n) { split(k, p, "|"); printf "  - (%s, %s) x%d\n", p[1], p[2], count[k] } }
  ' "$SELFEVAL_FOUND")
  [ -n "$PAIR_DUPES" ] && PROMOTION_BODY="${PROMOTION_BODY}repeated (root_cause, domain-tag) pairs:
${PAIR_DUPES}
"
fi

if [ -n "$MEMORY_DIR" ] && [ -d "$MEMORY_DIR" ]; then
  RECENT_SECTIONS=""
  for memfile in "$MEMORY_DIR/feedback.md" "$MEMORY_DIR/project.md"; do
    [ -f "$memfile" ] || continue
    if find "$memfile" -mtime -7 -print 2>/dev/null | grep -q .; then
      SECTIONS=$(grep -E '^## ' "$memfile" 2>/dev/null | sed 's/^## /  - /')
      SEC_COUNT=$(printf '%s\n' "$SECTIONS" | grep -c '^  - ' 2>/dev/null)
      if [ "${SEC_COUNT:-0}" -ge "$THRESHOLD_N" ]; then
        RECENT_SECTIONS="${RECENT_SECTIONS}$(basename "$memfile") (modified within 7d, ${SEC_COUNT} sections):
${SECTIONS}
"
      fi
    fi
  done
  [ -n "$RECENT_SECTIONS" ] && PROMOTION_BODY="${PROMOTION_BODY}recent memory additions (<= 7d):
${RECENT_SECTIONS}"
fi

if [ -n "$MEMORY_DIR" ] && [ -d "$MEMORY_DIR" ]; then
  OVERLAP=""
  TMP_HEADERS=$(mktemp 2>/dev/null || echo "/tmp/liplus-headers-$$")
  TMP_TOKENS=$(mktemp 2>/dev/null || echo "/tmp/liplus-tokens-$$")
  for memfile in "$MEMORY_DIR/feedback.md" "$MEMORY_DIR/project.md"; do
    [ -f "$memfile" ] || continue
    grep -E '^## ' "$memfile" 2>/dev/null > "$TMP_HEADERS" || true
    while IFS= read -r header; do
      [ -n "$header" ] || continue
      title=$(printf '%s' "$header" | sed 's/^## //')
      printf '%s' "$title" | tr 'A-Z' 'a-z' | tr -cs 'a-z0-9' '\n' | awk 'length($0) >= 4' > "$TMP_TOKENS"
      [ -s "$TMP_TOKENS" ] || continue
      while IFS= read -r src; do
        [ -f "$src" ] || continue
        HIT=""
        SRC_LC=$(tr 'A-Z' 'a-z' < "$src")
        while IFS= read -r tok; do
          [ -n "$tok" ] || continue
          printf '%s' "$SRC_LC" | grep -qF "$tok" 2>/dev/null && HIT="${HIT}${tok} "
        done < "$TMP_TOKENS"
        [ -n "$HIT" ] && OVERLAP="${OVERLAP}  - $(basename "$memfile") [${title}] ~ $(basename "$src") (tokens: ${HIT% })
"
      done < <(find "$LIPLUS_DIR/rules" -type f -name '*.md' 2>/dev/null; find "$LIPLUS_DIR/skills" -maxdepth 2 -type f -name 'SKILL.md' 2>/dev/null)
    done < "$TMP_HEADERS"
  done
  rm -f "$TMP_HEADERS" "$TMP_TOKENS"
  [ -n "$OVERLAP" ] && PROMOTION_BODY="${PROMOTION_BODY}possible keyword overlap with Li+ source:
${OVERLAP}"
fi
register_section "promotion_candidates" "Promotion candidates (memory → Li+ source)" "$PROMOTION_BODY"

# --- self-evolution observation surface (due / overdue) ---
# Implements rules/evolution/cold-start-synthesis.md "Self-Evolution Observation
# Surface" (#1537). Port of the same block in adapter/claude/hooks/on-session-start.sh:
#   next_check <= today AND verdict_state == pending -> "observation due"
#   expires    <  today AND verdict_state == pending -> "observation overdue,
#                                                       human judgment needed"
#
# Deliberately NOT registered via register_section: the trigger is date-driven
# while the body is content-driven, so an unresolved entry keeps a byte-identical
# body and a fingerprint comparison would surface it once and then suppress it
# for the whole period it still needs attention. Empty body = silent skip.
# An entry past expires is reported as OVERDUE only (overdue carries the
# escalation; reporting it on both axes is noise). Date comparison is
# lexicographic on ISO YYYY-MM-DD, which is order-preserving.
OBSERVATION_BODY=""
OBSERVATION_FILE=""
if [ -n "$MEMORY_DIR" ] && [ -f "$MEMORY_DIR/self-evolution-observation.md" ]; then
  OBSERVATION_FILE="$MEMORY_DIR/self-evolution-observation.md"
fi
if [ -n "$OBSERVATION_FILE" ]; then
  TODAY=$(date +%Y-%m-%d 2>/dev/null || echo "")
  if [ -n "$TODAY" ]; then
    OBSERVATION_LIST=$(awk -v today="$TODAY" '
      function flush(   label) {
        if (name == "") return
        if (state == "pending") {
          label = ""
          if (expires != "" && expires < today) {
            label = "OVERDUE (expires " expires ", human judgment needed)"
          } else if (nextcheck != "" && nextcheck <= today) {
            label = "DUE (next_check " nextcheck ")"
          }
          if (label != "") {
            printf "  - %s: %s%s\n", label, name, (pr == "" ? "" : " [PR #" pr "]")
          }
        }
        name = ""; pr = ""; expires = ""; nextcheck = ""; state = ""
      }
      /^##[[:space:]]+observation:/ {
        flush()
        v = $0
        sub(/^##[[:space:]]+observation:[[:space:]]*/, "", v)
        gsub(/[[:space:]]+$/, "", v)
        name = v
        next
      }
      name != "" && /^[[:space:]]*pr:[[:space:]]*/ {
        v = $0; sub(/^[[:space:]]*pr:[[:space:]]*/, "", v); gsub(/[[:space:]]+$/, "", v); pr = v; next
      }
      name != "" && /^[[:space:]]*expires:[[:space:]]*/ {
        v = $0; sub(/^[[:space:]]*expires:[[:space:]]*/, "", v); gsub(/[[:space:]]+$/, "", v); expires = v; next
      }
      name != "" && /^[[:space:]]*next_check:[[:space:]]*/ {
        v = $0; sub(/^[[:space:]]*next_check:[[:space:]]*/, "", v); gsub(/[[:space:]]+$/, "", v); nextcheck = v; next
      }
      name != "" && /^[[:space:]]*verdict_state:[[:space:]]*/ {
        v = $0; sub(/^[[:space:]]*verdict_state:[[:space:]]*/, "", v); gsub(/[[:space:]]+$/, "", v); state = v; next
      }
      /^##[[:space:]]/ { flush() }
      END { flush() }
    ' "$OBSERVATION_FILE")
    if [ -n "$OBSERVATION_LIST" ]; then
      OBSERVATION_BODY="memory/self-evolution-observation.md - entries whose check window has opened:
${OBSERVATION_LIST}
Surfacing is observation, not auto-action. Verdict transition (settle / revert /
supersede) follows rules/evolution/memory-entry-format.md Self-Evolution
Observation Format."
    fi
  fi
fi

# Emitted before the diff sections so a due/overdue entry is not buried under
# whatever else changed.
OBSERVATION_EMITTED=0
if [ -n "$OBSERVATION_BODY" ]; then
  emit_section "Self-evolution observation (due / overdue)" "$OBSERVATION_BODY"
  OBSERVATION_EMITTED=1
fi

# ===================================================================
# Diff-only emission (startup)
# ===================================================================
# JSON handling uses Node.js (`node -e`) instead of an external `jq` binary.
# Node is a safe assumption: it is the runtime Codex CLI itself depends on
# (mirrors the fix applied to adapter/claude/hooks/on-session-start.sh in #1519;
# on-session-start.ps1, the Windows-native primary, already avoided jq via
# PowerShell-native ConvertFrom-Json/ConvertTo-Json).
FAIL_SAFE_FULL_EMIT=0
FAIL_SAFE_REASON=""

NODE_BIN=""
if command -v node >/dev/null 2>&1; then
  NODE_BIN="node"
fi

if [ -z "$(sha256_of probe)" ]; then FAIL_SAFE_FULL_EMIT=1; FAIL_SAFE_REASON="sha256 tool unavailable"; fi
if [ "$FAIL_SAFE_FULL_EMIT" -eq 0 ] && [ -z "$NODE_BIN" ]; then FAIL_SAFE_FULL_EMIT=1; FAIL_SAFE_REASON="node unavailable"; fi

# Read prior state, if present and parseable. On success, PRIOR_FP_DUMP holds
# one "key<TAB>fingerprint" line per recorded section (flat text, easy to
# grep from bash without needing associative arrays).
PRIOR_FP_DUMP=""
if [ "$FAIL_SAFE_FULL_EMIT" -eq 0 ]; then
  if [ -f "$STATE_FILE" ]; then
    PRIOR_FP_DUMP=$("$NODE_BIN" -e '
      const fs = require("fs");
      try {
        const raw = fs.readFileSync(process.argv[1], "utf8");
        const data = JSON.parse(raw);
        const sections = (data && typeof data === "object" && data.sections) || {};
        for (const k of Object.keys(sections)) {
          process.stdout.write(k + "\t" + String(sections[k]) + "\n");
        }
      } catch (e) {
        process.exit(1);
      }
    ' "$STATE_FILE" 2>/dev/null)
    if [ "$?" -ne 0 ]; then
      FAIL_SAFE_FULL_EMIT=1
      FAIL_SAFE_REASON="state file malformed JSON"
    fi
  else
    FAIL_SAFE_FULL_EMIT=1
    FAIL_SAFE_REASON="state file absent (first run or post-cleanup)"
  fi
fi

# Helper: look up a key's prior fingerprint from the flat PRIOR_FP_DUMP dump.
prior_fp_of() {
  local key="$1"
  [ -n "$PRIOR_FP_DUMP" ] || return 0
  printf '%s\n' "$PRIOR_FP_DUMP" | awk -F'\t' -v k="$key" '$1 == k { print $2; exit }'
}

EMITTED_ANY=0
NEW_FP_KEYS=(); NEW_FP_VALS=()
i=0
while [ "$i" -lt "${#SECTION_KEYS[@]}" ]; do
  key="${SECTION_KEYS[$i]}"; banner="${SECTION_BANNERS[$i]}"; body="${SECTION_BODIES[$i]}"
  i=$((i + 1))
  [ -z "$body" ] && continue
  current_fp=$(sha256_of "$body")
  prior_fp=""
  if [ "$FAIL_SAFE_FULL_EMIT" -eq 0 ]; then
    prior_fp=$(prior_fp_of "$key")
  fi
  if [ -n "$current_fp" ]; then
    NEW_FP_KEYS+=("$key")
    NEW_FP_VALS+=("$current_fp")
  fi
  if [ "$FAIL_SAFE_FULL_EMIT" -eq 1 ] || [ "$current_fp" != "$prior_fp" ] || [ -z "$current_fp" ]; then
    emit_section "$banner" "$body"; EMITTED_ANY=1
  fi
done

# The observation surface counts as material: pairing a just-emitted overdue
# entry with "No new orientation material" would be self-contradictory output.
if [ "$EMITTED_ANY" -eq 0 ] && [ "$OBSERVATION_EMITTED" -eq 0 ] && [ "$FAIL_SAFE_FULL_EMIT" -eq 0 ]; then
  emit_section "Orientation diff" "No new orientation material since last session. Prior in-context state remains authoritative."
fi

# Persist new state (best-effort; failure is non-fatal — next session will
# fall through to fail-safe full emit). Keys/values/timestamp are passed as
# argv to a single node invocation (no shell-side JSON string building).
if [ -n "$NODE_BIN" ]; then
  mkdir -p "$STATE_DIR" 2>/dev/null || true
  TS=$(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || echo "")
  NEW_FP_ARGV=()
  j=0
  while [ "$j" -lt "${#NEW_FP_KEYS[@]}" ]; do
    NEW_FP_ARGV+=("${NEW_FP_KEYS[$j]}" "${NEW_FP_VALS[$j]}")
    j=$((j + 1))
  done
  "$NODE_BIN" -e '
    const fs = require("fs");
    const outPath = process.argv[1];
    const ts = process.argv[2];
    const rest = process.argv.slice(3);
    const sections = {};
    for (let i = 0; i < rest.length; i += 2) {
      sections[rest[i]] = rest[i + 1];
    }
    const state = { sections: sections };
    if (ts) { state.last_emit_at = ts; }
    try {
      fs.writeFileSync(outPath, JSON.stringify(state) + "\n");
    } catch (e) {
      process.exit(1);
    }
  ' "$STATE_FILE" "$TS" "${NEW_FP_ARGV[@]}" 2>/dev/null || true
fi

if [ "$FAIL_SAFE_FULL_EMIT" -eq 1 ]; then
  emit "━━━ Cold-start Synthesis: instruction ━━━"
  emit "Fail-safe full emit (reason: ${FAIL_SAFE_REASON:-unknown}). All available"
  emit "material is shown above. Using it, perform Cold-start Synthesis through"
  emit "Character_Instance:"
  emit "1. Summarize the current Li+ state (active tag, recent structural shifts, unresolved threads)."
  emit "2. Report synthesis to the human as the opening orientation."
  emit "The hook only gathers material. Judgment and expression belong to the AI."
  emit "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
else
  emit "━━━ Cold-start Synthesis: instruction ━━━"
  emit "Diff-only emission: only sections changed since the prior session are shown"
  emit "above (rules + cold-start rule literal are always re-anchored). Using the diff"
  emit "plus your loaded layers, perform Cold-start Synthesis through Character_Instance:"
  emit "1. Summarize the current Li+ state delta (what changed; unresolved threads)."
  emit "2. Report synthesis to the human as the opening orientation — apply the"
  emit "   non-redundancy gate in rules/evolution/cold-start-synthesis.md (silent"
  emit "   skip when no unique insight remains after synthesis)."
  emit "The hook only gathers material. Judgment and expression belong to the AI."
  emit "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
fi

flush_json
exit 0
