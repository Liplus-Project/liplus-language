"""Fixtures for docs/6.-Adapter.md and adapter/codex/character-config.md."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from codex_output_style import LIMIT, MATCHERS, StyleBlocked, body_bytes, digest, load
from install_codex_output_style import install as install_handler
from install_codex_rules import install as install_rules
from migrate_codex_character import MigrationBlocked, migrate as migrate_legacy
from migrate_codex_output_style import migrate


class BaseStyleFixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "project with spaces 雪"
        self.root.mkdir()
        self.config = self.root / ".codex/config.toml"
        self.config.parent.mkdir()
        self.config.write_bytes(b'# keep\ndeveloper_instructions = "common"\nmodel = "custom"\n')
        self.styles = self.root / ".codex/output-styles"
        self.helper = self.root / ".codex/hooks/codex-output-style.py"
        self.helper.parent.mkdir()
        shutil.copyfile(ROOT / "scripts/codex_output_style.py", self.helper)
        self.body = "# character_Instance\r\nNAME=Example\r\n日本語 café 雪\r\n".encode()
        self.env = dict(os.environ, LI_PLUS_OUTPUT_STYLE="")

    def write_style(self, name="character_instance", body=None, front=b""):
        self.styles.mkdir(exist_ok=True)
        path = self.styles / (name + ".md")
        path.write_bytes(front + (self.body if body is None else body))
        return path

    def select(self, value):
        self.config.write_text('[liplus]\noutput_style = ' + value + '\n', encoding="utf-8")

    def cli(self, *args, event=None, environment=None, root=None):
        return subprocess.run([sys.executable, str(self.helper), *args, "--root", str(root or self.root)],
                              input=json.dumps(event, ensure_ascii=False).encode() if event else None,
                              capture_output=True, env=environment or self.env)

class StyleFixture(BaseStyleFixture):
    def test_legacy_default_disable_override_and_no_double_body(self):
        self.assertEqual(load(self.root, self.root, environment=False)[0]["mode"], "legacy")
        self.write_style()
        meta, body = load(self.root, self.root, environment=False)
        self.assertEqual((meta["name"], body), ("character_instance", self.body))
        self.assertEqual((meta["sha256"], meta["byte_count"]), (digest(self.body), len(self.body)))
        account = b"# Different H1\nNAME=Account\n"
        self.write_style("character_codex_luna", account)
        self.select("false")
        self.assertEqual(load(self.root, self.root, environment=False)[0]["mode"], "disabled")
        env = dict(self.env, LI_PLUS_OUTPUT_STYLE="character_codex_luna")
        for matcher in MATCHERS:
            result = self.cli("hook", event={"cwd": str(self.root), "source": matcher,
                             "hook_event_name": "SessionStart"}, environment=env)
            self.assertEqual(result.returncode, 0, result.stderr)
            context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
            self.assertEqual(context.encode(), account)
            self.assertNotIn(self.body.decode(), context)

    def test_default_missing_and_invalid_types_fail_without_inline_fallback(self):
        self.styles.mkdir()
        with self.assertRaises(StyleBlocked):
            load(self.root, self.root, environment=False)
        failed_hook = self.cli("hook", event={"cwd": str(self.root), "source": "startup", "hook_event_name": "SessionStart"})
        self.assertEqual(failed_hook.returncode, 0)
        self.assertFalse(json.loads(failed_hook.stdout)["continue"])
        self.assertNotIn("hookSpecificOutput", json.loads(failed_hook.stdout))
        self.assertEqual(self.cli("resolve", "--cwd", str(self.root)).returncode, 1)
        for value in ('""', "true", "42", '[]', '{}', '"../secret"', '"C:drive"', '"a/b"', '"a\\\\b"'):
            with self.subTest(value=value):
                self.select(value)
                with self.assertRaises(ValueError):
                    load(self.root, self.root, environment=False)

    def test_bom_crlf_frontmatter_and_h1_are_preserved(self):
        for scalar in (b"character_instance", b'"character_instance"', b"'character_instance'"):
            artifact = b"\xef\xbb\xbf---\r\nname: " + scalar + b"\r\nkeep-coding-instructions: true\r\n---\r\n" + self.body
            self.assertEqual(body_bytes(artifact, "character_instance"), self.body)
        self.assertEqual(body_bytes(b"---\ndescription: fixture\n---\n" + self.body,
                                    "character_instance"), self.body)

    def test_bad_frontmatter_utf8_empty_and_caps(self):
        values = [b"\xff", b" \r\n", b"---\nname: character_instance\n",
                  b"---\nname: other\n---\nbody", b'---\nname: "character_instance\\n"\n---\nbody',
                  b"---\nname: character_instance\nname: character_instance\n---\nbody",
                  b"---\n name: other\n---\nbody", b'---\n"name": other\n---\nbody',
                  b"---\nname : other\n---\nbody", b"x" * (LIMIT + 1),
                  b"\t" * (LIMIT // 2) + b"body"]
        for value in values:
            with self.subTest(prefix=value[:70], size=len(value)):
                with self.assertRaises((ValueError, UnicodeError)):
                    body_bytes(value, "character_instance")
        self.assertEqual(len(body_bytes(b"x" * (LIMIT - 100), "character_instance")), LIMIT - 100)

    def test_real_entry_spelling_is_case_sensitive_without_name_metadata(self):
        self.write_style("CaseStyle")
        self.select('"casestyle"')
        with self.assertRaises(StyleBlocked):
            load(self.root, self.root, environment=False)
        self.select('"CaseStyle"')
        self.assertEqual(load(self.root, self.root, environment=False)[1], self.body)

    def test_containment_and_installed_root_check(self):
        self.write_style()
        outside = self.root.parent / "outside"
        outside.mkdir()
        with self.assertRaises(StyleBlocked):
            load(outside, self.root, environment=False)
        result = self.cli("resolve", "--cwd", str(outside))
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["reason"], "outside_project")
        result = self.cli("resolve", "--cwd", str(outside), root=outside)
        self.assertEqual(json.loads(result.stdout)["reason"], "helper_root_mismatch")

    def test_symlink_and_windows_junction_cannot_escape(self):
        self.write_style()
        outside = self.root.parent / "outside"
        outside.mkdir()
        target = outside / "linked.md"
        target.write_bytes(self.body)
        link = self.styles / "linked.md"
        try:
            link.symlink_to(target)
        except OSError:
            if os.name != "nt":
                self.skipTest("Symlink creation unavailable")
            linked_dir = self.styles / "escape"
            command = f'New-Item -ItemType Junction -Path "{linked_dir}" -Target "{outside}" | Out-Null'
            made = subprocess.run(["powershell", "-NoProfile", "-Command", command], capture_output=True)
            self.assertEqual(made.returncode, 0, made.stderr)
            with self.assertRaises(StyleBlocked):
                from codex_output_style import contained
                contained(linked_dir, self.styles.resolve())
            linked_dir.rmdir()
        else:
            self.select('"linked"')
            with self.assertRaises(StyleBlocked):
                load(self.root, self.root, environment=False)

    def test_resolve_is_one_line_body_free_and_hook_errors_are_secret_free(self):
        self.write_style()
        result = self.cli("resolve", "--cwd", str(self.root))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(result.stdout.splitlines()), 1)
        metadata = json.loads(result.stdout)
        self.assertEqual(metadata["protocol_version"], 1)
        self.assertEqual(metadata["handler"]["path"], str(self.helper.resolve()))
        self.assertEqual(metadata["handler"]["sha256"], digest(self.helper.read_bytes()))
        self.assertNotIn("additionalContext", result.stdout.decode())
        self.assertNotIn("NAME=Example", result.stdout.decode())
        self.config.write_bytes(b'private_secret = "secret fixture"\n[liplus]\noutput_style = 42\n')
        result = self.cli("hook", event={"cwd": str(self.root), "source": "startup", "hook_event_name": "SessionStart"})
        self.assertEqual(result.returncode, 0)
        parsed_control = json.loads(result.stdout) if result.returncode == 0 else {}
        self.assertFalse(parsed_control["continue"])
        self.assertNotIn(b"secret fixture", result.stdout + result.stderr)
        self.assertNotIn(b"NAME=Example", result.stdout + result.stderr)
        resolved = self.cli("resolve", "--cwd", str(self.root))
        self.assertEqual(resolved.returncode, 1)
        self.assertEqual(json.loads(resolved.stdout)["status"], "blocked")

    def test_full_large_body_delivery_and_legacy_disabled_empty_context(self):
        for mode in ("legacy", "disabled"):
            if mode == "disabled":
                self.select("false")
            result = self.cli("hook", event={"cwd": str(self.root), "source": "resume", "hook_event_name": "SessionStart"})
            self.assertEqual(json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"], "")
        body = ("日本語雪\r\n" * 4000).encode()
        self.write_style(body=body)
        self.select('"character_instance"')
        result = self.cli("hook", event={"cwd": str(self.root), "source": "resume", "hook_event_name": "SessionStart"})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"].encode(), body)

    def test_python_utf8_delivery_through_windows_powershell_51_all_matchers(self):
        if os.name != "nt" or not shutil.which("powershell"):
            self.skipTest("Windows PowerShell 5.1 fixture")
        self.write_style()
        command = '& "' + sys.executable + '" "' + str(self.helper) + '" hook --root "' + str(self.root) + '"'
        for matcher in MATCHERS:
            result = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", command],
                                    input=json.dumps({"cwd": str(self.root), "source": matcher,
                                         "hook_event_name": "SessionStart"}).encode(), capture_output=True, env=self.env)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"].encode(), self.body)


class MigrationFixture(BaseStyleFixture):
    def prepare(self):
        self.persona = self.root / "approved-private.txt"
        self.persona.write_bytes(self.body)
        original = ('\ufeff# 日本語\r\ndeveloper_instructions = ' + json.dumps("common\n" + self.body.decode(), ensure_ascii=False)
                    + '\r\nmodel = "custom"\r\n[mcp_servers.fixture]\r\ncommand = "keep"\r\n').encode()
        self.config.write_bytes(original)
        return original

    def test_plan_apply_exact_backups_common_settings_and_second_noop(self):
        original = self.prepare()
        self.assertFalse(migrate(self.root, "character_instance", self.persona)["applied"])
        self.assertEqual(self.config.read_bytes(), original)
        with self.assertRaises(MigrationBlocked):
            migrate(self.root, "character_instance", self.persona, apply=True)
        result = migrate(self.root, "character_instance", self.persona, apply=True, approve_existing=True)
        self.assertEqual(Path(result["backups"][0]).read_bytes(), original)
        saved = self.config.read_bytes()
        data = tomllib.loads(saved.decode("utf-8-sig"))
        self.assertEqual(data["developer_instructions"], "common\n")
        self.assertEqual(data["mcp_servers"]["fixture"]["command"], "keep")
        self.assertTrue(saved.startswith(b"\xef\xbb\xbf"))
        self.assertEqual(load(self.root, self.root, environment=False)[1], self.body)
        before = {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(migrate(self.root, "character_instance", self.persona, apply=True, approve_existing=True)["status"], "already-migrated")
        self.assertEqual(before, {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()})
        self.assertEqual(migrate_legacy(self.root / "AGENTS.md", self.config, "absent", apply=True)["status"], "preserve-style")

    def test_existing_different_user_style_activation_and_account_selector_preserved(self):
        self.prepare()
        style = self.write_style(body=b"# User owned\nNAME=Different\n")
        before = style.read_bytes()
        with self.assertRaises(MigrationBlocked):
            migrate(self.root, "character_instance", self.persona, apply=True, approve_existing=True)
        migrate(self.root, "character_instance", self.persona, apply=True,
                approve_existing=True, use_existing_style=True)
        self.assertEqual(style.read_bytes(), before)
        profile = self.config.parent / "account.config.toml"
        profile.write_text('developer_instructions = ' + json.dumps(self.body.decode()) + '\nmodel = "account-model"\n', encoding="utf-8")
        account = self.write_style("character_codex_luna", b"Account selected\n")
        config = self.config.read_bytes()
        migrate(self.root, "character_codex_luna", self.persona, removals=[(profile, self.persona)],
                apply=True, approve_existing=True, preserve_selection=True, use_existing_style=True)
        self.assertEqual(self.config.read_bytes(), config)
        self.assertEqual(account.read_bytes(), b"Account selected\n")
        self.assertEqual(tomllib.loads(profile.read_text())["developer_instructions"], "")

    def test_ambiguous_boundaries_and_failed_save_do_not_destroy_inputs(self):
        original = self.prepare()
        self.persona.write_bytes(b"not in value")
        with self.assertRaises(MigrationBlocked):
            migrate(self.root, "character_instance", self.persona, apply=True, approve_existing=True)
        self.assertEqual(self.config.read_bytes(), original)
        self.persona.write_bytes(self.body)
        real_write = Path.write_bytes
        failed = False
        def fail(path, content):
            nonlocal failed
            if path == self.config and not failed:
                failed = True
                real_write(path, b"partial")
                raise OSError("fixture failure")
            return real_write(path, content)
        with patch.object(Path, "write_bytes", fail):
            with self.assertRaises(OSError):
                migrate(self.root, "character_instance", self.persona, apply=True, approve_existing=True)
        self.assertEqual(self.config.read_bytes(), original)
        self.assertFalse((self.styles / "character_instance.md").exists())

    def test_concurrent_input_change_blocks_before_mutation(self):
        original = self.prepare()
        real_read = Path.read_bytes
        reads = 0
        def changed(path):
            nonlocal reads
            if path == self.persona:
                reads += 1
                if reads > 2:
                    return b"external change"
            return real_read(path)
        with patch.object(Path, "read_bytes", changed):
            with self.assertRaises(MigrationBlocked):
                migrate(self.root, "character_instance", self.persona, apply=True, approve_existing=True)
        self.assertEqual(self.config.read_bytes(), original)
        self.assertFalse(self.styles.exists())


class InstallationFixture(BaseStyleFixture):
    def test_install_preserves_other_handlers_updates_owned_helper_and_noop(self):
        source = ROOT / "scripts/codex_output_style.py"
        self.helper.unlink()
        hooks = self.root / ".codex/hooks.json"
        rules_handler = {"type": "command", "command": "existing-rules", "additionalContextLimit": 9000}
        other = {"UserPromptSubmit": [{"hooks": [{"type": "command", "command": "other-product"}]}]}
        data = {"hooks": dict(other, SessionStart=[{"matcher": "startup|resume|clear|compact", "hooks": [rules_handler]}])}
        hooks.write_text(json.dumps(data), encoding="utf-8")
        config = self.config.read_bytes()
        result = install_handler(source, self.root, apply=True)
        self.assertTrue(result["trust_required"])
        updated = json.loads(hooks.read_bytes())["hooks"]
        self.assertEqual(updated["UserPromptSubmit"], other["UserPromptSubmit"])
        self.assertEqual(updated["SessionStart"][0]["hooks"][0], rules_handler)
        style = updated["SessionStart"][0]["hooks"][1]
        self.assertEqual(style["additionalContextLimit"], 0)
        self.assertEqual(len(updated["SessionStart"][0]["hooks"]), 2)
        self.assertEqual(self.config.read_bytes(), config)
        self.assertFalse(install_handler(source, self.root, apply=True)["changed"])
        next_source = self.root / "next-helper.py"
        next_source.write_bytes(source.read_bytes() + b"\n# fixture revision\n")
        install_handler(next_source, self.root, apply=True)
        self.assertEqual(self.helper.read_bytes(), next_source.read_bytes())
        self.assertEqual(json.loads(hooks.read_bytes())["hooks"]["SessionStart"][0]["hooks"][0], rules_handler)
        self.helper.write_bytes(b"user modified")
        with self.assertRaises(MigrationBlocked):
            install_handler(source, self.root, apply=True)

    def test_installer_failure_restores_existing_helper_and_hook_bytes(self):
        source = ROOT / "scripts/codex_output_style.py"
        install_handler(source, self.root, apply=True)
        hooks = self.root / ".codex/hooks.json"
        original_helper, original_hooks = self.helper.read_bytes(), hooks.read_bytes()
        new_source = self.root / "next-helper.py"
        new_source.write_bytes(original_helper + b"\n# fixture revision\n")
        real_replace = Path.replace
        def fail(path, target):
            if Path(target).name == "liplus-output-style.json":
                raise OSError("fixture failure")
            return real_replace(path, target)
        with patch.object(Path, "replace", fail):
            with self.assertRaises(OSError):
                install_handler(new_source, self.root, apply=True)
        self.assertEqual(self.helper.read_bytes(), original_helper)
        self.assertEqual(hooks.read_bytes(), original_hooks)

    def test_rules_gate_accepts_style_without_readding_inline_and_rejects_bad_style(self):
        self.write_style()
        self.config.write_bytes(b'developer_instructions = "common"\n')
        original = self.config.read_bytes()
        install_rules(ROOT / "rules", self.root, self.config, "style", apply=True)
        self.assertEqual(self.config.read_bytes(), original)
        rules = list((self.root / ".codex/rules").rglob("*.md"))
        self.assertEqual(len(rules), len(list((ROOT / "rules").rglob("*.md"))) - 1)
        self.assertFalse((self.root / ".codex/rules/model/character_Instance.md").exists())
        (self.styles / "character_instance.md").write_bytes(b"\xff")
        with self.assertRaises(ValueError):
            install_rules(ROOT / "rules", self.root, self.config, "style", apply=True)

    def test_json_toml_registration_parity(self):
        import re
        document = (ROOT / "adapter/codex/hooks-config.md").read_text(encoding="utf-8")
        json_config = json.loads(re.search(r"```json\n(.*?)\n```", document, re.S)[1])
        toml_config = tomllib.loads(re.search(r"```toml\n(.*?)\n```", document, re.S)[1])
        self.assertEqual(json_config, toml_config)


if __name__ == "__main__":
    unittest.main()
