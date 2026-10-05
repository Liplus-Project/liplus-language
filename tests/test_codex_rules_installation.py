"""Fixtures for the installed mirror specified in Li+update.md 4x.1r."""

from pathlib import Path
import json
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from install_codex_rules import CHARACTER, InstallationBlocked, install


class RulesInstallationTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.source = self.base / "source/rules"
        self.workspace = self.base / "workspace"
        self.rules = self.workspace / ".codex/rules"
        self.config = self.workspace / ".codex/config.toml"
        self.config.parent.mkdir(parents=True)
        self.config.write_bytes(b'# keep\ndeveloper_instructions = "common\\n[Character_Instance]\\nNAME=Luna"\nmodel = "custom"\n')
        self.seed("evolution/cold-start-synthesis.md", b"anchor\n")
        self.seed("model/absolute.md", b"rule\n")
        self.seed(CHARACTER, b"default character\n")

    def seed(self, relative, content):
        path = self.source / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)

    def run_install(self, **kwargs):
        return install(self.source, self.workspace, self.config, "present", **kwargs)

    def snapshot(self):
        return {p.relative_to(self.workspace).as_posix(): p.read_bytes()
                for p in self.workspace.rglob("*") if p.is_file()}

    def test_read_only_then_install_omit_character_preserve_config_and_policy(self):
        self.rules.mkdir(parents=True)
        policy = self.rules / "default.rules"
        policy.write_bytes(b"user execution policy")
        custom = self.rules / "custom.md"
        custom.write_bytes(b"user rule")
        original = self.snapshot()
        self.assertFalse(self.run_install()["applied"])
        self.assertEqual(self.snapshot(), original)
        self.run_install(apply=True)
        self.assertFalse((self.rules / CHARACTER).exists())
        self.assertEqual((self.rules / "model/absolute.md").read_bytes(), b"rule\n")
        for name, content in original.items():
            self.assertEqual((self.workspace / name).read_bytes(), content)
        after = self.snapshot()
        self.run_install(apply=True)
        self.assertEqual(self.snapshot(), after)

    def test_update_and_stale_cleanup_only_touch_recorded_unmodified_files(self):
        self.run_install(apply=True)
        stale = self.rules / "model/absolute.md"
        user = self.rules / "model/user.md"
        user.write_bytes(b"custom")
        (self.source / "model/absolute.md").unlink()
        self.seed("task/new.md", b"new")
        result = self.run_install(apply=True)
        self.assertEqual(result["remove"], ["model/absolute.md"])
        self.assertFalse(stale.exists())
        self.assertEqual(user.read_bytes(), b"custom")
        backup = Path(result["backups"][0]) / "rules/model/absolute.md"
        self.assertEqual(backup.read_bytes(), b"rule\n")

    def test_unowned_and_modified_conflicts_stop_before_mutation(self):
        (self.rules / "model").mkdir(parents=True)
        path = self.rules / "model/absolute.md"
        path.write_bytes(b"user custom")
        before = self.snapshot()
        with self.assertRaises(InstallationBlocked):
            self.run_install(apply=True)
        self.assertEqual(self.snapshot(), before)
        path.write_bytes(b"rule\n")
        self.run_install(apply=True)
        path.write_bytes(b"modified")
        before = self.snapshot()
        with self.assertRaises(InstallationBlocked):
            self.run_install(apply=True)
        self.assertEqual(self.snapshot(), before)

    def test_old_character_copy_requires_native_readback_and_preserved_custom(self):
        (self.rules / "model").mkdir(parents=True)
        old = self.rules / CHARACTER
        old.write_bytes(b"default character\n")
        self.config.write_bytes(b'model = "keep"\n')
        before = self.snapshot()
        with self.assertRaises(InstallationBlocked):
            self.run_install(apply=True)
        self.assertEqual(self.snapshot(), before)
        result = self.run_install(apply=True, effective_instructions="[Character_Instance]\nNAME=Custom")
        self.assertFalse(old.exists())
        self.assertEqual((Path(result["backups"][0]) / "rules" / CHARACTER).read_bytes(), b"default character\n")
        old.write_bytes(b"custom old character")
        before = self.snapshot()
        with self.assertRaises(InstallationBlocked):
            self.run_install(apply=True, effective_instructions="[Character_Instance]\nNAME=Custom")
        self.assertEqual(self.snapshot(), before)

    def test_resolved_optout_can_install_without_config_mutation(self):
        self.config.write_bytes(b'developer_instructions = ""\n')
        original = self.config.read_bytes()
        install(self.source, self.workspace, self.config, "disabled", apply=True)
        self.assertEqual(self.config.read_bytes(), original)
        self.assertFalse((self.rules / CHARACTER).exists())

    def test_native_name_literal_without_bracket_marker_is_read_back(self):
        self.config.write_bytes(b'developer_instructions = "common\\nLUNA_CONTEXT:\\nNAME=Luna"\n')
        original = self.config.read_bytes()
        self.run_install(apply=True)
        self.assertEqual(self.config.read_bytes(), original)

    def test_unowned_custom_character_already_saved_in_native_can_be_retired(self):
        (self.rules / "model").mkdir(parents=True)
        old = self.rules / CHARACTER
        custom = b'---\nalwaysApply: true\n---\n<characters>\n# Characters\nNAME=Custom\nKeep custom wording\n</characters>\n'
        old.write_bytes(custom)
        original = self.config.read_bytes()
        result = self.run_install(apply=True, effective_instructions="common\n[Character_Instance]\nNAME=Custom\nKeep custom wording")
        self.assertFalse(old.exists())
        self.assertEqual(self.config.read_bytes(), original)
        self.assertEqual((Path(result["backups"][0]) / "rules" / CHARACTER).read_bytes(), custom)
        old.write_bytes(custom)
        manifest = self.workspace / ".codex/state/liplus-rules.json"
        record = json.loads(manifest.read_text())
        record["files"][CHARACTER] = "0" * 64
        manifest.write_text(json.dumps(record))
        self.run_install(apply=True, effective_instructions="[Character_Instance]\nNAME=Custom\nKeep custom wording")
        self.assertFalse(old.exists())

    def test_invalid_manifest_path_is_rejected(self):
        state = self.workspace / ".codex/state"
        state.mkdir()
        (state / "liplus-rules.json").write_text(json.dumps({"version": 1, "files": {"../config.toml": "0" * 64}}))
        with self.assertRaises(InstallationBlocked):
            self.run_install(apply=True)

    def test_failed_rule_save_restores_prior_bytes(self):
        self.run_install(apply=True)
        before = self.snapshot()
        self.seed("evolution/cold-start-synthesis.md", b"new anchor")
        self.seed("model/absolute.md", b"new rule")
        real_write = Path.write_bytes
        def fail(path, content):
            if path == self.rules / "model/absolute.md" and content == b"new rule":
                raise OSError("fixture failure")
            return real_write(path, content)
        with patch.object(Path, "write_bytes", fail):
            with self.assertRaises(OSError):
                self.run_install(apply=True)
        for name, content in before.items():
            self.assertEqual((self.workspace / name).read_bytes(), content)


if __name__ == "__main__":
    unittest.main()
