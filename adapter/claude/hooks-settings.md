# hooks-settings.md — Claude Code settings.json hook bindings

Layer = L6 Adapter Layer (Claude Code binding)
Semantic source = adapter/claude/CLAUDE.md trigger contract + L1 Model Layer / L2 Evolution Layer / L3 Task Layer / L4 Operations Layer foreground intake rules.
This file defines the entire `{workspace_root}/.claude/settings.json` content.

Bootstrap target: runtime=claude only.
Hook script bodies live as real files under `adapter/claude/hooks/` and are copied
verbatim into `{workspace_root}/.claude/hooks/` at bootstrap time.

## File ownership boundary

`{workspace_root}/.claude/settings.json` = **Li+ owned**. Bootstrap renders it
from the literal template below.

`{workspace_root}/.claude/settings.local.json` = **user owned**. Li+ never touches
this file. Anything the workspace owner wants persisted alongside Li+'s wiring —
`permissions`, `env`, `theme`, additional `command` hooks, additional `mcp_tool`
hooks for other MCP servers — goes here.

Claude Code reads both files at runtime and merges them, so user keys in
`settings.local.json` remain effective without entering Li+'s template surface.

Move user-added keys found in `settings.json` (permissions / env / theme / custom
hooks / additional `mcp_tool` entries) to `settings.local.json` before bootstrap;
the compare-and-overwrite step below drops them from `settings.json`.

## Bootstrap behavior

- If `{workspace_root}/.claude/settings.json` does **not exist**: create it from
  the literal JSON below.
- Write the rendered template with LF line endings and a trailing newline, on the
  create branch above and the overwrite branch below alike. Fix the newline at write
  time; do not leave it to the writer's default text mode (Windows text mode converts
  `\n` to `\r\n`, which makes the skip below unreachable from the moment the file is
  written).
- If `{workspace_root}/.claude/settings.json` **exists and content matches** the
  rendered template after newline normalization: skip (no overwrite, no permission
  prompt). Normalization applies to both sides before comparison and covers two points
  only: CRLF -> LF, and presence or absence of a trailing newline. Nothing else is
  normalized — a difference in whitespace, key order, indentation or any value falls to
  the branch below.
- If `{workspace_root}/.claude/settings.json` **exists and content differs**:
  overwrite with the rendered template. `settings.json` is Li+ owned per the
  File ownership boundary; intentional user customizations belong in
  `settings.local.json`.
- Hook script bodies (`hooks/*.sh`) are regenerated on tag mismatch (per the
  `# Source: ... ({LI_PLUS_TAG})` comment line).

## settings.json

Target: `{workspace_root}/.claude/settings.json`

```json
{
  "outputStyle": "character_Instance",
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash \"$CLAUDE_PROJECT_DIR/.claude/hooks/on-user-prompt.sh\""
          },
          {
            "type": "mcp_tool",
            "server": "github-webhook-mcp",
            "tool": "get_pending_status",
            "input": {}
          }
        ]
      }
    ],
    "SessionStart": [
      {
        "matcher": "startup",
        "hooks": [
          {
            "type": "command",
            "command": "bash \"$CLAUDE_PROJECT_DIR/.claude/hooks/on-session-start.sh\""
          }
        ]
      },
      {
        "matcher": "resume",
        "hooks": [
          {
            "type": "command",
            "command": "bash \"$CLAUDE_PROJECT_DIR/.claude/hooks/on-session-start.sh\""
          }
        ]
      },
      {
        "matcher": "clear",
        "hooks": [
          {
            "type": "command",
            "command": "bash \"$CLAUDE_PROJECT_DIR/.claude/hooks/on-session-start.sh\""
          }
        ]
      },
      {
        "matcher": "compact",
        "hooks": [
          {
            "type": "command",
            "command": "bash \"$CLAUDE_PROJECT_DIR/.claude/hooks/on-session-start.sh\""
          }
        ]
      },
      {
        "matcher": "fork",
        "hooks": [
          {
            "type": "command",
            "command": "bash \"$CLAUDE_PROJECT_DIR/.claude/hooks/on-session-start.sh\""
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash|Write|Edit|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "bash \"$CLAUDE_PROJECT_DIR/.claude/hooks/post-tool-use.sh\""
          }
        ]
      }
    ]
  }
}
```

## Hook script sources

Real files, copied verbatim into `{workspace_root}/.claude/hooks/` on bootstrap
(with `{LI_PLUS_TAG}` placeholder replaced by the resolved target tag):

