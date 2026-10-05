"""Real-process fixtures for docs/6.-Adapter.md Windows source/text reads."""

import base64
import json
import os
import shutil
import subprocess
import unittest
from unittest.mock import patch

import test_on_session_start_observation_surface as harness
from test_on_session_start_observation_surface import Workspace, emitted_sections, promotion_section


class WindowsSourceLoadingTest(unittest.TestCase):
    def fixture(self):
        ws = Workspace()
        self.addCleanup(ws.cleanup)
        ws.write(ws.workspace, "Li+config.md", "LI_PLUS_MODE=clone\nLI_PLUS_BASE_LANGUAGE=日本語\nLI_PLUS_PROJECT_LANGUAGE=日本語\n")
        ws.write(ws.workspace, "AGENTS.md", "# --- Li+ BEGIN (fixture-tag) ---\n")
        ws.seed_coldstart_rule("日本語の起動基準 café 雪")
        ws.write(ws.installed_rules / "model", "probe.md", "日本語本文 café 雪 widget calibration harness\n")
        ws.write(ws.installed_rules / "model", "character_Instance.md", "CHARACTER-MUST-NOT-INJECT")
        ws.write(ws.liplus / "docs", "Decision-Structure.md", "# タグ固定の判断 café 雪\n")
        ws.write(ws.liplus / "skills/probe", "SKILL.md", "# タグ固定 skill café 雪\nwidget calibration harness\n")
        ws.binary_source = bytes(range(256)) + "日本語 café 雪".encode("utf-8")
        (ws.liplus / "skills/probe/fixture.bin").write_bytes(ws.binary_source)
        ws.write(ws.shared_memory, "feedback_widgets.md", "---\nname: widget calibration harness\n---\n日本語 memory\n")
        ws.write(ws.shared_memory, "self-evaluation_log.md", "# 自己評価 café 雪\n")
        for args in (("init",), ("add", "."), ("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-m", "Fixture"), ("tag", "fixture-tag")):
            subprocess.run(["git", "-C", str(ws.liplus), *args], check=True, capture_output=True)
        ws.write(ws.liplus / "docs", "Decision-Structure.md", "WORKING-TREE-MUST-NOT-EMIT\n")
        ws.write(ws.liplus / "skills/probe", "SKILL.md", "WORKING-TREE-MUST-NOT-SCAN\n")
        ws.temp_dir = ws.root / "temp with spaces 雪"
        ws.temp_dir.mkdir()
        return ws

    def ports(self):
        if harness.PWSH:
            yield "pwsh", harness.PWSH
        if os.name == "nt" and shutil.which("powershell"):
            yield "ps5.1", shutil.which("powershell")
        if not harness.PWSH and os.name != "nt":
            harness.require_runtime("pwsh", "Windows source fixture")

    def run_hook(self, ws, runtime, matcher="startup", wrapper=""):
        command = [runtime, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass"]
        if wrapper:
            runner = ws.write(ws.root, "runner.ps1", wrapper + "\n& '" + str(harness.HOOKS["codex_ps1"]).replace("'", "''") + "'\n")
            command += ["-File", str(runner)]
        else:
            command += ["-File", str(harness.HOOKS["codex_ps1"])]
        payload = json.dumps({"cwd": str(ws.workspace), "source": matcher, "hook_event_name": "SessionStart"})
        result = subprocess.run(command, input=payload.encode("utf-8"), capture_output=True,
                                env=ws._env_for("codex_ps1", {"TMP": str(ws.temp_dir), "TEMP": str(ws.temp_dir)}), timeout=180)
        self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8", errors="replace"))
        output = json.loads(result.stdout.decode("utf-8"))["hookSpecificOutput"]["additionalContext"]
        self.assertEqual(list(ws.temp_dir.glob("liplus-tree-*")), [])
        return output

    def test_real_archive_and_unicode_text(self):
        for label, runtime in self.ports():
            for matcher in ("startup", "resume", "clear", "compact"):
                with self.subTest(runtime=label, matcher=matcher):
                    ws = self.fixture()
                    capture = ws.root / "extracted-bytes.txt"
                    wrapper = ("function tar { & $env:LIPLUS_FIXTURE_TAR @args; "
                               "$code = $LASTEXITCODE; "
                               "$bytes = [IO.File]::ReadAllBytes((Join-Path $args[3] 'skills/probe/fixture.bin')); "
                               "[IO.File]::WriteAllText($env:LIPLUS_FIXTURE_CAPTURE, [Convert]::ToBase64String($bytes)); "
                               "$global:LASTEXITCODE = $code }")
                    with patch.dict(os.environ, {"LIPLUS_FIXTURE_TAR": shutil.which("tar"), "LIPLUS_FIXTURE_CAPTURE": str(capture)}):
                        output = self.run_hook(ws, runtime, matcher, wrapper)
                    self.assertEqual(base64.b64decode(capture.read_text(encoding="utf-8")), ws.binary_source)
                    self.assertIn("日本語本文 café 雪", output)
                    self.assertIn("LI_PLUS_BASE_LANGUAGE=日本語", output)
                    anchor = next(body for title, body in emitted_sections(output) if "Cold-start Synthesis (" in title)
                    self.assertIn("日本語の起動基準 café 雪", anchor)
                    self.assertNotIn("CHARACTER-MUST-NOT-INJECT", output)
                    self.assertNotIn("WORKING-TREE-MUST-NOT", output)
                    if matcher == "startup":
                        self.assertIn("タグ固定の判断 café 雪", output)
                        self.assertIn("自己評価 café 雪", output)
                        overlap = promotion_section(output)
                        self.assertIn("skills/probe/SKILL.md", overlap)
                        self.assertIn(".codex/rules/model/probe.md", overlap)

    def test_failed_git_empty_tar_and_failed_tar_stop_without_working_tree(self):
        wrappers = {
            "git-failure": "function git { if ($args -contains 'archive') { $global:LASTEXITCODE = 7 } else { & $env:LIPLUS_FIXTURE_GIT @args } }",
            "empty-tar": "function tar { $global:LASTEXITCODE = 0 }",
            "failed-tar": "function tar { $global:LASTEXITCODE = 9 }",
        }
        for label, runtime in self.ports():
            for failure, wrapper in wrappers.items():
                with self.subTest(runtime=label, failure=failure):
                    ws = self.fixture()
                    with patch.dict(os.environ, {"LIPLUS_FIXTURE_GIT": shutil.which("git")}):
                        output = self.run_hook(ws, runtime, wrapper=wrapper)
                    self.assertIn("reason=liplus-source-unresolved", output)
                    self.assertIn("extraction failed", output)
                    self.assertNotIn("WORKING-TREE-MUST-NOT", output)
                    self.assertNotIn("LI_PLUS_UPDATE_STATUS=unnecessary", output)

    def test_unresolved_tag_keeps_existing_fallback(self):
        for label, runtime in self.ports():
            with self.subTest(runtime=label):
                ws = self.fixture()
                ws.write(ws.workspace, "AGENTS.md", "# --- Li+ BEGIN (missing-tag) ---\n")
                output = self.run_hook(ws, runtime)
                self.assertIn("WORKING-TREE-MUST-NOT-EMIT", output)
                self.assertNotIn("extraction failed", output)

    def test_partial_extraction_missing_required_files_stops(self):
        for label, runtime in self.ports():
            for relative in ("docs/Decision-Structure.md", "skills/probe/SKILL.md"):
                with self.subTest(runtime=label, missing=relative):
                    ws = self.fixture()
                    wrapper = ("function tar { & $env:LIPLUS_FIXTURE_TAR @args; "
                               "$code = $LASTEXITCODE; "
                               "Remove-Item -LiteralPath (Join-Path $args[3] '" + relative + "'); "
                               "$global:LASTEXITCODE = $code }")
                    with patch.dict(os.environ, {"LIPLUS_FIXTURE_TAR": shutil.which("tar")}):
                        output = self.run_hook(ws, runtime, wrapper=wrapper)
                    self.assertIn("reason=liplus-source-unresolved", output)
                    self.assertIn("extraction failed", output)
                    self.assertNotIn("WORKING-TREE-MUST-NOT", output)


if __name__ == "__main__":
    unittest.main()
