# Source: adapter/codex/hooks/on-session-start.ps1 ({LI_PLUS_TAG})
# Codex SessionStart hook (Windows native / PowerShell). PRIMARY Windows path.
# Port of adapter/claude/hooks/on-session-start.sh.
#
# Three responsibilities (the first is Codex-specific; Claude gets it from the
# always-loaded .claude/rules/ folder which Codex has no equivalent of):
#   1. RULES INJECTION (Codex-only): read rules/*.md from the LI_PLUS_REPO clone
#      and emit them as additionalContext. This is the Codex substitute for
#      Claude's .claude/rules/ always-on folder (#1502 verified design).
#   2. Update-status verification: sentinel tag / config schema / language
#      contract -> emit LI_PLUS_UPDATE_STATUS marker (parsed by AGENTS.md startup
#      block to decide whether to run the Li+config + Li+update walkthrough).
#   3. Cold-start material gathering (decision structure head, releases, open
#      issues, self-eval head, promotion candidates) with diff-only emission.
#
# Codex contract difference vs Claude: SessionStart context injection on Codex
# requires JSON on stdout (hookSpecificOutput.additionalContext). Claude injects
# raw stdout directly. So the WHOLE emission is accumulated into one buffer and
# wrapped into the JSON envelope at the end.
#
# Matchers: startup / resume / clear / compact (see hooks.json / config.toml).
#   startup            -> full pipeline: rules injection + update status +
#                         diff-only cold-start material.
#   resume/clear/compact -> rules re-injection + cold-start rule literal
#                         re-anchor only (work context continuous; no diff eval).
#
# NOTE on rules injection + compact: #1502 leaves "does additionalContext survive
# auto-compaction on Codex" UNVERIFIED (Codex App has no manual /compact). We
# re-inject rules on the compact matcher as the safer-side design; if a future
# real-device test shows additionalContext survives compaction, the compact
# re-injection can be trimmed.
$ErrorActionPreference = 'SilentlyContinue'

# ---------- helpers ----------
$script:BUFFER = [System.Text.StringBuilder]::new()
function Emit([string]$text) { [void]$script:BUFFER.AppendLine($text) }
function Emit-Section([string]$banner, [string]$body) {
  if (-not $body) { return }
  Emit "━━━ $banner ━━━"
  Emit $body
  Emit "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  Emit ''
}
function Sha256Of([string]$s) {
  if ($null -eq $s) { $s = '' }
  $sha = [System.Security.Cryptography.SHA256]::Create()
  $bytes = [System.Text.Encoding]::UTF8.GetBytes($s)
  ($sha.ComputeHash($bytes) | ForEach-Object { $_.ToString('x2') }) -join ''
}
function Flush-Json {
  # Wrap the accumulated buffer into the Codex SessionStart JSON envelope.
  $ctx = $script:BUFFER.ToString()
  $out = @{
    hookSpecificOutput = @{
      hookEventName     = 'SessionStart'
      additionalContext = $ctx
    }
  }
  $out | ConvertTo-Json -Depth 5 -Compress
}

# ---------- stdin / paths ----------
$raw = [Console]::In.ReadToEnd()
$payload = $null
if ($raw) { try { $payload = $raw | ConvertFrom-Json } catch { $payload = $null } }

$projectRoot = $null
if ($payload -and $payload.cwd) { $projectRoot = $payload.cwd }
if (-not $projectRoot -and $env:CODEX_PROJECT_DIR) { $projectRoot = $env:CODEX_PROJECT_DIR }
if (-not $projectRoot) { $projectRoot = (Get-Location).Path }

$liplusDir       = Join-Path $projectRoot 'liplus-language'
$coldstartMd     = Join-Path $liplusDir 'rules/evolution/cold-start-synthesis.md'
$decisionStruct  = Join-Path $liplusDir 'docs/Decision-Structure.md'
$stateDir        = Join-Path $projectRoot '.codex/state'
$stateFile       = Join-Path $stateDir 'last-cold-start-emit.json'
$adapterFile     = Join-Path $projectRoot 'AGENTS.md'
$configFile      = Join-Path $projectRoot 'Li+config.md'

