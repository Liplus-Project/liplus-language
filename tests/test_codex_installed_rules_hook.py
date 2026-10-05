"""Process fixtures for Li+update.md 4x.1r installed rules reads."""

import json
import unittest
from test_on_session_start_observation_surface import Workspace, emitted_sections, promotion_section


class InstalledRulesHookTest(unittest.TestCase):
    def fixture(self):
        ws = Workspace()
        self.addCleanup(ws.cleanup)
        ws.write(ws.workspace, "Li+config.md", "LI_PLUS_MODE=clone\nLI_PLUS_BASE_LANGUAGE=ja\nLI_PLUS_PROJECT_LANGUAGE=ja\n")
        ws.seed_coldstart_rule("stale-clone-token")
        ws.write(ws.installed_rules / "evolution", "cold-start-synthesis.md", "---\nalwaysApply: true\n---\n\n# Cold-start Synthesis\n\ninstalled-anchor-token\n")
        ws.write(ws.liplus / "rules/model", "probe.md", "stale-clone-rule")
        ws.write(ws.installed_rules / "model", "probe.md", "installed-rule-token")
        ws.write(ws.installed_rules / "model", "character_Instance.md", "CHARACTER-TEMPLATE-MUST-NOT-INJECT")
        return ws

    def test_both_ports_all_matchers_read_installed_rules_and_omit_character(self):
        for adapter in ("codex_sh", "codex_ps1"):
            for matcher in ("startup", "resume", "clear", "compact"):
                with self.subTest(adapter=adapter, matcher=matcher):
                    ws = self.fixture()
                    output = ws.run(adapter, matcher)
                    self.assertIn("installed-rule-token", output)
                    self.assertIn("installed-anchor-token", output)
                    anchor = next(body for title, body in emitted_sections(output) if "Cold-start Synthesis (" in title)
                    self.assertIn("installed-anchor-token", anchor)
                    self.assertIn(".codex/rules/model/probe.md", output)
                    self.assertNotIn("stale-clone-token", output)
                    self.assertNotIn("stale-clone-rule", output)
                    self.assertNotIn("CHARACTER-TEMPLATE-MUST-NOT-INJECT", output)
                    self.assertNotIn("character_Instance.md", output)

    def test_missing_anchor_requests_installation_without_stale_fallback(self):
        for adapter in ("codex_sh", "codex_ps1"):
            with self.subTest(adapter=adapter):
                ws = self.fixture()
                (ws.installed_rules / "evolution/cold-start-synthesis.md").unlink()
                output = ws.run(adapter)
                self.assertIn("LI_PLUS_UPDATE_STATUS=needed reason=installed-rules-missing", output)
                self.assertNotIn("stale-clone-token", output)
                self.assertNotIn("stale-clone-rule", output)

    def test_missing_recorded_non_anchor_rule_stops_injection_on_all_matchers(self):
        for adapter in ("codex_sh", "codex_ps1"):
            for matcher in ("startup", "resume", "clear", "compact"):
                with self.subTest(adapter=adapter, matcher=matcher):
                    ws = self.fixture()
                    (ws.installed_rules / "model/probe.md").unlink()
                    output = ws.run(adapter, matcher)
                    self.assertIn("LI_PLUS_UPDATE_STATUS=needed reason=installed-rules-missing", output)
                    self.assertNotIn("LI_PLUS_UPDATE_STATUS=unnecessary", output)
                    self.assertNotIn("installed-anchor-token", output)
                    self.assertNotIn("stale-clone-rule", output)
                    self.assertNotIn("stale-clone-token", output)

    def test_unavailable_or_invalid_manifest_stops_injection(self):
        for adapter in ("codex_sh", "codex_ps1"):
            for invalid in (None, "{", {"version": 2, "files": {}},
                            {"version": "1", "files": {}},
                            {"version": 1, "files": []},
                            {"version": 1, "files": {"model/probe.md": "a" * 64}}):
                with self.subTest(adapter=adapter, invalid=invalid):
                    ws = self.fixture()
                    manifest = ws.workspace / ".codex/state/liplus-rules.json"
                    if invalid is None:
                        manifest.unlink()
                    else:
                        manifest.write_text(invalid if isinstance(invalid, str) else json.dumps(invalid), encoding="utf-8")
                    output = ws.run(adapter)
                    self.assertIn("LI_PLUS_UPDATE_STATUS=needed reason=installed-rules-missing", output)
                    self.assertNotIn("installed-anchor-token", output)

    def test_invalid_managed_entries_stop_injection(self):
        for adapter in ("codex_sh", "codex_ps1"):
            for relative, value in (("../outside.md", "a" * 64),
                                    ("model//probe.md", "a" * 64),
                                    ("model/character_Instance.md", "a" * 64),
                                    ("model/probe.md", "invalid")):
                with self.subTest(adapter=adapter, relative=relative, value=value):
                    ws = self.fixture()
                    manifest = ws.workspace / ".codex/state/liplus-rules.json"
                    record = json.loads(manifest.read_text(encoding="utf-8"))
                    record["files"][relative] = value
                    manifest.write_text(json.dumps(record), encoding="utf-8")
                    output = ws.run(adapter)
                    self.assertIn("LI_PLUS_UPDATE_STATUS=needed reason=installed-rules-missing", output)
                    self.assertNotIn("installed-anchor-token", output)

    def test_unrecorded_extra_and_modified_present_rule_remain_readable(self):
        for adapter in ("codex_sh", "codex_ps1"):
            with self.subTest(adapter=adapter):
                ws = self.fixture()
                (ws.installed_rules / "model/probe.md").write_text("modified-present-rule", encoding="utf-8")
                (ws.installed_rules / "model/extra.md").write_text("unrecorded-extra-rule", encoding="utf-8")
                output = ws.run(adapter)
                self.assertIn("modified-present-rule", output)
                self.assertIn("unrecorded-extra-rule", output)
                self.assertNotIn("reason=installed-rules-missing", output)

    def test_keyword_scan_uses_installed_body_and_emits_its_real_path(self):
        for adapter in ("codex_sh", "codex_ps1"):
            with self.subTest(adapter=adapter):
                ws = self.fixture()
                ws.write(ws.shared_memory, "feedback_widgets.md", "---\nname: widget calibration harness\n---\nbody\n")
                ws.write(ws.installed_rules / "model", "probe.md", "widget calibration harness notes\n")
                overlap = promotion_section(ws.run(adapter))
                self.assertIsNotNone(overlap)
                self.assertIn(".codex/rules/model/probe.md", overlap)
                self.assertNotIn("character_Instance.md", overlap)


if __name__ == "__main__":
    unittest.main()
