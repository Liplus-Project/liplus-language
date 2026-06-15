# hooks-config.md — Codex hook bindings (hooks.json / config.toml)

Layer = L6 Adapter Layer (Codex binding)
Semantic source = adapter/codex/AGENTS.md trigger contract + L1 Model Layer / L2
Evolution Layer / L3 Task Layer / L4 Operations Layer foreground intake rules.
This file is the Codex counterpart of `adapter/claude/hooks-settings.md`. It
defines the `{workspace_root}/.codex/hooks.json` content (primary) and an
equivalent `config.toml` `[hooks]` snippet (alternate placement).

Bootstrap target: runtime=codex only.
Hook script bodies live as real files under `adapter/codex/hooks/` and are copied
verbatim into `{workspace_root}/.codex/hooks/` at bootstrap time.

## Placement summary (Codex vs Claude)

| Surface | Claude | Codex |
|---|---|---|
| host instruction file | `.claude/CLAUDE.md` | `AGENTS.md` (root) |
| hook registration | `.claude/settings.json` `hooks` | `.codex/hooks.json` (or `config.toml` `[hooks]`) |
| hook script bodies | `.claude/hooks/*.sh` | `.codex/hooks/*.ps1` (+ `*.sh` fallback) |
| skills | `.claude/skills/<name>/SKILL.md` | `.agents/skills/<name>/SKILL.md` |
| subagents | `.claude/agents/*.md` | `.codex/agents/*.md` |
| always-on rules | `.claude/rules/**/*.md` (folder auto-load) | injected by SessionStart hook (no folder equivalent) |
| diff-only state | `.claude/state/last-cold-start-emit.json` | `.codex/state/last-cold-start-emit.json` |

The placements (`.agents/skills`, `.codex/`, AGENTS.md) are real-device verified in
#1502: skills auto-fire by description with no trust gate; hooks run on Windows
native via PowerShell; SessionStart `additionalContext` reaches the model.

## One-time GUI trust requirement (Codex-specific friction)

Unlike Claude hooks, **Codex hooks require a one-time GUI trust before they run**
(verified in #1502):

1. After bootstrap writes `.codex/hooks.json` + `.codex/hooks/*`, open the Codex
   App and go to **Settings → Hooks → (this project row) → trust**.
   - The CLI `/hooks` command does **not** exist in the Codex App — trust is
     GUI-only.
2. Trust is granted **per hook content hash**. When a Li+ build changes a hook
   body (tag bump regenerates `*.ps1` / `*.sh`), Codex **re-prompts for trust**.
   Master must re-trust after each build that touches the hooks.
3. Before trust is granted, hooks do **not** run (and write no log) — this is the
   trust gate stopping execution, not a discovery failure. Skills are unaffected
   (no trust gate).

This friction has no Claude equivalent. The bootstrap walkthrough and
`docs/D.-Installation.md` must surface it (handled in the bootstrap follow-up,
not here). Without trust, the SessionStart rules injection and the per-turn gate
re-arm silently do nothing — so trust is a hard precondition for Li+ "always-on"
behavior on Codex.

## File ownership boundary

`{workspace_root}/.codex/hooks.json` = **Li+ owned**. Bootstrap renders it from
the literal template below (compare-and-overwrite on content drift, same policy
as the Claude `settings.json`).

`{workspace_root}/.codex/config.toml` = **user owned** when present for non-Li+
settings. If the user prefers TOML placement of hooks over `hooks.json`, the
`[hooks]` snippet below can be merged into `config.toml` instead; do not maintain
both at once (Codex would register the hooks twice). The `hooks.json` template is
the Li+ default; the TOML snippet is the documented alternate.

## Bootstrap behavior

- If `{workspace_root}/.codex/hooks.json` does **not exist**: create it from the
  literal JSON below.
- If it **exists and content matches** byte-for-byte: skip (no overwrite).
- If it **exists and content differs**: overwrite with the rendered template
  (`hooks.json` is Li+ owned).
- Hook script bodies (`hooks/*.ps1`, `hooks/*.sh`) are regenerated on tag
  mismatch (per the `# Source: ... ({LI_PLUS_TAG})` comment line). Regeneration
  changes the content hash, which **invalidates the GUI trust** — re-trust is
  required (see above).

## Path safety

Both the `command` (POSIX) and `commandWindows` paths use absolute paths under
`{workspace_root}/.codex/hooks/`. The bootstrap substitutes `{WORKSPACE_ROOT}`
with the resolved absolute workspace path at install time. Quote any path that
may contain spaces. The proven Windows invocation form (verified in #1502) is:

```
powershell -NoProfile -ExecutionPolicy Bypass -File "<abs path>.ps1"
```

The `.ps1` reads JSON on stdin, optionally logs, and writes the
`hookSpecificOutput` JSON envelope to stdout.

## hooks.json

Target: `{workspace_root}/.codex/hooks.json`

`{WORKSPACE_ROOT}` is replaced with the absolute workspace path at bootstrap.

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|resume|clear|compact",
        "hooks": [
          {
            "type": "command",
            "command": "bash \"{WORKSPACE_ROOT}/.codex/hooks/on-session-start.sh\"",
            "commandWindows": "powershell -NoProfile -ExecutionPolicy Bypass -File \"{WORKSPACE_ROOT}/.codex/hooks/on-session-start.ps1\"",
            "timeout": 60,
            "statusMessage": "Li+ cold-start + rules injection"
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash \"{WORKSPACE_ROOT}/.codex/hooks/on-user-prompt.sh\"",
            "commandWindows": "powershell -NoProfile -ExecutionPolicy Bypass -File \"{WORKSPACE_ROOT}/.codex/hooks/on-user-prompt.ps1\"",
            "timeout": 30,
            "statusMessage": "Li+ Trigger Check Gate re-arm"
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
            "command": "bash \"{WORKSPACE_ROOT}/.codex/hooks/post-tool-use.sh\"",
            "commandWindows": "powershell -NoProfile -ExecutionPolicy Bypass -File \"{WORKSPACE_ROOT}/.codex/hooks/post-tool-use.ps1\"",
            "timeout": 60,
            "statusMessage": "Li+ sub-issue refs auto-append"
          }
        ]
      }
    ]
  }
}
```

### Matcher notes

- Codex matchers are regex (verified against the official hooks schema):
  `"startup|resume|clear|compact"` matches all four SessionStart sources in one
  group — no need for four separate Claude-style entries.
- `PostToolUse` matcher `"Bash"` filters to Bash tool calls (the hook body also
  re-checks `tool_name == "Bash"` as a defensive guard).
- `UserPromptSubmit` has no matcher (fires every turn).

## config.toml [hooks] snippet (alternate placement)

If hooks are placed in `config.toml` instead of `hooks.json`, use the
double-bracket array-of-tables form. **Use either `hooks.json` OR this snippet,
not both.**

Target: `{workspace_root}/.codex/config.toml`

```toml
[[hooks.SessionStart]]
matcher = "startup|resume|clear|compact"

  [[hooks.SessionStart.hooks]]
  type = "command"
  command = 'bash "{WORKSPACE_ROOT}/.codex/hooks/on-session-start.sh"'
  commandWindows = 'powershell -NoProfile -ExecutionPolicy Bypass -File "{WORKSPACE_ROOT}/.codex/hooks/on-session-start.ps1"'
  timeout = 60
  statusMessage = "Li+ cold-start + rules injection"