# ---------- matcher resolution ----------
# Codex stdin uses hook_event_name + an optional source/matcher field. We treat
# the SessionStart "source" (startup|resume|clear|compact) the same as Claude's
# matcher. Default = startup.
$matcher = 'startup'
if ($payload) {
  $m = $null
  foreach ($k in @('matcher','source','session_source')) {
    if ($payload.PSObject.Properties[$k] -and $payload.$k) { $m = $payload.$k; break }
  }
  if ($m -in @('startup','resume','clear','compact')) { $matcher = $m }
}

# ---------- guard: liplus source not resolved yet (pre-bootstrap) ----------
if (-not (Test-Path -LiteralPath $liplusDir)) {
  Emit '━━━ Li+ update status ━━━'
  Emit 'LI_PLUS_UPDATE_STATUS=needed reason=liplus-source-unresolved'
  Emit 'liplus-language clone not found under workspace root. Run the Li+config / Li+update walkthrough.'
  Emit '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
  Flush-Json
  exit 0
}

# ===================================================================
# RULES INJECTION (Codex-only; substitute for Claude .claude/rules/)
# ===================================================================
# Read every rules/**/*.md from the clone and emit the literal bodies. This is
# the always-on rules surface for Codex. Runs on EVERY matcher (startup and
# resume/clear/compact) because Codex has no folder-level persistence — the
# only always-on substrate is re-injection per session boundary.
$rulesRoot = Join-Path $liplusDir 'rules'
if (Test-Path -LiteralPath $rulesRoot) {
  $ruleFiles = Get-ChildItem -LiteralPath $rulesRoot -Recurse -Filter '*.md' -File -ErrorAction SilentlyContinue |
    Sort-Object FullName
  if ($ruleFiles) {
    Emit '━━━ Li+ rules (always-on; injected because Codex has no .claude/rules equivalent) ━━━'
    foreach ($rf in $ruleFiles) {
      $rel = $rf.FullName.Substring($liplusDir.Length).TrimStart('\','/') -replace '\\','/'
      $content = Get-Content -LiteralPath $rf.FullName -Raw -ErrorAction SilentlyContinue
      Emit "----- $rel -----"
      Emit $content
      Emit ''
    }
    Emit '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
    Emit ''
  }
}

# ===================================================================
# Update sentinel-skip verification (axes 1-3) — startup matcher only.
# On resume/clear/compact the work context is continuous, so we do not re-run
# the update-status verification (matches the Claude design: only the cold-start
# anchor is re-emitted on those matchers). Rules were already re-injected above.
# ===================================================================
if ($matcher -eq 'startup') {
  $updateReasons = @()

  # --- axis 1: adapter sentinel tag vs current target tag ---
  $adapterTag = ''
  if (Test-Path -LiteralPath $adapterFile) {
    $line = Select-String -LiteralPath $adapterFile -Pattern '^# --- Li\+ BEGIN \(([^)]*)\) ---' -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($line) { $adapterTag = $line.Matches[0].Groups[1].Value }
  }

  $channel = ''
  if (Test-Path -LiteralPath $configFile) {
    $cl = Select-String -LiteralPath $configFile -Pattern '^\s*LI_PLUS_CHANNEL\s*=\s*(.*)$' -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($cl) { $channel = $cl.Matches[0].Groups[1].Value.Trim() }
  }
  if (-not $channel) { $channel = 'release' }

  $targetTag = ''
  switch ($channel) {
    'latest' { $targetTag = (gh release view --repo Liplus-Project/liplus-language --json tagName --jq '.tagName' 2>$null) }
    'release' { $targetTag = (gh release list --repo Liplus-Project/liplus-language --limit 1 --json tagName --jq '.[0].tagName' 2>$null) }
    'tag' {
      # ls-remote is the only source of truth (stale local clone must not emit a
      # false "unnecessary"). On failure leave empty -> forces "needed".
      $remote = git -C $liplusDir ls-remote --tags --sort=-creatordate origin 2>$null
      if ($remote) {
        $targetTag = ($remote -split "`n" |
          ForEach-Object { if ($_ -match 'refs/tags/(.+?)(\^\{\})?$') { $matches[1] } } |
          Select-Object -First 1)
      }
    }
  }
  if ($targetTag) { $targetTag = $targetTag.Trim() }

  if (-not $adapterTag -or -not $targetTag -or ($adapterTag -ne $targetTag)) {
    $at = if ($adapterTag) { $adapterTag } else { 'unknown' }
    $tt = if ($targetTag) { $targetTag } else { 'unknown' }
    $updateReasons += "sentinel-tag(adapter=$at,target=$tt)"
  }

  # --- axis 2: Li+config.md schema canonical (no legacy keys) ---
  if (Test-Path -LiteralPath $configFile) {
    $legacy = Select-String -LiteralPath $configFile -Pattern '^\s*(LI_PLUS_REPOSITORY|USER_REPOSITORY|USER_REPOSITORY_EXECUTION_MODE)\s*=|^\s*[^#\s][^=]*_EXECUTION_MODE\s*=' -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($legacy) { $updateReasons += 'legacy-schema-keys-present' }
  }

  # --- axis 3: language contract resolved ---
  $baseLang = ''
  $projLang = ''
  if (Test-Path -LiteralPath $configFile) {
    $bl = Select-String -LiteralPath $configFile -Pattern '^\s*LI_PLUS_BASE_LANGUAGE\s*=\s*(.*)$' -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($bl) { $baseLang = $bl.Matches[0].Groups[1].Value.Trim() }
    $pl = Select-String -LiteralPath $configFile -Pattern '^\s*LI_PLUS_PROJECT_LANGUAGE\s*=\s*(.*)$' -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($pl) { $projLang = $pl.Matches[0].Groups[1].Value.Trim() }
  }
  if (-not $baseLang -or -not $projLang) {
    $b = if ($baseLang) { $baseLang } else { 'unset' }
    $p = if ($projLang) { $projLang } else { 'unset' }
    $updateReasons += "language-contract-unresolved(base=$b,project=$p)"
  }

  # --- emit update status marker ---
  if ($updateReasons.Count -eq 0) {
    Emit '━━━ Li+ update status ━━━'
    Emit "LI_PLUS_UPDATE_STATUS=unnecessary tag=$targetTag channel=$channel"
    Emit 'Sentinel-skip applies: AI skips Li+update.md re-execution this session. Li+config.md spot read (Read for value lookup, do not execute contents) is permitted.'
    Emit 'Override: Master input containing "Li+configを実行" / "Li+config を実行" forces the full walkthrough.'
    Emit '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
    Emit ''
  } else {
    $reasonStr = ($updateReasons -join ',')
    Emit '━━━ Li+ update status ━━━'
    Emit "LI_PLUS_UPDATE_STATUS=needed reason=$reasonStr"
    Emit 'AI must read Li+config.md and execute Li+update.md walkthrough this session.'
    Emit '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
    Emit ''
  }
}

# ===================================================================
# Cold-start material gathering
# ===================================================================

# --- coldstart literal block (ALWAYS emitted; drift recovery anchor) ---
$coldstartLiteral = ''
if (Test-Path -LiteralPath $coldstartMd) {
  $lines = Get-Content -LiteralPath $coldstartMd -ErrorAction SilentlyContinue
  # Strip frontmatter (between first two --- markers) and a leading H1 line.
  $dashCount = 0
  $afterFm = @()
  foreach ($l in $lines) {
    if ($l -eq '---') { $dashCount++; continue }
    if ($dashCount -ge 2) { $afterFm += $l }
  }
  # Drop a leading H1, then drop leading blank lines.
  if ($afterFm.Count -gt 0 -and $afterFm[0] -match '^# ') { $afterFm = $afterFm[1..($afterFm.Count-1)] }
  while ($afterFm.Count -gt 0 -and $afterFm[0].Trim() -eq '') { $afterFm = $afterFm[1..($afterFm.Count-1)] }
  $coldstartLiteral = ($afterFm -join "`n")
}
Emit-Section 'Cold-start Synthesis (rules/evolution/cold-start-synthesis.md literal)' $coldstartLiteral

# Non-startup matchers: rules were re-injected + cold-start anchor emitted; stop.
if ($matcher -ne 'startup') {
  Emit '━━━ Cold-start Synthesis: instruction ━━━'
  Emit "Matcher = $matcher. Session is continuous (resume/clear/compact). Rules were"
  Emit 'reinjected and the cold-start rule literal re-anchored above. Treat the prior'
  Emit "session's in-context state as authoritative; do not re-orient from scratch."
  Emit '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
  Flush-Json
  exit 0
}

# --- register diff-only sections (startup only) ---
$sectionKeys    = @()
$sectionBanners = @()
$sectionBodies  = @()
function Register-Section([string]$key, [string]$banner, [string]$body) {
  $script:sectionKeys    += $key
  $script:sectionBanners += $banner
  $script:sectionBodies  += $body
}

# decision structure index head
$decisionHead = ''
if (Test-Path -LiteralPath $decisionStruct) {
  $decisionHead = (Get-Content -LiteralPath $decisionStruct -TotalCount 20 -ErrorAction SilentlyContinue) -join "`n"
}
Register-Section 'decision_structure_head' 'Decision structure index (docs/Decision-Structure.md head)' $decisionHead

# rules tree (fetch address table)
$rulesTree = ''
if (Test-Path -LiteralPath $rulesRoot) {
  $rel = Get-ChildItem -LiteralPath $rulesRoot -Recurse -Filter '*.md' -File -ErrorAction SilentlyContinue |
    ForEach-Object { 'rules/' + ($_.FullName.Substring($rulesRoot.Length).TrimStart('\','/') -replace '\\','/') } |
    Sort-Object
  $rulesTree = ($rel -join "`n")
}
Register-Section 'rules_tree' 'Rules tree (fetch address table for rules/ cache)' $rulesTree

# recent releases (includes prereleases)
$recentReleases = ''
$rr = gh release list -R Liplus-Project/liplus-language --limit 3 2>$null
if ($rr) { $recentReleases = (($rr -split "`n") | Select-Object -First 3) -join "`n" }
Register-Section 'recent_releases' 'Recent releases (includes prereleases)' $recentReleases

# open in-progress issues (max 5)
$openIssues = ''
$oi = gh issue list -R Liplus-Project/liplus-language --state open --label in-progress --limit 5 --json number,title,labels --jq '.[] | "#\(.number) \(.title) [\(.labels | map(.name) | join(","))]"' 2>$null
if ($oi) { $openIssues = ($oi -split "`n" | Where-Object { $_ }) -join "`n" }
Register-Section 'open_in_progress_issues' 'Open in-progress issues (max 5)' $openIssues

# self-evaluation log head (workspace-local memory under Codex)
# Codex has no ~/.claude/projects/<slug>/memory; the workspace-local memory/
# directory is the available surface. Best-effort.
$selfEvalFound = ''
foreach ($cand in @(
    (Join-Path $projectRoot 'memory/self-evaluation_log.md'),
    (Join-Path $liplusDir 'memory/self-evaluation_log.md'))) {
  if (Test-Path -LiteralPath $cand) { $selfEvalFound = $cand; break }
}
$selfEvalHead = ''
if ($selfEvalFound) {
  $selfEvalHead = (Get-Content -LiteralPath $selfEvalFound -TotalCount 15 -ErrorAction SilentlyContinue) -join "`n"
}
Register-Section 'self_eval_head' 'Self-evaluation log head (most recent)' $selfEvalHead

# promotion candidates (memory -> Li+ source)
$thresholdN = 2
$memoryDir = ''
if ($selfEvalFound) { $memoryDir = Split-Path -Parent $selfEvalFound }
$promotionBody = ''

# Detector 1: repeated (root_cause, first-tag) pairs in self-evaluation_log.md.
if ($selfEvalFound -and (Test-Path -LiteralPath $selfEvalFound)) {
  $pairCount = @{}
  $rc = ''
  foreach ($l in (Get-Content -LiteralPath $selfEvalFound -ErrorAction SilentlyContinue)) {
    if ($l -match '^\s*root_cause:\s*(.*)$') { $rc = $matches[1].Trim(); continue }
    if ($l -match '^\s*tags:\s*(.*)$' -and $rc -ne '') {
      $tag = (($matches[1] -split ',')[0]).Trim()
      if ($tag) { $key = "$rc|$tag"; if ($pairCount.ContainsKey($key)) { $pairCount[$key]++ } else { $pairCount[$key] = 1 } }
      $rc = ''
    }
  }
  $dupes = ''
  foreach ($k in $pairCount.Keys) {
    if ($pairCount[$k] -ge $thresholdN) {
      $p = $k -split '\|'
      $dupes += "  - ($($p[0]), $($p[1])) x$($pairCount[$k])`n"
    }
  }
  if ($dupes) { $promotionBody += "repeated (root_cause, domain-tag) pairs:`n$dupes" }
}

# Detector 2: recent (<=7d) memory section additions in feedback.md / project.md.
if ($memoryDir -and (Test-Path -LiteralPath $memoryDir)) {
  $recentSections = ''
  foreach ($mf in @((Join-Path $memoryDir 'feedback.md'), (Join-Path $memoryDir 'project.md'))) {
    if (-not (Test-Path -LiteralPath $mf)) { continue }
    $mtime = (Get-Item -LiteralPath $mf -ErrorAction SilentlyContinue).LastWriteTime
    if ($mtime -and $mtime -ge (Get-Date).AddDays(-7)) {
      $secs = Select-String -LiteralPath $mf -Pattern '^## ' -ErrorAction SilentlyContinue | ForEach-Object { '  - ' + ($_.Line -replace '^## ', '') }
      if ($secs -and $secs.Count -ge $thresholdN) {
        $recentSections += "$(Split-Path -Leaf $mf) (modified within 7d, $($secs.Count) sections):`n" + ($secs -join "`n") + "`n"
      }
    }
  }
  if ($recentSections) { $promotionBody += "recent memory additions (<= 7d):`n$recentSections" }
}

# Detector 3: keyword overlap between memory section titles and Li+ source files.
if ($memoryDir -and (Test-Path -LiteralPath $memoryDir)) {
  $overlap = ''
  $srcFiles = @()
  $srcFiles += Get-ChildItem -LiteralPath $rulesRoot -Recurse -Filter '*.md' -File -ErrorAction SilentlyContinue
  $skillsRoot = Join-Path $liplusDir 'skills'
  if (Test-Path -LiteralPath $skillsRoot) {
    $srcFiles += Get-ChildItem -LiteralPath $skillsRoot -Recurse -Filter 'SKILL.md' -File -ErrorAction SilentlyContinue
  }
  $srcLc = @{}
  foreach ($sf in $srcFiles) {
    $c = Get-Content -LiteralPath $sf.FullName -Raw -ErrorAction SilentlyContinue
    if ($c) { $srcLc[$sf.FullName] = $c.ToLower() }
  }
  foreach ($mf in @((Join-Path $memoryDir 'feedback.md'), (Join-Path $memoryDir 'project.md'))) {
    if (-not (Test-Path -LiteralPath $mf)) { continue }
    $headers = Select-String -LiteralPath $mf -Pattern '^## ' -ErrorAction SilentlyContinue
    foreach ($h in $headers) {
      $title = ($h.Line -replace '^## ', '')
      $tokens = ($title.ToLower() -split '[^a-z0-9]+') | Where-Object { $_.Length -ge 4 } | Select-Object -Unique
      if (-not $tokens) { continue }
      foreach ($sfPath in $srcLc.Keys) {
        $hit = @()
        foreach ($tok in $tokens) { if ($srcLc[$sfPath].Contains($tok)) { $hit += $tok } }
        if ($hit.Count -gt 0) {
          $overlap += "  - $(Split-Path -Leaf $mf) [$title] ~ $(Split-Path -Leaf $sfPath) (tokens: $($hit -join ' '))`n"
        }
      }
    }
  }
  if ($overlap) { $promotionBody += "possible keyword overlap with Li+ source:`n$overlap" }
}
Register-Section 'promotion_candidates' 'Promotion candidates (memory → Li+ source)' $promotionBody

# ===================================================================
# Diff-only emission (startup matcher)
# ===================================================================
$failSafeFull = $false
$failSafeReason = ''

# Read prior state.
$priorFp = @{}
if (Test-Path -LiteralPath $stateFile) {
  try {
    $prior = Get-Content -LiteralPath $stateFile -Raw | ConvertFrom-Json
    if ($prior -and $prior.sections) {
      foreach ($prop in $prior.sections.PSObject.Properties) { $priorFp[$prop.Name] = $prop.Value }
    }
  } catch {
    $failSafeFull = $true; $failSafeReason = 'state file malformed JSON'
  }
} else {
  $failSafeFull = $true; $failSafeReason = 'state file absent (first run or post-cleanup)'
}

$emittedAny = $false
$newSections = @{}
for ($i = 0; $i -lt $sectionKeys.Count; $i++) {
  $key = $sectionKeys[$i]; $banner = $sectionBanners[$i]; $body = $sectionBodies[$i]
  if (-not $body) { continue }
  $curFp = Sha256Of $body
  $newSections[$key] = $curFp
  $pf = if ($priorFp.ContainsKey($key)) { $priorFp[$key] } else { '' }
  if ($failSafeFull -or ($curFp -ne $pf)) {
    Emit-Section $banner $body
    $emittedAny = $true
  }
}

if (-not $emittedAny -and -not $failSafeFull) {
  Emit-Section 'Orientation diff' 'No new orientation material since last session. Prior in-context state remains authoritative.'
}

# Persist new state (best-effort).
try {
  if (-not (Test-Path -LiteralPath $stateDir)) { New-Item -ItemType Directory -Path $stateDir -Force | Out-Null }
  $ts = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
  $stateObj = @{ sections = $newSections; last_emit_at = $ts }
  $stateObj | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $stateFile -Encoding UTF8
} catch { }

# --- instruction to the AI ---
if ($failSafeFull) {
  Emit '━━━ Cold-start Synthesis: instruction ━━━'
  Emit "Fail-safe full emit (reason: $failSafeReason). All available material is shown"
  Emit 'above. Using it, perform Cold-start Synthesis through Character_Instance:'
  Emit '1. Summarize the current Li+ state (active tag, recent structural shifts, unresolved threads).'
  Emit '2. Report synthesis to the human as the opening orientation.'
  Emit 'The hook only gathers material. Judgment and expression belong to the AI.'
  Emit '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
} else {
  Emit '━━━ Cold-start Synthesis: instruction ━━━'
  Emit 'Diff-only emission: only sections changed since the prior session are shown'
  Emit 'above (rules + cold-start rule literal are always re-anchored). Using the diff'
  Emit 'plus your loaded layers, perform Cold-start Synthesis through Character_Instance:'
  Emit '1. Summarize the current Li+ state delta (what changed; unresolved threads).'
  Emit '2. Report synthesis to the human as the opening orientation — apply the'
  Emit '   non-redundancy gate in rules/evolution/cold-start-synthesis.md (silent'
  Emit '   skip when no unique insight remains after synthesis).'
  Emit 'The hook only gathers material. Judgment and expression belong to the AI.'
  Emit '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
}

Flush-Json
exit 0
