#!/bin/bash
# Source: adapter/claude/hooks/on-session-start.sh ({LI_PLUS_TAG})
# Cold-start Synthesis hook: emits orientation material for the session-opening turn.
# stdout is injected into the initial session context (Claude Code SessionStart contract).
# The hook does NOT synthesize — it only gathers material. AI performs synthesis
# through Character_Instance using the emitted material plus its own loaded layers.
#
# Matchers: startup / resume / clear / compact (see hooks-settings.md).
# Keep total output modest (a few KB). Truncate rather than skip when sources are large.
#
# Diff-only emission (matcher = startup only):
#   Each material section is fingerprinted (sha256 of the raw body) and the
#   fingerprint set is persisted at {workspace_root}/.claude/state/last-cold-start-emit.json.
#   On the next startup the hook compares current fingerprints to the stored set
#   and emits only sections whose body changed. The cold-start rule literal is
#   always emitted (drift recovery anchor). When no section changed, a single
#   "No new orientation material since last session" marker is emitted so the
#   human can still observe that a session boundary occurred.
#
#   Fail-safe: missing state, unreadable state, malformed JSON, or sha256 tool
#   absence collapses to "full emit" (every available section) and rewrites the
#   state. A corrupted diff is heavier than a redundant full emit.
#
#   resume / clear / compact matchers do not run diff comparison (the work
#   context is continuous; only the cold-start rule literal is re-anchored).
export PATH="$HOME/.local/bin:$PATH"
PROJECT_ROOT="${CLAUDE_PROJECT_DIR:-.}"
LIPLUS_DIR="$PROJECT_ROOT/liplus-language"
COLDSTART_MD="$LIPLUS_DIR/rules/evolution/cold-start-synthesis.md"
DECISION_STRUCTURE="$LIPLUS_DIR/docs/Decision-Structure.md"
STATE_DIR="$PROJECT_ROOT/.claude/state"
STATE_FILE="$STATE_DIR/last-cold-start-emit.json"
ADAPTER_FILE="$PROJECT_ROOT/.claude/CLAUDE.md"
CONFIG_FILE="$PROJECT_ROOT/Li+config.md"

# ===================================================================
# Prerequisite install: gh CLI
# ===================================================================
# Relocated from Li+update.md Phase 2.1. The hook ensures `~/.local/bin/gh`
# exists so the update walkthrough does not have to spell out install steps
# every session. Install is performed only when the binary is absent; presence
# is a silent skip. Failure does NOT abort the hook — it is surfaced as a
# cold-start material entry so the AI can ask the user to intervene.
GH_INSTALL_STATUS=""
if ! command -v "$HOME/.local/bin/gh" >/dev/null 2>&1 && [ ! -x "$HOME/.local/bin/gh" ]; then
  GH_INSTALL_LOG=$(mktemp 2>/dev/null || echo "/tmp/liplus-gh-install-$$.log")
  {
    set -e
    mkdir -p "$HOME/.local/bin"
    GH_VERSION="2.62.0"
    GH_ARCH="linux_amd64"
    GH_URL="https://github.com/cli/cli/releases/download/v${GH_VERSION}/gh_${GH_VERSION}_${GH_ARCH}.tar.gz"
    GH_TARBALL="$HOME/.local/bin/gh.tar.gz"
    GH_EXTRACT_DIR="$HOME/.local/bin/_gh_extract"
    mkdir -p "$GH_EXTRACT_DIR"
    curl -fsSL -o "$GH_TARBALL" "$GH_URL"
    tar -xzf "$GH_TARBALL" -C "$GH_EXTRACT_DIR" --strip-components=1
    mv "$GH_EXTRACT_DIR/bin/gh" "$HOME/.local/bin/gh"
    chmod +x "$HOME/.local/bin/gh"
    rm -rf "$GH_EXTRACT_DIR" "$GH_TARBALL"
  } > "$GH_INSTALL_LOG" 2>&1
  if [ -x "$HOME/.local/bin/gh" ]; then
    GH_INSTALL_STATUS="installed"
  else
    GH_INSTALL_STATUS="failed: $(tail -n 3 "$GH_INSTALL_LOG" 2>/dev/null | tr '\n' ' ')"
  fi
  rm -f "$GH_INSTALL_LOG" 2>/dev/null || true
