# Codex project output styles

Requirements: `docs/6.-Adapter.md`; bootstrap: `Li+update.md` 4x.0s / 4x.3.
The user owns `.codex/output-styles/<name>.md` under the trusted project root.
Normal Codex App/CLI reads only that project's `.codex/config.toml` selection:

```toml
[liplus]
output_style = "character_instance"
```

Absent selection plus an existing `.codex/output-styles` directory selects
`character_instance`. A missing default file fails explicitly. Only absence of
both selection and directory is `legacy` (existing inline compatibility).
`false` disables the default persona; empty string, true and other types fail.
Global/profile common `developer_instructions` remain native. The hook cannot
observe effective profiles/CLI overrides; this project selector does not promise
to track them. Before file mode, resolve overlapping inline personas in the
effective native configuration. Do not silently edit unrelated profiles/global
settings. When removing the only project inline persona, keep its instruction
key as an empty string to preserve native override behavior.

A nonempty process-local `LI_PLUS_OUTPUT_STYLE` overrides the project selection,
including false. Pullcept sets only this stem, not a body, for its account. One
selected body replaces the default body; it is not appended to it. Empty override
uses project selection. CLI `--style` takes precedence over the environment.
No H1/persona name in the body is used as a selector. Luna is not a distributed
default. Lin/Lay remains the initial opt-in template in
`adapter/codex/character-instructions.toml` for the legacy bootstrap path.

## Artifact bytes and frontmatter

Stems are case-sensitive ASCII `[A-Za-z0-9][A-Za-z0-9_-]{0,127}`. Paths, drive
names, separators and dotdot are rejected. Config, cwd and styles must stay inside
the canonical project boundaries; a style link must also stay inside the canonical
`.codex/output-styles` directory. Junctions/symlinks escaping them fail.

UTF-8 with optional BOM and LF/CRLF is supported. The BOM and a frontmatter block
starting with a standalone first line `---` and ending with a standalone `---`
are removed; the remaining body bytes are retained exactly. A frontmatter `name`
is optional. When present, one unindented `name: stem`, `name: "stem"`, or
`name: 'stem'` line must match the selected stem. Quoting is literal; escapes,
comments, multiline scalars, complex YAML and duplicate/indented name entries
are unsupported and fail. This is not a general YAML parser. Shared Claude styles
are generated with name equal to the stem, description, and
`keep-coding-instructions: true`.

Missing files, invalid UTF-8, unclosed frontmatter, whitespace-only bodies,
artifacts over 128 KiB and handler UTF-8 JSON outputs over 128 KiB fail. JSON
escaping/envelope overhead can make the handler limit stricter than the artifact
limit. No invalid file mode falls back to inline instructions.

## Installed helper and resolve protocol (version 1)

Python >=3.11 (`tomllib`) is required. Copy `scripts/codex_output_style.py`
byte-faithfully to `.codex/hooks/codex-output-style.py`. The helper verifies its
installed hooks/.codex location, derives its own canonical root and requires it
to equal `--root`. Both modes verify canonical cwd containment. The caller gets
the root from the host's native trusted project layer, not from an arbitrary
repository marker or an environment variable. A helper/metadata existing does
not prove native hook trust; Pullcept must also verify the native trusted handler
registration against `adapter/codex/hooks-config.md`.

```text
python <installed-helper> resolve --cwd <effective-cwd> --root <native-trusted-project-root> [--style <account-stem>]
```

Success: exit 0, exactly one UTF-8 JSON line (no body or config literals):

```json
{"protocol_version":1,"mode":"file","name":"character_instance","root":"/project","sha256":"<body-sha256>","byte_count":123,"handler":{"path":"/project/.codex/hooks/codex-output-style.py","sha256":"<helper-sha256>","additional_context_limit":0,"matchers":["startup","resume","clear","compact"]}}
```

