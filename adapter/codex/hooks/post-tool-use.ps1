# Source: adapter/codex/hooks/post-tool-use.ps1 ({LI_PLUS_TAG})
# Codex PostToolUse hook (Windows native / PowerShell).
# Port of adapter/claude/hooks/post-tool-use.sh.
#
# After adapter flattening (#1102) the only remaining injection is:
#   gh pr create  ->  auto-append missing sub-issue `Closes #NNN` to the PR body.
# rules/* are always-present (AGENTS.md core + SessionStart rules injection) and
# skills/* auto-invoke by description, so section-extraction injection is gone.
#
# Codex PostToolUse stdin payload: tool_name, tool_input.command, tool_response.
# For Bash, tool_response is a JSON string holding the command's model-facing
# output, not an object - so it differs from Claude Code, whose Bash result is
# an object carrying `stdout` (#2060). If a future Codex build changes this
# shape, update the extraction below.
$ErrorActionPreference = 'SilentlyContinue'

$raw = [Console]::In.ReadToEnd()
if (-not $raw) { exit 0 }
$payload = $null
try { $payload = $raw | ConvertFrom-Json } catch { exit 0 }
if (-not $payload) { exit 0 }

$toolName = $payload.tool_name
$command  = $null
if ($payload.tool_input) { $command = $payload.tool_input.command }

if ($toolName -cne 'Bash') { exit 0 }
if (-not $command) { exit 0 }

# First line only, strip heredoc tail.
$cmdLine = ($command -split "`n")[0]
$cmdLine = $cmdLine -replace '<<.*$', ''

# Resolve project root + liplus clone location.
$projectRoot = $payload.cwd
if (-not $projectRoot -and $env:CODEX_PROJECT_DIR) { $projectRoot = $env:CODEX_PROJECT_DIR }
if (-not $projectRoot) { $projectRoot = (Get-Location).Path }
$liplusDir = Join-Path $projectRoot 'liplus-language'

function Emit-Context([string]$ctx) {
  if (-not $ctx) { exit 0 }
  $out = @{
    hookSpecificOutput = @{
      hookEventName     = 'PostToolUse'
      additionalContext = $ctx
    }
  }
  # Write raw UTF-8 bytes so non-ASCII survives Windows PowerShell 5.1
  # (default redirected-output encoding is ANSI).
  $json = $out | ConvertTo-Json -Depth 5 -Compress
  $stdout = [System.Console]::OpenStandardOutput()
  $bytes = [System.Text.Encoding]::UTF8.GetBytes($json)
  $stdout.Write($bytes, 0, $bytes.Length); $stdout.Flush()
}

function Repo-From-Origin {
  $url = git -C $liplusDir remote get-url origin 2>$null
  if (-not $url) { return '' }
  $m = [regex]::Match($url, '[^/@:]+/[^/]+$')
  if (-not $m.Success) { return '' }
  return ($m.Value -replace '\.git$', '')
}

# Firing trace (#1710). Once the command has matched `gh pr create`, every exit
# below emits exactly one line naming how the run ended; calls that never
# matched stay silent. Emit it only as `hookSpecificOutput.additionalContext`
# on exit 0, not on plain stdout, stderr or exit 2. docs/6.-Adapter.md
# post-tool-use.sh holds the per-line table and the channel evidence.
function Emit-Trace([string]$line) {
  Emit-Context "post-tool-use: $line"
  exit 0
}

# on_pr: gh pr create -> sub-issue auto-append to PR body.
if ($cmdLine -notmatch 'gh(\.exe)? pr create') { exit 0 }

# Codex's Bash tool_response is itself the output string: the hook runtime
# hands over the command's model-facing output as a JSON string value, with no
# `output` field to read. Any other type reads as absent, as in the shell
# ports, rather than being coerced to text.
$output = $null
if ($payload.tool_response -is [string]) { $output = $payload.tool_response }
if (-not $output) { Emit-Trace 'gh pr create matched, but tool_response is absent, empty or not a string; no sub-issue refs appended.' }

$prMatch = [regex]::Match($output, '/pull/(\d+)')
if (-not $prMatch.Success) { Emit-Trace 'gh pr create matched, but tool_response carries no /pull/<number> URL; no sub-issue refs appended.' }
$prNumber = $prMatch.Groups[1].Value

$repo = Repo-From-Origin
# No clone to ask (api mode, #2031): read the repository out of the PR URL
# `gh pr create` printed.
if (-not $repo) {
  $urlMatch = [regex]::Match($output, '([^/\s]+/[^/\s]+)/pull/\d+')
  if ($urlMatch.Success) { $repo = $urlMatch.Groups[1].Value }
}
if (-not $repo) { Emit-Trace "PR #${prNumber}: repository could not be resolved; no sub-issue refs appended." }

# Native output arrives as one string per line. Keep the body as one string
# with its newlines, so the PATCH below sends its line breaks intact.
$prBody = (gh api "repos/$repo/pulls/$prNumber" --jq '.body' 2>$null) -join "`n"
if (-not $prBody) { Emit-Trace "PR #${prNumber}: body could not be read or is empty; no sub-issue refs appended." }

# Parent = the first `#<n>` that directly follows a GitHub closing keyword
# (close / closes / closed / fix / fixes / fixed / resolve / resolves /
# resolved, any case, optionally followed by a colon). A bare `#<n>` with no
# keyword before it is never taken as the parent.
$parentMatch = [regex]::Match($prBody, '(?i)(?<![A-Za-z0-9_])(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?):?[ \t]+#([0-9]+)')
if (-not $parentMatch.Success) { Emit-Trace "PR #${prNumber}: body carries no closing #<issue> reference; no sub-issue refs appended." }
$parentIssue = $parentMatch.Groups[1].Value

$subRaw = gh api "repos/$repo/issues/$parentIssue/sub_issues" --jq '.[].number' 2>$null
$subIssueNumbers = @($subRaw -split "`n" | Where-Object { $_ -match '^\d+$' })
if ($subIssueNumbers.Count -eq 0) { Emit-Trace "PR #${prNumber}: parent #${parentIssue} has no sub-issues, or they could not be read; nothing to append." }

$missing = @()
foreach ($num in $subIssueNumbers) {
  $num = $num.Trim()
  if (-not $num) { continue }
  if (-not [regex]::IsMatch($prBody, "#$num(\D|$)")) { $missing += $num }
}
if ($missing.Count -eq 0) { Emit-Trace "PR #${prNumber}: every sub-issue of parent #${parentIssue} is already referenced; nothing to append." }

$additions = ''
foreach ($num in $missing) { $additions += "`nCloses #$num" }
$newBody = "$prBody$additions"
$refs = ($missing | ForEach-Object { "Closes #$_" }) -join ', '

# The exit status decides which line is emitted: an append is reported only
# when the PATCH itself succeeded.
gh api "repos/$repo/pulls/$prNumber" --method PATCH -f body="$newBody" 2>$null | Out-Null
if ($LASTEXITCODE -eq 0) { Emit-Trace "PR #${prNumber}: sub-issue refs auto-appended (parent #${parentIssue}): $refs." }
Emit-Trace "PR #${prNumber}: PATCH of the body failed; sub-issue refs NOT appended (parent #${parentIssue}): $refs."
