"""Fixture coverage of Li+update.md 4x.0 saving, not host instruction injection."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import tomllib
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from migrate_codex_character import (  # noqa: E402
    BANNER, MigrationBlocked, migrate, plan_migration,
)


CUSTOM = '[Character_Instance]\nCUSTOM_CONTEXT:\nNAME=Aria\nKeep my 日本語 and "quotes".\nEXPRESSION=Quiet'


def legacy(body: str = CUSTOM, newline: str = "\n") -> bytes:
    return ("User prefix\n# --- Li+ BEGIN (build-old) ---\nRules\n"
            + BANNER + "\n\n" + body + "\n" + BANNER + "\n\n"
            + BANNER + "\nResponsibilities\n" + BANNER
            + "\nOther rules\n# --- Li+ END ---\nUser suffix\n").replace("\n", newline).encode()


def instructions(config: bytes) -> str:
    return tomllib.loads(config.decode("utf-8-sig"))["developer_instructions"]


class CodexCharacterPlanTest(unittest.TestCase):
    def test_fresh_default_is_lin_lay_without_luna(self) -> None:
        plan = plan_migration(None, None, "absent")
        self.assertEqual(plan.status, "install-default")
        value = instructions(plan.config)
        self.assertIn("NAME=Lin", value)
        self.assertIn("NAME=Lay", value)
        self.assertNotIn("Luna", value)

    def test_legacy_custom_replaces_default_and_preserves_content(self) -> None:
        for newline in ("\n", "\r\n"):
            with self.subTest(newline=newline):
                plan = plan_migration(legacy(newline=newline), None, "absent")
                self.assertEqual(instructions(plan.config), CUSTOM.replace("\n", newline))
                self.assertNotIn("NAME=Lin", instructions(plan.config))

    def test_existing_user_agents_without_adapter_offers_initial_pair(self) -> None:
        agents = "# Workspace\nKeep the user's 日本語 instructions.\n".encode()
        plan = plan_migration(agents, None, "absent")
        self.assertEqual(plan.status, "install-default")
        self.assertEqual(plan.config, plan_migration(None, None, "absent").config)
        for state in ("present", "disabled"):
            with self.subTest(state=state):
                self.assertEqual(plan_migration(agents, None, state).config, b"")

    def test_literal_free_adapter_with_ambiguous_sentinels_blocks_native_choices(self) -> None:
        adapter = (ROOT / "adapter/codex/AGENTS.md").read_bytes()
        begin = b"# --- Li+ BEGIN ({LI_PLUS_TAG}) ---"
        end = b"# --- Li+ END ---"
        native = ('developer_instructions = ' + json.dumps(CUSTOM) + "\n").encode()
        for agents in (adapter.replace(end, b""), adapter.replace(begin, b""),
                       adapter + b"\n" + end, adapter + b"\n" + begin,
                       end + b"\n" + begin,
                       adapter.replace(begin, b"# --- Li+ BEGIN malformed ---")):
            for state, config, inherited in (("absent", None, ""),
                                             ("present", b"model = 'keep'\n", ""),
                                             ("disabled", b"model = 'keep'\n", ""),
                                             ("absent", b'developer_instructions = ""\n', ""),
                                             ("absent", native, ""),
                                             ("absent", b"model = 'keep'\n", CUSTOM)):
                with self.subTest(agents=agents, state=state, config=config, inherited=inherited):
                    with self.assertRaises(MigrationBlocked):
                        plan_migration(agents, config, state, inherited)

    def test_common_instructions_and_unrelated_config_bytes_survive(self) -> None:
        for common in ('"common \\"quote\\""', "'''common\nmultiline'''", '"""common\nmultiline"""'):
            old = ("# user header\n'developer_instructions' = " + common
                   + " # user annotation\nmodel = 'custom'\nprofile = 'user-choice'\n"
                   + "[profiles.user-choice]\ndeveloper_instructions = 'inactive profile'\n"
                   + "[mcp_servers.private]\ncommand = 'keep'\n").encode()
            with self.subTest(common=common):
                plan = plan_migration(legacy(), old, "absent")
                self.assertEqual(instructions(plan.config), instructions(old) + "\n\n" + CUSTOM)
                self.assertTrue(plan.config.startswith(b"# user header\n'developer_instructions' = "))
                self.assertEqual(plan.config.split(b" # user annotation", 1)[1],
                                 old.split(b" # user annotation", 1)[1])
                before, after = tomllib.loads(old.decode()), tomllib.loads(plan.config.decode())
                before.pop("developer_instructions")
                after.pop("developer_instructions")
                self.assertEqual(after, before)

    def test_root_key_inserted_before_tables_without_reformatting(self) -> None:
        old = b"\xef\xbb\xbf# custom\r\n[features]\r\nx = true\r\n"
        plan = plan_migration(legacy(), old, "absent")
        self.assertTrue(plan.config.startswith(b"\xef\xbb\xbfdeveloper_instructions = "))
        self.assertTrue(plan.config.endswith(old[3:]))
        self.assertEqual(instructions(plan.config), CUSTOM)

    def test_inherited_common_instructions_not_hidden_by_project_value(self) -> None:
        old = b"[features]\nx = true\n"
        plan = plan_migration(legacy(), old, "absent", "inherited common 日本語")
        self.assertEqual(instructions(plan.config), "inherited common 日本語\n\n" + CUSTOM)
        self.assertTrue(plan.config.endswith(old))

    def test_explicit_native_character_and_opt_out_win(self) -> None:
        native = ('developer_instructions = ' + json.dumps(CUSTOM) + "\n").encode()
        for state, old in (("present", native), ("absent", native),
                           ("disabled", b"model = 'keep'\n"),
                           ("absent", b'developer_instructions = ""\n')):
            with self.subTest(state=state, old=old):
                self.assertEqual(plan_migration(legacy(), old, state).config, old)
                adapter = (ROOT / "adapter/codex/AGENTS.md").read_bytes()
                self.assertEqual(plan_migration(adapter, old, state).config, old)

    def test_inherited_native_literal_is_preserved_without_project_override(self) -> None:
        old = b"model = 'keep'\n"
        self.assertEqual(plan_migration(legacy(), old, "absent", CUSTOM).config, old)

    def test_repeated_save_and_reupdate_do_not_duplicate_or_reintroduce(self) -> None:
        first = plan_migration(legacy(), None, "absent")
        self.assertEqual(plan_migration(legacy(), first.config, "absent").config, first.config)
        adapter = (ROOT / "adapter/codex/AGENTS.md").read_bytes()
        self.assertEqual(plan_migration(adapter, first.config, "present").config, first.config)
        self.assertEqual(plan_migration(adapter, None, "absent").config, b"")

    def test_ambiguous_boundaries_stop_before_replacement(self) -> None:
        for old in (CUSTOM.encode(), legacy() + CUSTOM.encode(),
                    legacy().replace(b"Responsibilities", b"Unknown heading"),
                    legacy().replace(b"NAME=Aria", b"unknown"),
                    legacy().replace(b"[Character_Instance]", b"[Character_Instance] # edited"),
                    legacy().replace(b"[Character_Instance]", b""),
                    legacy() + b"# --- Li+ END ---\n"):
            with self.subTest(old=old):
                with self.assertRaises(MigrationBlocked):
                    plan_migration(old, None, "absent")

    def test_invalid_toml_and_unresolved_state_are_rejected(self) -> None:
        for config, state in ((b"developer_instructions = 3", "absent"),
                              (b"invalid =", "present"),
                              (b"\xff", "absent"), (b"", "unknown")):
            with self.subTest(config=config, state=state):
                with self.assertRaises(ValueError):
                    plan_migration(legacy(), config, state)


class CodexCharacterSaveTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.agents = self.directory / "AGENTS.md"
        self.config = self.directory / ".codex/config.toml"

    def test_read_only_plan_has_no_side_effects(self) -> None:
        self.agents.write_bytes(legacy())
        result = migrate(self.agents, self.config, "absent")
        self.assertFalse(result["applied"])
        self.assertEqual(list(self.directory.iterdir()), [self.agents])

    def test_ambiguous_adapter_blocks_apply_without_changing_native_or_opt_out(self) -> None:
        agents = (ROOT / "adapter/codex/AGENTS.md").read_bytes().replace(b"# --- Li+ END ---", b"")
        self.agents.write_bytes(agents)
        self.config.parent.mkdir()
        for state, config in (("present", b"model = 'keep'\n"),
                              ("disabled", b"model = 'keep'\n"),
                              ("absent", b'developer_instructions = ""\n')):
            with self.subTest(state=state, config=config):
                self.config.write_bytes(config)
                with self.assertRaises(MigrationBlocked):
                    migrate(self.agents, self.config, state, apply=True, approve_existing=True)
                self.assertEqual(self.agents.read_bytes(), agents)
                self.assertEqual(self.config.read_bytes(), config)
                self.assertEqual(list(self.directory.rglob("*.liplus-character-backup-*")), [])

    def test_default_install_and_update_preserve_exact_config(self) -> None:
        migrate(self.agents, self.config, "absent", apply=True)
        first = self.config.read_bytes()
        self.agents.write_bytes((ROOT / "adapter/codex/AGENTS.md").read_bytes())
        result = migrate(self.agents, self.config, "present", apply=True)
        self.assertEqual(self.config.read_bytes(), first)
        self.assertEqual(result["backups"], [])

    def test_existing_config_requires_consent_and_backups_are_exact(self) -> None:
        self.agents.write_bytes(legacy())
        self.config.parent.mkdir()
        before = b'# private\ndeveloper_instructions = "common" # preserve\nmodel = "keep"\n'
        self.config.write_bytes(before)
        with self.assertRaises(MigrationBlocked):
            migrate(self.agents, self.config, "absent", apply=True)
        self.assertEqual(self.config.read_bytes(), before)
        self.assertEqual(list(self.directory.glob("*.liplus-character-backup-*")), [])
        result = migrate(self.agents, self.config, "absent", apply=True, approve_existing=True)
        backups = [Path(p).read_bytes() for p in result["backups"]]
        self.assertEqual(backups, [legacy(), before])
        self.assertEqual(self.agents.read_bytes(), legacy())
        self.assertEqual(instructions(self.config.read_bytes()), "common\n\n" + CUSTOM)

    def test_first_install_with_user_agents_preserves_common_config_and_opt_out(self) -> None:
        agents = b"# User workspace\nUse small commits.\n"
        old = b'developer_instructions = "common"\nmodel = "keep"\n'
        self.agents.write_bytes(agents)
        self.config.parent.mkdir()
        self.config.write_bytes(old)
        plan = migrate(self.agents, self.config, "absent")
        self.assertEqual(plan["status"], "install-default")
        self.assertFalse(plan["applied"])
        self.assertEqual(migrate(self.agents, self.config, "disabled", apply=True)["backups"], [])
        self.assertEqual(self.config.read_bytes(), old)
        with self.assertRaises(MigrationBlocked):
            migrate(self.agents, self.config, "absent", apply=True)
        result = migrate(self.agents, self.config, "absent", apply=True, approve_existing=True)
        saved = self.config.read_bytes()
        self.assertTrue(instructions(saved).startswith("common\n\n[Character_Instance]"))
        self.assertIn("NAME=Lin", instructions(saved))
        self.assertIn("NAME=Lay", instructions(saved))
        self.assertTrue(saved.endswith(b'\nmodel = "keep"\n'))
        self.assertEqual(self.agents.read_bytes(), agents)
        self.assertEqual([Path(p).read_bytes() for p in result["backups"]], [agents, old])
        self.assertEqual(migrate(self.agents, self.config, "absent")["config_change"], False)

    def test_native_wins_but_legacy_is_backed_up_before_adapter_replacement(self) -> None:
        self.agents.write_bytes(legacy())
        result = migrate(self.agents, self.config, "present", apply=True)
        self.assertFalse(self.config.exists())
        self.assertEqual([Path(p).read_bytes() for p in result["backups"]], [legacy()])

    def test_save_then_proxy_tag_updates_keep_custom_and_outside_bytes(self) -> None:
        from test_adapter_update_contract import apply_adapter_update

        self.agents.write_bytes(legacy())
        migrate(self.agents, self.config, "absent", apply=True)
        saved = self.config.read_bytes()
        for tag in (b"build-next", b"build-later"):
            source = (ROOT / "adapter/codex/AGENTS.md").read_bytes().replace(b"{LI_PLUS_TAG}", tag)
            self.agents.write_bytes(apply_adapter_update(self.agents.read_bytes(), source))
            migrate(self.agents, self.config, "present", apply=True)
            self.assertEqual(self.config.read_bytes(), saved)
            self.assertEqual(instructions(saved), CUSTOM)
            self.assertTrue(self.agents.read_bytes().startswith(b"User prefix\n"))
            self.assertTrue(self.agents.read_bytes().endswith(b"\nUser suffix\n"))
            self.assertNotIn(b"[Character_Instance]", self.agents.read_bytes())

    def test_write_failure_restores_old_config_and_keeps_old_agents(self) -> None:
        self.agents.write_bytes(legacy())
        self.config.parent.mkdir()
        old = b'developer_instructions = "common"\n'
        self.config.write_bytes(old)
        write = Path.write_bytes
        failed = False

        def failing_write(path: Path, data: bytes) -> int:
            nonlocal failed
            if path == self.config and not failed:
                failed = True
                write(path, b"partial")
                raise OSError("fixture write failure")
            return write(path, data)

        with patch.object(Path, "write_bytes", failing_write):
            with self.assertRaises(OSError):
                migrate(self.agents, self.config, "absent", apply=True, approve_existing=True)
        self.assertEqual(self.config.read_bytes(), old)
        self.assertEqual(self.agents.read_bytes(), legacy())

    def test_blocked_cli_does_not_disclose_config_or_character(self) -> None:
        self.agents.write_bytes(CUSTOM.encode())
        self.config.parent.mkdir()
        self.config.write_bytes(b"private_secret = 'secret fixture'\n")
        result = subprocess.run([sys.executable, str(ROOT / "scripts/migrate_codex_character.py"),
                                 "--agents", str(self.agents), "--config", str(self.config),
                                 "--native-state", "absent", "--apply"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["status"], "blocked")
        self.assertNotIn("secret fixture", result.stdout + result.stderr)
        self.assertNotIn("Aria", result.stdout + result.stderr)

    def test_updated_adapter_has_no_literal_or_configuration_pointer(self) -> None:
        adapter = (ROOT / "adapter/codex/AGENTS.md").read_text(encoding="utf-8")
        self.assertNotIn("[Character_Instance]", adapter)
        self.assertNotIn("LIN_CONTEXT:", adapter)
        self.assertNotIn("LAY_CONTEXT:", adapter)
        self.assertNotIn("character-config", adapter)
        self.assertNotIn("character-instructions", adapter)
        self.assertNotIn("developer_instructions", adapter)
        self.assertNotIn(".codex/config.toml", adapter)


if __name__ == "__main__":
    unittest.main()
