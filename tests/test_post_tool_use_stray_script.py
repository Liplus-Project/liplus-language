"""Stray-script scan of `adapter/claude/hooks/post-tool-use.sh` (#2047).

Observed here: after a `Write` / `Edit` / `MultiEdit` payload, the claude port
reads the file named by `tool_input.file_path` and, when a run of Cyrillic /
Hangul (or another listed non-Latin, non-Japanese script) touches a Latin
letter, kana or kanji with no whitespace between, writes one
`hookSpecificOutput.additionalContext` naming the file, the line number and the
run. The file's bytes are unchanged afterwards. A run bounded by whitespace or
punctuation on both sides, a clean file, a binary file and an oversized file
produce no output.

The fixtures carry the observed shapes as `\\u` escapes, so this file does not
itself hold a run the scan reports.

Where the detection condition, the output shape and the skipped cases are
fixed: `docs/6.-Adapter.md` post-tool-use.sh.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from test_on_session_start_observation_surface import (
    BASH,
    HOOK_TIMEOUT,
    NODE,
    ROOT,
    posix_path,
    require_runtime,
)


HOOK = ROOT / "adapter" / "claude" / "hooks" / "post-tool-use.sh"
SETTINGS_DOC = ROOT / "adapter" / "claude" / "hooks-settings.md"
PREFIX = "post-tool-use: stray-script check: "

# Observed shapes that occur on the file surface (issue #2047): each is a run
# touching Latin, kana or kanji with no whitespace between.
CYRILLIC_IN_LATIN = "прем" + "ise"
CYRILLIC_BEFORE_PROLONGED_MARK = "эскал" + "ーション"
HANGUL_IN_KANA = "側へ" + "진" + "んだ"
FLAGGED = {
    "Cyrillic inside a Latin word": (CYRILLIC_IN_LATIN, "прем", "Cyrillic"),
    "Cyrillic before the prolonged sound mark": (
        CYRILLIC_BEFORE_PROLONGED_MARK, "эскал", "Cyrillic"),
    "Hangul between kana": (HANGUL_IN_KANA, "진", "Hangul"),
}

# Runs bounded by whitespace or punctuation on both sides. The first is the
# fourth observed shape (a room utterance): a lone Cyrillic letter set off by
# spaces, which the condition cannot tell from a quoted word.
NOT_FLAGGED = {
    "space-separated lone letters": "в в 在ります",
    "space-separated quoted word": "the word премия is Russian",
    "word in Japanese quote brackets": "「премия」という語",
    "word in backticks": "`премия` と書く",
}

CLEAN_TEXT = "Plain English line.\n日本語の文です。\n"


class Fixture:
    """A project root holding one file the tool call just wrote."""

    def __init__(self) -> None:
        self.root = Path(tempfile.mkdtemp(prefix="liplus-ptu-stray-"))
        self.home = self.root / "home"
        self.home.mkdir()
        self.target = self.root / "written.md"

    def cleanup(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)

    def write(self, data: str | bytes) -> bytes:
        raw = data.encode("utf-8") if isinstance(data, str) else data
        self.target.write_bytes(raw)
        return raw

    def run(self, tool_name: str = "Write", file_path: str | None = None) -> str:
        if not BASH:
            require_runtime("bash", "claude shell hook")
        if not NODE:
            require_runtime("node", "payload parsing and the scan in the shell hook")
        payload = {
            "hook_event_name": "PostToolUse",
            "tool_name": tool_name,
            # The scan runs in node, which reads a host-native path.
            "tool_input": {"file_path": str(self.target) if file_path is None else file_path},
            "tool_response": {"filePath": str(self.target), "success": True},
        }
        env = dict(os.environ)
        env["HOME"] = posix_path(self.home)
        env["CLAUDE_PROJECT_DIR"] = posix_path(self.root)
        result = subprocess.run(
            [BASH, posix_path(HOOK)],
            input=json.dumps(payload).encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            timeout=HOOK_TIMEOUT,
        )
        return result.stdout.decode("utf-8-sig", errors="replace")


def report(test: unittest.TestCase, stdout: str) -> str:
    """The additionalContext value, checked for envelope shape and prefix."""
    test.assertTrue(stdout.strip(), "no report for a file holding a stray run")
    specific = json.loads(stdout)["hookSpecificOutput"]
    test.assertEqual("PostToolUse", specific["hookEventName"])
    context = specific["additionalContext"]
    test.assertTrue(context.startswith(PREFIX), context)
    return context


class StrayScriptScanTestCase(unittest.TestCase):

    def fixture(self) -> Fixture:
        fixture = Fixture()
        self.addCleanup(fixture.cleanup)
        return fixture

    def test_observed_file_surface_shapes_are_reported(self) -> None:
        for name, (text, run, script) in FLAGGED.items():
            with self.subTest(shape=name):
                fixture = self.fixture()
                fixture.write("first line\n" + "prefix " + text + " suffix\n")
                context = report(self, fixture.run())
                self.assertIn(str(fixture.target), context)
                self.assertIn(f"line 2 ({script}):", context)
                self.assertIn(f"[{run}]", context)

    def test_edit_and_multiedit_are_scanned(self) -> None:
        for tool_name in ("Edit", "MultiEdit"):
            with self.subTest(tool_name=tool_name):
                fixture = self.fixture()
                fixture.write(HANGUL_IN_KANA + "\n")
                context = report(self, fixture.run(tool_name))
                self.assertIn("[진]", context)

    def test_file_is_not_rewritten(self) -> None:
        fixture = self.fixture()
        raw = fixture.write("a\r\n" + CYRILLIC_IN_LATIN + "\r\n")
        report(self, fixture.run())
        self.assertEqual(raw, fixture.target.read_bytes())

    def test_bounded_runs_are_not_reported(self) -> None:
        for name, text in NOT_FLAGGED.items():
            with self.subTest(case=name):
                fixture = self.fixture()
                fixture.write(text + "\n")
                self.assertEqual("", fixture.run().strip(), name)

    def test_silent_cases(self) -> None:
        cases = {
            "clean text": (CLEAN_TEXT.encode("utf-8"), "Write", None),
            "binary file": (b"\x00\x01" + CYRILLIC_IN_LATIN.encode("utf-8"), "Write", None),
            "file over 1 MiB": (
                (CYRILLIC_IN_LATIN + "\n").encode("utf-8") + b"a" * (1024 * 1024), "Write", None),
            "missing file": (b"", "Write", "does-not-exist.md"),
            "off-spec tool name casing": (CYRILLIC_IN_LATIN.encode("utf-8"), "write", None),
            "Bash tool": (CYRILLIC_IN_LATIN.encode("utf-8"), "Bash", None),
        }
        for name, (raw, tool_name, path) in cases.items():
            with self.subTest(case=name):
                fixture = self.fixture()
                fixture.write(raw)
                if path is not None:
                    path = str(fixture.root / path)
                self.assertEqual("", fixture.run(tool_name, path).strip(), name)

    def test_report_is_capped(self) -> None:
        fixture = self.fixture()
        fixture.write("".join(f"{CYRILLIC_IN_LATIN} {i}\n" for i in range(25)))
        context = report(self, fixture.run())
        self.assertIn("25 run(s)", context)
        self.assertEqual(20, len(re.findall(r"^  line \d+ ", context, re.M)))
        self.assertIn("... and 5 more", context)


class MatcherTestCase(unittest.TestCase):
    """The settings template must let the file-writing tools reach the hook."""

    def test_post_tool_use_matcher_admits_file_writing_tools(self) -> None:
        text = SETTINGS_DOC.read_text(encoding="utf-8")
        block = re.search(r"```json\n(.*?)\n```", text, re.S)
        self.assertIsNotNone(block, "no JSON block in hooks-settings.md")
        settings = json.loads(block.group(1))
        entries = settings["hooks"]["PostToolUse"]
        commands = [
            (entry["matcher"], hook["command"])
            for entry in entries
            for hook in entry["hooks"]
            if "post-tool-use.sh" in hook.get("command", "")
        ]
        self.assertTrue(commands, "post-tool-use.sh is not bound under PostToolUse")
        for tool_name in ("Bash", "Write", "Edit", "MultiEdit"):
            with self.subTest(tool_name=tool_name):
                self.assertTrue(
                    any(re.fullmatch(matcher, tool_name) for matcher, _ in commands),
                    f"PostToolUse matcher does not admit {tool_name}",
                )


if __name__ == "__main__":
    unittest.main()
