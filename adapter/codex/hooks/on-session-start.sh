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
  if command -v jq >/dev/null 2>&1; then
    jq -n --arg ctx "$BUFFER" '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":$ctx}}'
  else
    local esc
    esc=$(printf '%s' "$BUFFER" | sed 's/\\/\\\\/g; s/"/\\"/g' | awk 'BEGIN{ORS=""} {printf "%s\\n", $0}')
    printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"%s"}}\n' "$esc"
  fi
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
if [ -n "$HOOK_INPUT" ] && command -v jq >/dev/null 2>&1; then
  PROJECT_ROOT=$(printf '%s' "$HOOK_INPUT" | jq -r '.cwd // empty' 2>/dev/null)
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
  if command -v jq >/dev/null 2>&1; then
    EXTRACTED=$(printf '%s' "$HOOK_INPUT" | jq -r '.matcher // .source // .session_source // empty' 2>/dev/null)
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

  # axis 3: language contract resolved
  BASE_LANG=""; PROJ_LANG=""
  if [ -f "$CONFIG_FILE" ]; then
    BASE_LANG=$(sed -n 's/^[[:space:]]*LI_PLUS_BASE_LANGUAGE[[:space:]]*=[[:space:]]*\(.*\)$/\1/p' "$CONFIG_FILE" | head -n 1 | tr -d '\r' | sed 's/[[:space:]]*$//')
    PROJ_LANG=$(sed -n 's/^[[:space:]]*LI_PLUS_PROJECT_LANGUAGE[[:space:]]*=[[:space:]]*\(.*\)$/\1/p' "$CONFIG_FILE" | head -n 1 | tr -d '\r' | sed 's/[[:space:]]*$//')
  fi
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
MEMORY_DIR=""
[ -n "$SELFEVAL_FOUND" ] && MEMORY_DIR=$(dirname "$SELFEVAL_FOUND")
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

# ===================================================================
# Diff-only emission (startup)
# ===================================================================
FAIL_SAFE_FULL_EMIT=0
FAIL_SAFE_REASON=""
if [ -z "$(sha256_of probe)" ]; then FAIL_SAFE_FULL_EMIT=1; FAIL_SAFE_REASON="sha256 tool unavailable"; fi
if [ "$FAIL_SAFE_FULL_EMIT" -eq 0 ] && ! command -v jq >/dev/null 2>&1; then FAIL_SAFE_FULL_EMIT=1; FAIL_SAFE_REASON="jq unavailable"; fi

PRIOR_STATE_JSON=""
if [ "$FAIL_SAFE_FULL_EMIT" -eq 0 ]; then
  if [ -f "$STATE_FILE" ]; then
    if jq -e . "$STATE_FILE" >/dev/null 2>&1; then PRIOR_STATE_JSON=$(cat "$STATE_FILE")
    else FAIL_SAFE_FULL_EMIT=1; FAIL_SAFE_REASON="state file malformed JSON"; fi
  else FAIL_SAFE_FULL_EMIT=1; FAIL_SAFE_REASON="state file absent (first run or post-cleanup)"; fi
fi

EMITTED_ANY=0
NEW_STATE_JSON='{"sections":{}}'
i=0
while [ "$i" -lt "${#SECTION_KEYS[@]}" ]; do
  key="${SECTION_KEYS[$i]}"; banner="${SECTION_BANNERS[$i]}"; body="${SECTION_BODIES[$i]}"
  i=$((i + 1))
  [ -z "$body" ] && continue
  current_fp=$(sha256_of "$body")
  prior_fp=""
  if [ "$FAIL_SAFE_FULL_EMIT" -eq 0 ] && [ -n "$PRIOR_STATE_JSON" ]; then
    prior_fp=$(printf '%s' "$PRIOR_STATE_JSON" | jq -r ".sections[\"$key\"] // empty" 2>/dev/null)
  fi
  if command -v jq >/dev/null 2>&1 && [ -n "$current_fp" ]; then
    NEW_STATE_JSON=$(printf '%s' "$NEW_STATE_JSON" | jq --arg k "$key" --arg v "$current_fp" '.sections[$k] = $v' 2>/dev/null || printf '%s' "$NEW_STATE_JSON")
  fi
  if [ "$FAIL_SAFE_FULL_EMIT" -eq 1 ] || [ "$current_fp" != "$prior_fp" ] || [ -z "$current_fp" ]; then
    emit_section "$banner" "$body"; EMITTED_ANY=1
  fi
done

if [ "$EMITTED_ANY" -eq 0 ] && [ "$FAIL_SAFE_FULL_EMIT" -eq 0 ]; then
  emit_section "Orientation diff" "No new orientation material since last session. Prior in-context state remains authoritative."
fi

if command -v jq >/dev/null 2>&1; then
  mkdir -p "$STATE_DIR" 2>/dev/null || true
  TS=$(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || echo "")
  [ -n "$TS" ] && NEW_STATE_JSON=$(printf '%s' "$NEW_STATE_JSON" | jq --arg t "$TS" '.last_emit_at = $t' 2>/dev/null || printf '%s' "$NEW_STATE_JSON")
  printf '%s\n' "$NEW_STATE_JSON" > "$STATE_FILE" 2>/dev/null || true
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