[[hooks.UserPromptSubmit]]

  [[hooks.UserPromptSubmit.hooks]]
  type = "command"
  command = 'bash "{WORKSPACE_ROOT}/.codex/hooks/on-user-prompt.sh"'
  commandWindows = 'powershell -NoProfile -ExecutionPolicy Bypass -File "{WORKSPACE_ROOT}/.codex/hooks/on-user-prompt.ps1"'
  timeout = 30
  statusMessage = "Li+ Trigger Check Gate re-arm"

[[hooks.PostToolUse]]
matcher = "Bash"

  [[hooks.PostToolUse.hooks]]
  type = "command"
  command = 'bash "{WORKSPACE_ROOT}/.codex/hooks/post-tool-use.sh"'
  commandWindows = 'powershell -NoProfile -ExecutionPolicy Bypass -File "{WORKSPACE_ROOT}/.codex/hooks/post-tool-use.ps1"'
  timeout = 60
  statusMessage = "Li+ sub-issue refs auto-append"
```

## Hook script sources

Real files, copied verbatim into `{workspace_root}/.codex/hooks/` on bootstrap
(with `{LI_PLUS_TAG}` placeholder replaced by the resolved target tag). Each pair
is `.ps1` (Windows native, primary on the verified Codex Windows env) + `.sh`
(POSIX fallback):

- `adapter/codex/hooks/on-session-start.{ps1,sh}` — **rules injection** (reads
  `rules/**/*.md` from the clone, the Codex substitute for `.claude/rules/`) +
  update-status marker (`LI_PLUS_UPDATE_STATUS`) + diff-only Cold-start Synthesis
  material. State at `{workspace_root}/.codex/state/last-cold-start-emit.json`.
  On `resume` / `clear` / `compact`: rules re-injection + cold-start anchor only.
- `adapter/codex/hooks/on-user-prompt.{ps1,sh}` — per-turn Trigger Check Gate
  re-arm + webhook reminder (Character_Instance lives in AGENTS.md, not re-notified
  per turn).
- `adapter/codex/hooks/post-tool-use.{ps1,sh}` — sub-issue refs auto-append on
  `gh pr create`.

Each script carries a `# Source: ... ({LI_PLUS_TAG})` comment near the top as the
tag-tracking anchor. Bootstrap's tag-mismatch check reads this line.

## Codex contract differences vs Claude (load-bearing)

1. **JSON-only context injection.** Codex injects `additionalContext` only via the
   JSON envelope on **every** event including UserPromptSubmit. Claude accepts
   plain text on UserPromptSubmit stdout; Codex does not. All three Codex hooks
   emit the JSON envelope.
2. **No always-on rules folder.** Claude auto-loads `.claude/rules/**` (survives
   compaction). Codex has no equivalent, so SessionStart injects the rule bodies.
   The injection runs on every matcher (startup + resume/clear/compact) because
   re-injection per session boundary is the only always-on substrate Codex offers.
   `compact` survival of `additionalContext` is **unverified** in #1502 (Codex App
   has no manual `/compact`); re-injecting on `compact` is the safer-side default.
3. **GUI trust gate.** See the One-time GUI trust section above. No Claude analog.
4. **32 KiB AGENTS.md cap** (`project_doc_max_bytes`). The root AGENTS.md holds
   only the minimal always-present core (identity / character / startup contract);
   full rules go through the SessionStart injection, well past 32 KiB.

## mcp_tool webhook entry

The Claude template adds a sibling `type: "mcp_tool"` UserPromptSubmit entry that
calls `get_pending_status` on `github-webhook-mcp`. The Codex hooks schema documents
only `type: "command"` handlers. Therefore the Codex webhook intake stays on the
**poll** path: the `on-user-prompt` hook emits the reminder text and the AI calls
the MCP tool itself. `LI_PLUS_WEBHOOK_DELIVERY=channel` / `mcp_hook` suppress the
reminder, but a Codex host without an mcp_tool hook substrate falls back to `poll`
(see `adapter/codex/AGENTS.md` Optional Webhook Notification Flow).
