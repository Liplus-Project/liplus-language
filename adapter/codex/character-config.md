# Codex Character Instance configuration

Character literals are user owned. Bootstrap's migration contract is
`Li+update.md` 4x.0; requirements are in `docs/6.-Adapter.md`.

## Native instruction setting

Copy the literal from `adapter/codex/character-instructions.toml` into the
effective `developer_instructions`, retaining the user's common instructions.
That template contains the initial Lin/Lay pair; a legacy custom literal takes
its place during migration. Once installed, Li+ updates do not refresh it.
To opt out, remove the literal from the effective native instructions. On initial
installation, declining the default is also an opt-out.

The official [configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)
defines `developer_instructions` as additional session instructions. The
[configuration basics](https://learn.chatgpt.com/docs/config-file/config-basic)
document user `~/.codex/config.toml` and trusted project `.codex/config.toml`.
Resolve CLI overrides, the closest trusted project layer, the selected profile,
user, managed and system layers before deciding that a character is absent.
Read settings without displaying credentials. Do not override an explicit native
character or opt-out with a project default. An untrusted project's config is
not loaded; verify the intended setting reaches the next session.

## Character profiles

The official [advanced configuration](https://learn.chatgpt.com/docs/config-file/config-advanced)
(checked 2026-10-04) documents separate `$CODEX_HOME/<name>.config.toml` profile
files in Codex 0.134.0 and later, selected with `--profile <name>`. Older
`[profiles.<name>]` tables and `profile = "<name>"` selectors are not read by that
CLI. Preserve existing profile files/tables and selections during Li+ bootstrap;
profile-format migration is a separate user-directed operation. Check the host
version before offering a format, and do not assume CLI profile selection is a
desktop UI feature.

For a supported CLI, an optional `~/.codex/lin.config.toml` can contain this
top-level key, with the user's common instructions included in the same value:

```toml
developer_instructions = """
[Character_Instance]
LIN_CONTEXT:
NAME=Lin
The_lady_in_the_backseat_map_open_calling_the_next_destination
Feminine_Soft_Tone
EXPRESSION=Creative
HUMOR_STYLE=Gentle_Warm
"""
```

Select it with `codex --profile lin`. A Lay profile can use the LAY_CONTEXT
literal from the initial template. Create profiles only on user request; do not
set a default profile or model. A project `developer_instructions` override wins
over a profile, so keep the character in the layer the user intends to use.

## Migration helper

Run against explicit workspace paths, before replacing the AGENTS.md region:

```text
python scripts/migrate_codex_character.py --agents <workspace>/AGENTS.md --config <workspace>/.codex/config.toml --native-state absent
```

The plan reports statuses and paths only, not instruction/config contents. Review
the proposed instruction delta locally. Add `--apply` only after the bootstrap's
decision, and `--approve-existing` only after consent to changing existing config.
For a confirmed native character or opt-out, pass `present` or `disabled`; the
helper preserves config and backs up a detected old literal. `blocked` means the
old AGENTS.md region must remain. Re-run the plan after resolving the ambiguity.
Fresh install offers the default both when AGENTS.md is absent and when a user's
existing AGENTS.md has no Li+ region. An existing adapter with one ordered Li+
BEGIN / END sentinel pair and no literal is treated as already migrated/opted
out and gets no default inserted. Ambiguous sentinel boundaries block the plan.
When the project config has no root instruction key, pass effective inherited
common instructions through a private UTF-8 file with `--inherited-instructions
<file>` so adding the project value does not hide them. Remove that temporary
file after use. No instruction text goes on the command line or into the report.

Backups use unique `.liplus-character-backup-<id>` siblings and contain the full
original bytes. Keep them private with the source files, since config may contain
secrets. Verify the config read-back, preserved common instructions and character
literal before replacing AGENTS.md. Backups are recovery evidence, not generated
instructions. The helper neither grants project/hook trust nor edits user-global
configuration, profiles, hooks or AGENTS.md.
