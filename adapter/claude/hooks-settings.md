# hooks-settings.md — Claude Code settings.json hook bindings

Layer = L6 Adapter Layer (Claude Code binding)
Semantic source = adapter/claude/CLAUDE.md trigger contract + L1 Model Layer / L2 Evolution Layer / L3 Task Layer / L4 Operations Layer foreground intake rules.
This file defines the `hooks` section of `{workspace_root}/.claude/settings.json`.

Bootstrap target: runtime=claude only.
Hook script bodies live as real files under `adapter/claude/hooks/` and are copied
verbatim into `{workspace_root}/.claude/hooks/` at bootstrap time. Only the
`settings.json` binding needs markdown-format housing, because existing
workspace-side `settings.json` may already contain unrelated keys
(`permissions`, `env`, `theme`, other component hooks) that Li+ must not touch.

## Bootstrap behavior

- If `{workspace_root}/.claude/settings.json` does not exist: create it from the
  literal JSON below (initial template; permissions and other keys are added
  later by the workspace owner).
- If `{workspace_root}/.claude/settings.json` exists: **do not modify it**. The
  workspace owns the file once it has been created. Any future change to the
  hooks structure below must be applied manually by the human, guided by release
  notes — Li+ will not silently rewrite user settings.
- Hook script bodies (`hooks/*.sh`) are regenerated on tag mismatch. The
  `settings.json` structure is stable and is not regenerated.

Structure stability rationale: hook script paths and matcher names below are
deliberately long-lived — hook logic changes happen inside the script files,
not in the settings.json wiring. If the wiring ever needs to change, surface
it through release notes so the human decides when to apply it.

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
