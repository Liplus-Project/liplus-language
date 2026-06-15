# Source: adapter/codex/hooks/on-user-prompt.ps1 ({LI_PLUS_TAG})
# Codex UserPromptSubmit hook (Windows native / PowerShell).
# Port of adapter/claude/hooks/on-user-prompt.sh.
#
# Per-turn Trigger Check Gate re-arm + webhook reminder. The gate re-arm is the
# deterministic firing surface for rules/model/trigger-check-gate.md.
# Character_Instance is loaded via AGENTS.md (always-present root instruction),
# not re-notified per turn.
#
# Codex contract difference vs Claude: UserPromptSubmit context injection on
# Codex requires JSON on stdout (hookSpecificOutput.additionalContext). Claude
# accepts plain text on UserPromptSubmit stdout; Codex does not. So this port
# wraps the gate text into the JSON envelope.
#
# Webhook delivery: the Claude version emits a reminder so the AI calls the
# github-webhook-mcp tool. The poll/channel/mcp_hook switch is read from
# Li+config.md LI_PLUS_WEBHOOK_DELIVERY (default = poll = emit reminder).
$ErrorActionPreference = 'SilentlyContinue'

# Read stdin payload (Codex passes JSON: session_id, cwd, hook_event_name, ...).
$raw = [Console]::In.ReadToEnd()
$payload = $null
if ($raw) { try { $payload = $raw | ConvertFrom-Json } catch { $payload = $null } }

# Resolve project root: prefer payload cwd, fall back to CODEX_PROJECT_DIR / PWD.
$projectRoot = $null
if ($payload -and $payload.cwd) { $projectRoot = $payload.cwd }
if (-not $projectRoot -and $env:CODEX_PROJECT_DIR) { $projectRoot = $env:CODEX_PROJECT_DIR }
if (-not $projectRoot) { $projectRoot = (Get-Location).Path }

# --- Webhook delivery mode (poll / channel / mcp_hook) ---
$webhookDelivery = ''
$configFile = Join-Path $projectRoot 'Li+config.md'
if (Test-Path -LiteralPath $configFile) {
  $line = Select-String -LiteralPath $configFile -Pattern '^LI_PLUS_WEBHOOK_DELIVERY=' -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($line) { $webhookDelivery = ($line.Line -replace '^LI_PLUS_WEBHOOK_DELIVERY=', '').Trim() }
}

$sb = [System.Text.StringBuilder]::new()

if ($webhookDelivery -ne 'channel' -and $webhookDelivery -ne 'mcp_hook') {
  [void]$sb.AppendLine('')
  [void]$sb.AppendLine('━━━ Webhook: check pending notifications ━━━')
  [void]$sb.AppendLine('Run mcp__github-webhook-mcp__get_pending_status silently.')
  [void]$sb.AppendLine('Report only foreground-relevant or notable items.')
  [void]$sb.AppendLine('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
}

# --- Trigger Check Gate re-arm (every turn) ---
[void]$sb.AppendLine('')
[void]$sb.AppendLine('━━━ Trigger Check Gate ━━━')
[void]$sb.AppendLine('Before any non-trivial speech or action, run the 5-axis check (one No -> pause, retrieve, verify):')
[void]$sb.AppendLine('  Rule / Literal / Source / Frame / Character')
[void]$sb.AppendLine('Situational routing: external content read -> Frame + Source. Asserting from internal memory -> Source. Applying a Li+ rule -> Rule + Literal.')
[void]$sb.AppendLine('Axis detail: rules/model/trigger-check-gate.md (always-on).')
[void]$sb.AppendLine('━━━━━━━━━━━━━━━━━━━━━━━━━━')

$context = $sb.ToString()

# Emit Codex JSON envelope (hookSpecificOutput.additionalContext reaches the model).
$out = @{
  hookSpecificOutput = @{
    hookEventName    = 'UserPromptSubmit'
    additionalContext = $context
  }
}
$out | ConvertTo-Json -Depth 5 -Compress