fi

# Guard: if liplus-language source is not resolved yet (e.g. pre-bootstrap), exit silently
# AFTER emitting the gh install failure marker if applicable.
if [ ! -d "$LIPLUS_DIR" ]; then
  if [ "${GH_INSTALL_STATUS#failed}" != "$GH_INSTALL_STATUS" ]; then
    printf '━━━ gh install ━━━\n%s\n%s\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n' \
      "Prerequisite install failed. Master intervention required." \
      "Detail: $GH_INSTALL_STATUS"
  fi
  exit 0
fi

# --- matcher resolution ---
# Claude Code passes the SessionStart payload as JSON on stdin. We read it once
# (non-blocking with a short timeout) and extract the matcher. Empty / unreadable
# stdin falls back to "startup" so the diff-only path is the default.
HOOK_INPUT=""
if [ -t 0 ]; then
  HOOK_INPUT=""
else
  HOOK_INPUT=$(cat 2>/dev/null || true)
fi
MATCHER="startup"
if [ -n "$HOOK_INPUT" ]; then
  EXTRACTED=""
  if command -v jq >/dev/null 2>&1; then
    EXTRACTED=$(printf '%s' "$HOOK_INPUT" | jq -r '.matcher // .hook_event_name // empty' 2>/dev/null)
  fi
  # jq fallback: regex-extract "matcher":"value" from the JSON payload.
  # The matcher key is a flat string field per Claude Code SessionStart contract.
  if [ -z "$EXTRACTED" ]; then
    EXTRACTED=$(printf '%s' "$HOOK_INPUT" | sed -n 's/.*"matcher"[[:space:]]*:[[:space:]]*"\([a-z]*\)".*/\1/p' | head -n 1)
  fi
  case "$EXTRACTED" in
    startup|resume|clear|compact)
      MATCHER="$EXTRACTED"
      ;;
  esac
fi

# ===================================================================
# Update sentinel-skip verification
# ===================================================================
# Issue #1309: avoid Li+config + Li+update walkthrough on every session.
# 99% of sessions have no tag change, no schema change, and all config values
# resolved — verification only, no actual changes. The walkthrough costs ~4%
# context (10% with Li+config execution vs 6% without). The hook performs the
# three verifications and emits a single-line update status marker the AI
# parses to decide whether to read Li+config + Li+update at all.
#
# Three axes (ALL must pass for "unnecessary"):
#   1. adapter sentinel tag in .claude/CLAUDE.md == current LI_PLUS_REPO target tag (per LI_PLUS_CHANNEL)
#   2. Li+config.md schema canonical (no legacy keys present)
#   3. LI_PLUS_BASE_LANGUAGE and LI_PLUS_PROJECT_LANGUAGE resolved (non-comment, non-empty)
#
# Marker format (machine/AI-parseable, single line + optional reason):
#   LI_PLUS_UPDATE_STATUS=unnecessary     -> AI skips Li+update walkthrough; Li+config spot read (Read for value lookup, no execute) is permitted
#   LI_PLUS_UPDATE_STATUS=needed reason=<one or more axes>  -> AI runs normal update path
#
# AI-side contract: see adapter/claude/CLAUDE.md "Execute the following at
# startup" block. Master's literal phrase "Li+configを実行" / "Li+config を実行"
# bypasses the marker and forces the full walkthrough; that override is
# AI-side, not hook-side.
UPDATE_STATUS="needed"
UPDATE_REASONS=()

