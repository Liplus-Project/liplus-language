#!/bin/bash
# Source: adapter/claude/hooks/on-session-start.sh ({LI_PLUS_TAG})
# Cold-start Synthesis hook: emits orientation material for the session-opening turn.
# stdout is injected into the initial session context (Claude Code SessionStart contract).
# The hook does NOT synthesize — it only gathers material. AI performs synthesis
# through Character_Instance using the emitted material plus its own loaded layers.
#
# Matchers: startup / resume / clear / compact (see hooks-settings.md).
# Keep total output modest (a few KB). Truncate rather than skip when sources are large.
export PATH="$HOME/.local/bin:$PATH"
PROJECT_ROOT="${CLAUDE_PROJECT_DIR:-.}"
LIPLUS_DIR="$PROJECT_ROOT/liplus-language"
COLDSTART_MD="$LIPLUS_DIR/rules/evolution/cold-start-synthesis.md"
DECISION_LOG="$LIPLUS_DIR/docs/a.-Decision-Log.md"

# Guard: if liplus-language source is not resolved yet (e.g. pre-bootstrap), exit silently.
[ -d "$LIPLUS_DIR" ] || exit 0

emit_section() {
  local banner="$1"
  local body="$2"
  [ -n "$body" ] || return 0
  printf '━━━ %s ━━━\n%s\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n' "$banner" "$body"
}

# --- coldstart literal block from rules/cold-start-synthesis.md ---
if [ -f "$COLDSTART_MD" ]; then
  # Strip frontmatter (lines between first two `---` markers) and H1 line
  COLDSTART_LITERAL=$(awk '/^---$/{n++; next} n>=2' "$COLDSTART_MD" | sed '1{/^# /d;}' | sed '/./,$!d')
  emit_section "Cold-start Synthesis (rules/cold-start-synthesis.md literal)" "$COLDSTART_LITERAL"
fi

# --- recent docs/a.- decision log entries (head of file = index) ---
if [ -f "$DECISION_LOG" ]; then
  DECISION_HEAD=$(head -n 40 "$DECISION_LOG")
  emit_section "Decision log index (docs/a.-Decision-Log.md head)" "$DECISION_HEAD"
fi

# --- most recent release tag (includes prereleases) ---
LATEST_RELEASE=$(gh release list -R Liplus-Project/liplus-language --limit 3 2>/dev/null \
  | head -n 3)
if [ -n "$LATEST_RELEASE" ]; then
  emit_section "Recent releases (includes prereleases)" "$LATEST_RELEASE"
fi

# --- open high-priority issues (in-progress + ready, capped) ---
OPEN_ISSUES=$(gh issue list -R Liplus-Project/liplus-language \
  --state open --label in-progress --limit 5 \
  --json number,title,labels \
  --jq '.[] | "#\(.number) \(.title) [\(.labels | map(.name) | join(","))]"' 2>/dev/null)
if [ -n "$OPEN_ISSUES" ]; then
  emit_section "Open in-progress issues (max 5)" "$OPEN_ISSUES"
fi

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
if [ -n "$SELFEVAL_FOUND" ] && [ -f "$SELFEVAL_FOUND" ]; then
  SELFEVAL_HEAD=$(head -n 30 "$SELFEVAL_FOUND")
  emit_section "Self-evaluation log head (most recent)" "$SELFEVAL_HEAD"
fi

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

emit_section "Promotion candidates (memory → Li+ source)" "$PROMOTION_BODY"

# --- instruction to the AI: synthesize through Character_Instance ---
cat <<'EOF'
━━━ Cold-start Synthesis: instruction ━━━
Using the material above, perform Cold-start Synthesis through Character_Instance:
1. Summarize the current Li+ state (active tag, recent structural shifts, unresolved threads).
2. Report synthesis to the human as the opening orientation.
The hook only gathers material. Judgment and expression belong to the AI.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EOF

exit 0