- `adapter/claude/hooks/on-user-prompt.sh` — per-turn Li+ update status re-emit (re-emits the `LI_PLUS_UPDATE_STATUS=needed` marker with its `sentinel-tag(...)` reason while `{workspace_root}/.claude/state/update-status.txt` records a non-empty target tag, the `.claude/CLAUDE.md` sentinel tag differs from it, and the sentinel still equals the one recorded beside it; local reads only, silent otherwise and when the file is absent) + Trigger Check Gate re-arm + webhook re-arm (the call half is `poll`-only; the handling half is emitted in every delivery mode — see the mcp_tool entry behavior section below). Character_Instance is loaded via output-styles, not per-turn re-notify
- `adapter/claude/hooks/on-session-start.sh` — Cold-start Synthesis material emitter (matcher-aware: `startup` runs diff-only against `{workspace_root}/.claude/state/last-cold-start-emit.json`; `resume` / `clear` / `compact` / `fork` re-anchor only the cold-start rule anchor — see `rules/evolution/cold-start-synthesis.md` for the emission-state table)

  `LI_PLUS_AGENT_KEY` (env var, default `default`): partitions the diff-only
  state file per key — see `rules/evolution/cold-start-synthesis.md` Hook
  Emission Contract.

  Update status state: on every matcher that reaches the update-status
  verification, a `needed` result writes one line
  `status=needed target=<target tag> adapter=<sentinel tag>` to
  `{workspace_root}/.claude/state/update-status.txt`, and an `unnecessary`
  result removes the file. `on-user-prompt.sh` reads it every turn. The file is
  workspace-level and not partitioned by `LI_PLUS_AGENT_KEY`.

  All five documented SessionStart matchers are registered; keep all five. An
  unregistered matcher does not fall through to another entry — the hook does
  not run for that entry point, and that session starts with no
  `LI_PLUS_UPDATE_STATUS` marker and no language-contract banner. `fork` covers
  `--fork-session` with `--resume` / `--continue`, the `/fork` background copy,
  and `/branch`.
- `adapter/claude/hooks/post-tool-use.sh` — sub-issue refs auto-append on PR create,
  with a one-line `additionalContext` firing trace on every run that matched the
  command (per-line table in `docs/6.-Adapter.md`), and a stray-script scan
  of the file a `Write` / `Edit` / `MultiEdit` call just wrote, reported through
  `additionalContext` without rewriting the file. The PostToolUse matcher
  `Bash|Write|Edit|MultiEdit` is what lets the file-writing tools reach it.

Each script carries a `# Source: ... ({LI_PLUS_TAG})` comment line near the top as
the tag-tracking anchor. Bootstrap's tag-mismatch check reads this line.

## mcp_tool entry behavior

The default template includes a `type: "mcp_tool"` UserPromptSubmit hook entry
that invokes `get_pending_status` on `github-webhook-mcp`. Claude Code v2.1.118+
parses the tool's text content as JSON; only output matching a Claude Code hook
decision schema reaches the AI prompt context (docs literal at
https://code.claude.com/docs/en/hooks).

Preconditions for the entry to actually deliver webhook context to the AI:

1. `mcp__github-webhook-mcp` is connected as an MCP server in the workspace.
2. `github-webhook-mcp >= v0.11.3`, whose bridge wraps `get_pending_status` into the
   UserPromptSubmit decision shape. Output from earlier versions is discarded by
   Claude Code.

`Li+config.md`'s `LI_PLUS_WEBHOOK_DELIVERY` setting controls the *bash hook's*
call half (poll / channel / mcp_hook) independently. The `mcp_tool` entry itself
fires unconditionally; setting `LI_PLUS_WEBHOOK_DELIVERY=mcp_hook` suppresses the
bash hook's "call the tool yourself" line, so the wrap delivery is the single
source of webhook context.

It does not suppress the handling half: the delivery mode selects only who calls
the tool. The report filter and the `mark_processed` re-arm are emitted by the
hook in every mode; do not leave them to the always-on canonical alone
(`rules/operations/main-agent-procedures.md` Foreground webhook notification
intake), whose firing moment is `each user turn start`.

If `github-webhook-mcp` is **not connected**: Claude Code's mcp_tool resolver
returns a `not connected` error per turn. The error is surfaced as plain text
to the AI but carries no actionable webhook payload. Workspaces that do not use
the webhook intake flow at all can leave the entry inert (the error is harmless
beyond the per-turn noise) or remove it knowing the next bootstrap will
restore it from the template.