# --- axis 1: adapter sentinel tag vs current target tag ---
ADAPTER_TAG=""
if [ -f "$ADAPTER_FILE" ]; then
  ADAPTER_TAG=$(sed -n 's/^# --- Li+ BEGIN (\([^)]*\)) ---.*/\1/p' "$ADAPTER_FILE" | head -n 1)
fi

# Resolve LI_PLUS_CHANNEL from config (default = release, matches Li+update.md Phase 3.1).
LI_PLUS_CHANNEL_VAL=""
if [ -f "$CONFIG_FILE" ]; then
  LI_PLUS_CHANNEL_VAL=$(sed -n 's/^[[:space:]]*LI_PLUS_CHANNEL[[:space:]]*=[[:space:]]*\(.*\)$/\1/p' "$CONFIG_FILE" | head -n 1 | tr -d '\r')
fi
[ -n "$LI_PLUS_CHANNEL_VAL" ] || LI_PLUS_CHANNEL_VAL="release"

# Resolve target tag by channel (best-effort; failure forces "needed").
TARGET_TAG=""
case "$LI_PLUS_CHANNEL_VAL" in
  latest)
    TARGET_TAG=$(gh release view --repo Liplus-Project/liplus-language --json tagName --jq '.tagName' 2>/dev/null)
    ;;
  release)
    TARGET_TAG=$(gh release list --repo Liplus-Project/liplus-language --limit 1 --json tagName --jq '.[0].tagName' 2>/dev/null)
    ;;
  tag)
    TARGET_TAG=$(git -C "$LIPLUS_DIR" ls-remote --tags --sort=-creatordate origin 2>/dev/null \
      | awk -F'refs/tags/' 'NF==2 {print $2}' | sed 's/\^{}$//' | head -n 1)
    if [ -z "$TARGET_TAG" ]; then
      TARGET_TAG=$(git -C "$LIPLUS_DIR" tag --sort=-creatordate 2>/dev/null | head -n 1)
    fi
    ;;
esac

if [ -z "$ADAPTER_TAG" ] || [ -z "$TARGET_TAG" ] || [ "$ADAPTER_TAG" != "$TARGET_TAG" ]; then
  UPDATE_REASONS+=("sentinel-tag(adapter=${ADAPTER_TAG:-unknown},target=${TARGET_TAG:-unknown})")
fi

# --- axis 2: Li+config.md schema canonical (no legacy keys) ---
LEGACY_HIT=""
if [ -f "$CONFIG_FILE" ]; then
  # Match active (non-comment) lines containing any legacy key form.
  LEGACY_HIT=$(grep -E '^[[:space:]]*(LI_PLUS_REPOSITORY|USER_REPOSITORY|USER_REPOSITORY_EXECUTION_MODE)[[:space:]]*=|^[[:space:]]*[^#[:space:]][^=]*_EXECUTION_MODE[[:space:]]*=' "$CONFIG_FILE" 2>/dev/null | head -n 3)
fi
if [ -n "$LEGACY_HIT" ]; then
  UPDATE_REASONS+=("legacy-schema-keys-present")
fi

# --- axis 3: language contract resolved ---
BASE_LANG=""
PROJ_LANG=""
if [ -f "$CONFIG_FILE" ]; then
  BASE_LANG=$(sed -n 's/^[[:space:]]*LI_PLUS_BASE_LANGUAGE[[:space:]]*=[[:space:]]*\(.*\)$/\1/p' "$CONFIG_FILE" | head -n 1 | tr -d '\r' | sed 's/[[:space:]]*$//')
  PROJ_LANG=$(sed -n 's/^[[:space:]]*LI_PLUS_PROJECT_LANGUAGE[[:space:]]*=[[:space:]]*\(.*\)$/\1/p' "$CONFIG_FILE" | head -n 1 | tr -d '\r' | sed 's/[[:space:]]*$//')
