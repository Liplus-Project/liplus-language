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

**Migration note for workspaces upgraded from earlier Li+ versions:** any
user-added keys currently sitting in `settings.json` (permissions / env / theme /
custom hooks / additional `mcp_tool` entries) should be moved to
`settings.local.json` before the first bootstrap under this rule. Otherwise the
compare-and-overwrite step (see below) detects content drift and overwrites
`settings.json` with the Li+ template, dropping the user keys.

## Bootstrap behavior

- If `{workspace_root}/.claude/settings.json` does **not exist**: create it from
  the literal JSON below.
- If `{workspace_root}/.claude/settings.json` **exists and content matches** the
  rendered template byte-for-byte: skip (no overwrite, no permission prompt).
- If `{workspace_root}/.claude/settings.json` **exists and content differs**:
  overwrite with the rendered template. `settings.json` is Li+ owned per the
  File ownership boundary; intentional user customizations belong in
  `settings.local.json`.
- Hook script bodies (`hooks/*.sh`) are regenerated on tag mismatch (per the
  `# Source: ... ({LI_PLUS_TAG})` comment line).

This compare-and-overwrite rule replaces the previous "do not modify if exists"
rule. The previous rule prevented Li+ from rolling out hook structure updates
automatically; the new rule keeps `settings.json` aligned with the template
release-by-release while sparing the user from sensitive-file permission prompts
on every bootstrap (only fires when content actually differs).

## settings.json

Target: `{workspace_root}/.claude/settings.json`

```json
{
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
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash",
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

- `adapter/claude/hooks/on-user-prompt.sh` — Character_Instance re-notify + webhook check
- `adapter/claude/hooks/on-session-start.sh` — Cold-start Synthesis material emitter
- `adapter/claude/hooks/post-tool-use.sh` — sub-issue refs auto-append on PR create

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
2. `github-webhook-mcp >= v0.11.3`. Earlier versions return generic JSON
   (`{pending_count, types, latest_received_at}`) which Claude Code parses
   successfully but discards because it does not match any UserPromptSubmit
   decision schema. v0.11.3 wraps `get_pending_status` results into the
   canonical decision shape (`hookSpecificOutput.hookEventName="UserPromptSubmit"`
   plus a natural language summary in `additionalContext`) on the local bridge
   side, so the wrapped output reaches the AI prompt context.

`Li+config.md`'s `LI_PLUS_WEBHOOK_DELIVERY` setting controls the *bash hook's*
reminder text behavior (poll / channel / mcp_hook) independently. The
`mcp_tool` entry itself fires unconditionally; setting
`LI_PLUS_WEBHOOK_DELIVERY=mcp_hook` suppresses the bash hook's reminder text so
the wrap delivery is the single source of webhook context.

If `github-webhook-mcp` is **not connected**: Claude Code's mcp_tool resolver
returns a `not connected` error per turn. The error is surfaced as plain text
to the AI but carries no actionable webhook payload. Workspaces that do not use
the webhook intake flow at all can leave the entry inert (the error is harmless
beyond the per-turn noise) or remove it knowing the next bootstrap will
restore it from the template.
