"""Process fixtures for Li+update.md 4x.1r installed rules reads."""

import unittest
from test_on_session_start_observation_surface import Workspace, emitted_sections


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


if __name__ == "__main__":
    unittest.main()