fi
if [ -z "$BASE_LANG" ] || [ -z "$PROJ_LANG" ]; then
  UPDATE_REASONS+=("language-contract-unresolved(base=${BASE_LANG:-unset},project=${PROJ_LANG:-unset})")
fi

# --- emit update status marker ---
# Always emit first, before any cold-start material, so AI parses it before
# deciding whether to read Li+config.md and Li+update.md.
if [ "${#UPDATE_REASONS[@]}" -eq 0 ]; then
  UPDATE_STATUS="unnecessary"
  printf '━━━ Li+ update status ━━━\n'
  printf 'LI_PLUS_UPDATE_STATUS=unnecessary tag=%s channel=%s\n' "$TARGET_TAG" "$LI_PLUS_CHANNEL_VAL"
  printf 'Sentinel-skip applies: AI skips Li+update.md re-execution this session. Li+config.md spot read (Read for value lookup, do not execute contents) is permitted.\n'
  printf 'Override: Master input containing "Li+configを実行" / "Li+config を実行" forces the full walkthrough.\n'
  printf '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n'
else
  REASON_STR=$(printf '%s,' "${UPDATE_REASONS[@]}")
  REASON_STR="${REASON_STR%,}"
  printf '━━━ Li+ update status ━━━\n'
  printf 'LI_PLUS_UPDATE_STATUS=needed reason=%s\n' "$REASON_STR"
  printf 'AI must read Li+config.md and execute Li+update.md walkthrough this session.\n'
  printf '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n'
fi

# Emit gh install status marker after update status (only when install was attempted).
if [ -n "$GH_INSTALL_STATUS" ]; then
  printf '━━━ gh install ━━━\n%s\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n' "GH_INSTALL_STATUS=$GH_INSTALL_STATUS"
fi

# --- sha256 helper (portable: prefers sha256sum, falls back to shasum -a 256) ---
sha256_of() {
  local input="$1"
  if command -v sha256sum >/dev/null 2>&1; then
    printf '%s' "$input" | sha256sum | awk '{print $1}'
  elif command -v shasum >/dev/null 2>&1; then
    printf '%s' "$input" | shasum -a 256 | awk '{print $1}'
  else
    # No sha256 tool available — return empty so the caller treats diff as
    # unavailable and falls back to full emit.
    printf ''
  fi
}

emit_section() {
  local banner="$1"
  local body="$2"
  [ -n "$body" ] || return 0
  printf '━━━ %s ━━━\n%s\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n' "$banner" "$body"
}

# Section registry (parallel arrays). Keys are stable identifiers used in the
# state JSON; banners are the human-facing section titles; bodies are filled
# below by the gather phase.
SECTION_KEYS=()
SECTION_BANNERS=()
SECTION_BODIES=()

register_section() {
  local key="$1"
  local banner="$2"
  local body="$3"
  SECTION_KEYS+=("$key")
  SECTION_BANNERS+=("$banner")
  SECTION_BODIES+=("$body")
}

# --- coldstart literal block from rules/evolution/cold-start-synthesis.md ---
# This section is ALWAYS emitted (drift recovery anchor). It is not part of the
# diff-only comparison set.
COLDSTART_LITERAL=""
if [ -f "$COLDSTART_MD" ]; then
  # Strip frontmatter (lines between first two `---` markers) and H1 line
  COLDSTART_LITERAL=$(awk '/^---$/{n++; next} n>=2' "$COLDSTART_MD" | sed '1{/^# /d;}' | sed '/./,$!d')
fi

# --- recent decision structure index entries (head of file = index) ---
DECISION_HEAD=""
if [ -f "$DECISION_STRUCTURE" ]; then
  DECISION_HEAD=$(head -n 20 "$DECISION_STRUCTURE")
fi
register_section "decision_structure_head" "Decision structure index (docs/Decision-Structure.md head)" "$DECISION_HEAD"