`root`/handler `path` are canonical absolute paths. `sha256` hashes exactly the
UTF-8 body after BOM/frontmatter removal, `byte_count` counts those bytes.
`mode` is file, disabled or legacy. Disabled/legacy return name/sha256 null,
byte_count 0 and the same handler metadata. Handler hash covers the installed
helper bytes. Resolver performs no mutation and loads no model.

Failure: exit 1, exactly one secret-free JSON line:

```json
{"protocol_version":1,"status":"blocked","reason":"invalid_selection"}
```

Reason codes are `invalid_selection`, `outside_project`, `invalid_project`,
`helper_root_mismatch`, `missing_style`, `unclosed_frontmatter`,
`ambiguous_frontmatter_name`, `frontmatter_name_mismatch`, `empty_style`,
`style_oversize`, `handler_oversize`, `missing_cwd`, `invalid_hook_input` and
`invalid_style_or_project` (I/O, TOML/UTF-8 and other parse failures).
Do not disclose parser exception text, config/body literals or secrets.

## Hook delivery

```text
python <installed-helper> hook --root <project-root>
```

Hook mode reads normal SessionStart JSON stdin (cwd, source, hook_event_name).
Only startup/resume/clear/compact sources are accepted. Its independent handler
uses `additionalContextLimit: 0` and timeout 30; the existing rules handler limit
and other event/product handlers remain unchanged. Success returns
`hookSpecificOutput.hookEventName: SessionStart` and `additionalContext` equal to
the full selected body; disabled/legacy context is empty. Failure returns
`continue:false`, a secret-free stopReason and exit 1 without partial context.
Changed hook bytes need native GUI trust again. Do not bypass trust or edit hashes.

## Explicit one-time migration

Prepare a private UTF-8 body-only file containing the approved exact persona slice
from the root native developer_instructions value. Review its unique boundaries
locally; do not print it or place its contents in argv/environment.

```text
python scripts/migrate_codex_output_style.py --workspace <project> --name character_instance --persona-file <private-body-file>
```

Read-only by default; `--apply --approve-existing` records the already-approved
explicit migration. It creates the style and edits only the local project config,
preserving common instructions, unrelated/MCP/model/profile values, BOM and
newline form. The persona slice must occur exactly once in a root instruction
value. Ambiguous TOML/boundaries stop. Existing user styles are protected.
Backups are unique byte-faithful `.liplus-character-backup-<id>` siblings and must
remain private because originals may contain secrets. Recheck all inputs before
saving, verify TOML/body read-back and restore touched files on failure. A completed
second application is a no-op. The temporary approved body file must be removed
after use; helpers do not delete it automatically.

For an explicitly approved local standalone profile, `--remove <local-config>
<private-exact-body-file>` selects the native value to remove; repeat this pair
only for individually approved local configs. Sources are direct `.codex/*.toml`
files in this project, not global files. To export an additional account artifact
while preserving the project selector, use `--preserve-selection` together with
that local profile removal. This option is not a scan of other profiles. Inspect
current native effective instructions again before choosing a profile/CLI override.

With explicit `--use-existing-style`, activate an existing validated artifact
without changing any of its bytes, even if it differs from the old approved
inline persona. Back up and remove only the approved inline slice; retain common
instructions. This is an activation decision, not permission to overwrite a style.

Updater and rules installer validate file/disabled mode before the legacy native
bootstrap; they do not regenerate styles or re-add inline personas. The legacy
`scripts/migrate_codex_character.py` remains for projects without a style directory
or selector. It checks old AGENTS sentinel boundaries, saves a unique old literal
with private backups and preserves already-effective native/opt-out settings.
Inherited common instructions travel only via its private `--inherited-instructions`
file. Rules installer omits `rules/model/character_Instance.md` and never edits
config; a custom old rule must be preserved in the selected body before retirement.

Claude sharing is a separate environment migration: protect existing
`.claude/output-styles` contents, link the selected artifact and select its stem
through Claude's outputStyle. Source tests do not grant hook trust or prove a real
CLI/Pullcept session. Report those external checks separately until completed.