# --- rules/ tree (fetch address table for cold-start-loaded rules cache) ---
# Issue #1422: cold-start loads the rule literal text into context, but at the
# judgment moment AI's attention does not always reach back to the underlying
# rule. Emitting the path tree of rules/ as an in-context index lets the AI
# resolve "which rule path should I read" without scanning loose headers across
# the prior emission. Filename = semantic identifier (kebab-case slugify of the
# heading topic) per rules/model/liplus-coding-rule.md Source File Format, so
# the path alone carries enough signal; no description extraction needed here.
#
# Generation is dynamic (per session), not a static artifact, to avoid stale
# cache after rule add / rename. Sits inside the diff-only mode via
# register_section, so unchanged trees do not re-emit.
#
# Scope = rules/ only. skills/ is handled by the host auto-invoke router on a
# separate axis; adapter/ is not a judgment-time fetch target.
RULES_TREE=""
if [ -d "$LIPLUS_DIR/rules" ]; then
  RULES_TREE=$(cd "$LIPLUS_DIR" && find rules -type f -name '*.md' 2>/dev/null | sort)
fi
register_section "rules_tree" "Rules tree (fetch address table for rules/ cache)" "$RULES_TREE"

# --- most recent release tag (includes prereleases) ---
LATEST_RELEASE=$(gh release list -R Liplus-Project/liplus-language --limit 3 2>/dev/null \
  | head -n 3)
register_section "recent_releases" "Recent releases (includes prereleases)" "$LATEST_RELEASE"

# --- open high-priority issues (in-progress + ready, capped) ---
OPEN_ISSUES=$(gh issue list -R Liplus-Project/liplus-language \
  --state open --label in-progress --limit 5 \
  --json number,title,labels \
  --jq '.[] | "#\(.number) \(.title) [\(.labels | map(.name) | join(","))]"' 2>/dev/null)
register_section "open_in_progress_issues" "Open in-progress issues (max 5)" "$OPEN_ISSUES"

# --- latest self-evaluation entry from host memory (if exists) ---
# Claude Code stores user memory at ~/.claude/projects/<slug>/memory/, where <slug>
# is CLAUDE_PROJECT_DIR with ':', '/', and '\' all replaced by '-'.
# Best-effort read only: silent skip when the file is absent.
CPD="${CLAUDE_PROJECT_DIR:-$PROJECT_ROOT}"
CCD_SLUG=$(printf '%s' "$CPD" | sed 's|[:/\\]|-|g')
SELFEVAL_FOUND=""
for candidate in \
  "$HOME/.claude/projects/$CCD_SLUG/memory/self-evaluation_log.md" \
  "$PROJECT_ROOT/memory/self-evaluation_log.md"; do
  if [ -f "$candidate" ]; then
    SELFEVAL_FOUND="$candidate"
    break
  fi
done
# Glob fallback: pick the most recently modified self-eval log under any project slug.
if [ -z "$SELFEVAL_FOUND" ]; then
  SELFEVAL_FOUND=$(ls -1t "$HOME"/.claude/projects/*/memory/self-evaluation_log.md 2>/dev/null | head -n 1)
fi
SELFEVAL_HEAD=""
if [ -n "$SELFEVAL_FOUND" ] && [ -f "$SELFEVAL_FOUND" ]; then
  SELFEVAL_HEAD=$(head -n 15 "$SELFEVAL_FOUND")
fi
register_section "self_eval_head" "Self-evaluation log head (most recent)" "$SELFEVAL_HEAD"

# --- promotion candidates (memory → Li+ source) ---
# Evolution Loop observe stage: surface pattern-detection candidates at cold-start
# so that AI sees promotion candidates without waiting for passive noticing.
# All three detectors are best-effort; silent skip when sources are absent.
# Threshold is adjustable via THRESHOLD_N (initial value = 2, see issue #1080).
THRESHOLD_N=2

# Resolve memory directory using the same lookup path as self-evaluation_log.md.
MEMORY_DIR=""
if [ -n "$SELFEVAL_FOUND" ]; then
  MEMORY_DIR=$(dirname "$SELFEVAL_FOUND")
fi

PROMOTION_BODY=""

# Detector 1: repeated (root_cause, domain-tag) combinations in self-evaluation_log.md.
# Log entries use lines like "root_cause: <category>" and "tags: <t1>, <t2>, ...".
# We pair each root_cause with the first tag on the following tags line and
# count duplicates. Any pair seen >= THRESHOLD_N times is surfaced.
if [ -n "$SELFEVAL_FOUND" ] && [ -f "$SELFEVAL_FOUND" ]; then
  PAIR_DUPES=$(awk -v n="$THRESHOLD_N" '
    /^[[:space:]]*root_cause:[[:space:]]*/ {
      sub(/^[[:space:]]*root_cause:[[:space:]]*/, "")
      rc=$0
      next
    }
    /^[[:space:]]*tags:[[:space:]]*/ && rc != "" {
      sub(/^[[:space:]]*tags:[[:space:]]*/, "")
      split($0, t, /,[[:space:]]*/)
      tag=t[1]
      gsub(/[[:space:]]+$/, "", tag)
      if (tag != "") {
        key=rc "|" tag
        count[key]++
      }
      rc=""
    }
    END {
      for (k in count) {
        if (count[k] >= n) {
          split(k, p, "|")
          printf "  - (%s, %s) x%d\n", p[1], p[2], count[k]
        }
      }
    }
  ' "$SELFEVAL_FOUND")
  if [ -n "$PAIR_DUPES" ]; then
    PROMOTION_BODY="${PROMOTION_BODY}repeated (root_cause, domain-tag) pairs:
${PAIR_DUPES}
"
  fi
fi

# Detector 2: recent section additions to memory/feedback.md or memory/project.md
# (within the last 7 days). Section headers match lines starting with '## '.
# Uses file mtime as the proxy for recency; if the file itself was modified
# within 7 days, list all '## ' section titles and flag when count >= THRESHOLD_N.
#
# Note: this 7d window is the memory-scan recency window (Cold-start observe
# stage surface), independent from the 3d cluster window in
# rules/evolution/promotion-judgment.md. The two timers serve different axes:
#   - 7d here = "did anything new land in memory recently? show it for AI review"
#   - 3d there = "has the same cluster crossed the noise floor for promotion?"
# Do not unify the two values; they intentionally sit on different axes.
if [ -n "$MEMORY_DIR" ] && [ -d "$MEMORY_DIR" ]; then
  RECENT_SECTIONS=""
  for memfile in "$MEMORY_DIR/feedback.md" "$MEMORY_DIR/project.md"; do
    [ -f "$memfile" ] || continue
    # file modified within last 7 days?
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
  if [ -n "$RECENT_SECTIONS" ]; then
    PROMOTION_BODY="${PROMOTION_BODY}recent memory additions (<= 7d):
${RECENT_SECTIONS}"
  fi
fi

# Detector 3: simple keyword overlap between memory section titles and Li+ source files.
# For each '## ' header in feedback.md / project.md, extract alphanumeric tokens of
# length >= 4 and check whether any token appears in a Li+ source file. Matches are
# surfaced as "possible overlap" candidates — not a promotion decision, only a hint.
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
      # Extract tokens (>=4 ASCII alnum chars). Non-ASCII titles yield no tokens.
      # Lowercase tokens (avoids unstable -iF combo on MinGW grep).
      printf '%s' "$title" | tr 'A-Z' 'a-z' | tr -cs 'a-z0-9' '\n' \
        | awk 'length($0) >= 4' > "$TMP_TOKENS"
      [ -s "$TMP_TOKENS" ] || continue
      while IFS= read -r src; do
        [ -f "$src" ] || continue
        HIT=""
        # Lowercase source snapshot for case-insensitive match without -iF combo.
        SRC_LC=$(tr 'A-Z' 'a-z' < "$src")
        while IFS= read -r tok; do
          [ -n "$tok" ] || continue
          if printf '%s' "$SRC_LC" | grep -qF "$tok" 2>/dev/null; then
            HIT="${HIT}${tok} "
          fi
        done < "$TMP_TOKENS"
        if [ -n "$HIT" ]; then
          OVERLAP="${OVERLAP}  - $(basename "$memfile") [${title}] ~ $(basename "$src") (tokens: ${HIT% })
"
        fi
      done < <(find "$LIPLUS_DIR/rules" -type f -name '*.md' 2>/dev/null; find "$LIPLUS_DIR/skills" -maxdepth 2 -type f -name 'SKILL.md' 2>/dev/null)
    done < "$TMP_HEADERS"
  done
  rm -f "$TMP_HEADERS" "$TMP_TOKENS"
  if [ -n "$OVERLAP" ]; then
    PROMOTION_BODY="${PROMOTION_BODY}possible keyword overlap with Li+ source:
${OVERLAP}"
  fi
fi
register_section "promotion_candidates" "Promotion candidates (memory → Li+ source)" "$PROMOTION_BODY"

# ===================================================================
# Emission phase
# ===================================================================
#
# Always emit cold-start rule literal first (drift recovery anchor).
emit_section "Cold-start Synthesis (rules/evolution/cold-start-synthesis.md literal)" "$COLDSTART_LITERAL"

# Non-startup matchers (resume / clear / compact): only the cold-start anchor is
# emitted. The work context is continuous; re-emitting the full material set
# would be the redundant noise this diff-only design exists to eliminate.
if [ "$MATCHER" != "startup" ]; then
  cat <<EOF
━━━ Cold-start Synthesis: instruction ━━━
Matcher = ${MATCHER}. Session is continuous (resume/clear/compact). Only the
cold-start rule literal is re-anchored above. Treat the prior session's
in-context state as authoritative; do not re-orient from scratch.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EOF
  exit 0
fi

# --- diff-only logic (startup matcher only) ---
#
# Compute current fingerprint per section. Load prior fingerprint set from
# state. Emit a section iff its fingerprint differs from the stored value or
# fail-safe (no state / unreadable / sha256 unavailable / jq unavailable)
# forces full emit.
FAIL_SAFE_FULL_EMIT=0
FAIL_SAFE_REASON=""

# sha256 availability check (used for both current fingerprints and state read).
if [ -z "$(sha256_of probe)" ]; then
  FAIL_SAFE_FULL_EMIT=1
  FAIL_SAFE_REASON="sha256 tool unavailable"
fi

# jq availability check: state read and write both require it. Without jq,
# diff comparison and state rewrite cannot proceed reliably.
if [ "$FAIL_SAFE_FULL_EMIT" -eq 0 ] && ! command -v jq >/dev/null 2>&1; then
  FAIL_SAFE_FULL_EMIT=1
  FAIL_SAFE_REASON="jq unavailable"
fi

# Read prior state, if present and parseable.
PRIOR_STATE_JSON=""
if [ "$FAIL_SAFE_FULL_EMIT" -eq 0 ]; then
  if [ -f "$STATE_FILE" ]; then
    if jq -e . "$STATE_FILE" >/dev/null 2>&1; then
      PRIOR_STATE_JSON=$(cat "$STATE_FILE")
    else
      FAIL_SAFE_FULL_EMIT=1
      FAIL_SAFE_REASON="state file malformed JSON"
    fi
  else
    FAIL_SAFE_FULL_EMIT=1
    FAIL_SAFE_REASON="state file absent (first run or post-cleanup)"
  fi
fi

# Build current fingerprints and emit per section.
EMITTED_ANY=0
NEW_STATE_JSON='{"sections":{}}'

i=0
while [ "$i" -lt "${#SECTION_KEYS[@]}" ]; do
  key="${SECTION_KEYS[$i]}"
  banner="${SECTION_BANNERS[$i]}"
  body="${SECTION_BODIES[$i]}"
  i=$((i + 1))

  # Empty body → no section to emit and no fingerprint to record.
  if [ -z "$body" ]; then
    continue
  fi

  current_fp=$(sha256_of "$body")

  prior_fp=""
  if [ "$FAIL_SAFE_FULL_EMIT" -eq 0 ] && [ -n "$PRIOR_STATE_JSON" ]; then
    prior_fp=$(printf '%s' "$PRIOR_STATE_JSON" | jq -r ".sections[\"$key\"] // empty" 2>/dev/null)
  fi

  # Update new state with current fingerprint (even if not emitted, so the
  # state always reflects "last gathered" not "last emitted"; this prevents
  # an unchanged section from being re-emitted forever after one stale state
  # read).
  if command -v jq >/dev/null 2>&1 && [ -n "$current_fp" ]; then
    NEW_STATE_JSON=$(printf '%s' "$NEW_STATE_JSON" | jq --arg k "$key" --arg v "$current_fp" '.sections[$k] = $v' 2>/dev/null || printf '%s' "$NEW_STATE_JSON")
  fi

  if [ "$FAIL_SAFE_FULL_EMIT" -eq 1 ] || [ "$current_fp" != "$prior_fp" ] || [ -z "$current_fp" ]; then
    emit_section "$banner" "$body"
    EMITTED_ANY=1
  fi
done

# If no section emitted under diff-only mode, emit the no-new-material marker
# so the human can still observe that a session boundary occurred (silent
# skip is intentionally avoided — it would hide the session transition).
if [ "$EMITTED_ANY" -eq 0 ] && [ "$FAIL_SAFE_FULL_EMIT" -eq 0 ]; then
  emit_section "Orientation diff" "No new orientation material since last session. Prior in-context state remains authoritative."
fi

# Persist new state (best-effort; failure is non-fatal — next session will
# fall through to fail-safe full emit).
if command -v jq >/dev/null 2>&1; then
  mkdir -p "$STATE_DIR" 2>/dev/null || true
  # Add a top-level timestamp for human-readable forensics.
  TS=$(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || echo "")
  if [ -n "$TS" ]; then
    NEW_STATE_JSON=$(printf '%s' "$NEW_STATE_JSON" | jq --arg t "$TS" '.last_emit_at = $t' 2>/dev/null || printf '%s' "$NEW_STATE_JSON")
  fi
  printf '%s\n' "$NEW_STATE_JSON" > "$STATE_FILE" 2>/dev/null || true
fi

# --- instruction to the AI: synthesize through Character_Instance ---
if [ "$FAIL_SAFE_FULL_EMIT" -eq 1 ]; then
  cat <<EOF
━━━ Cold-start Synthesis: instruction ━━━
Fail-safe full emit (reason: ${FAIL_SAFE_REASON:-unknown}). All available
material is shown above. Using it, perform Cold-start Synthesis through
Character_Instance:
1. Summarize the current Li+ state (active tag, recent structural shifts, unresolved threads).
2. Report synthesis to the human as the opening orientation.
The hook only gathers material. Judgment and expression belong to the AI.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EOF
else
  cat <<'EOF'
━━━ Cold-start Synthesis: instruction ━━━
Diff-only emission: only sections changed since the prior session are shown
above (cold-start rule literal is always re-anchored). Using the diff plus
your loaded layers, perform Cold-start Synthesis through Character_Instance:
1. Summarize the current Li+ state delta (what changed; unresolved threads).
2. Report synthesis to the human as the opening orientation — apply the
   non-redundancy gate in rules/evolution/cold-start-synthesis.md (silent
   skip when no unique insight remains after synthesis).
The hook only gathers material. Judgment and expression belong to the AI.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EOF
fi

exit 0
