"""Firing trace of the three `adapter/*/hooks/post-tool-use.*` ports (#1710).

Observed here: once a Bash command's first line matches `gh pr create`, each
port writes exactly one `hookSpecificOutput.additionalContext` line on stdout,
and that line names how the run ended — appended, PATCH failed, or which step
found nothing to append. Tool calls that do not match write nothing and never
reach `gh`.

The payload carries the PR URL in `tool_response.output`, the field the ports
read. `gh` is a stub reading canned answers from files in the fixture root and
logging each call, so the append path is observed without a network, and the
PATCH it sends is read back from the log.

Where the channel choice and each line's wording are fixed: `docs/6.-Adapter.md`
post-tool-use.sh.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from test_on_session_start_observation_surface import (
    ADAPTERS,
    BASH,
    HOOK_TIMEOUT,
    NODE,
    PWSH,
    ROOT,
    posix_path,
    require_runtime,
    slash_path,
)


POST_TOOL_USE = {
    "claude_sh": ROOT / "adapter" / "claude" / "hooks" / "post-tool-use.sh",
    "codex_sh": ROOT / "adapter" / "codex" / "hooks" / "post-tool-use.sh",
    "codex_ps1": ROOT / "adapter" / "codex" / "hooks" / "post-tool-use.ps1",
}

ORIGIN_URL = "https://github.com/Liplus-Project/liplus-language.git"
PR_URL = "https://github.com/Liplus-Project/liplus-language/pull/4242"
TRACE_PREFIX = "post-tool-use: "


class Fixture:
    """Project root with a `liplus-language` clone and a scripted `gh`."""

    def __init__(self) -> None:
        self.root = Path(tempfile.mkdtemp(prefix="liplus-ptu-trace-"))
        self.home = self.root / "home"
        self.project = self.root / "project"
        self.liplus = self.project / "liplus-language"
        self.liplus.mkdir(parents=True)
        self.stub_bin = self.home / ".local" / "bin"
        self.stub_bin.mkdir(parents=True)
        self.answers = self.root / "answers"
        self.answers.mkdir()
        self.gh_log = self.root / "gh-calls.log"
        self.answer(body="", subs="", patch_exit=0)
        self._write_stubs()
        self._init_clone()

    def answer(self, *, body: str, subs: str, patch_exit: int) -> None:
        (self.answers / "body").write_text(body, encoding="utf-8", newline="\n")
        (self.answers / "subs").write_text(subs, encoding="utf-8", newline="\n")
        (self.answers / "patch_exit").write_text(
            str(patch_exit), encoding="utf-8", newline="\n"
        )

    def _write_stubs(self) -> None:
        # POSIX stub, found through `$HOME/.local/bin` by the shell ports (and by
        # pwsh on a POSIX host if it prefers it over the .ps1 below; both answer
        # alike). The PATCH arm is tested first: its URL also contains /pulls/.
        log = posix_path(self.gh_log)
        answers = posix_path(self.answers)
        sh_stub = self.stub_bin / "gh"
        sh_stub.write_text(
            "#!/bin/sh\n"
            f'printf "CALL %s\\n" "$*" >> "{log}"\n'
            'case "$*" in\n'
            f'  *"--method PATCH"*) exit "$(cat "{answers}/patch_exit")" ;;\n'
            f'  */sub_issues*) cat "{answers}/subs"; exit 0 ;;\n'
            f'  */pulls/*) cat "{answers}/body"; exit 0 ;;\n'
            "esac\n"
            "exit 0\n",
            encoding="utf-8",
            newline="\n",
        )
        os.chmod(sh_stub, 0o755)

        # PowerShell stub. Emits one pipeline object per line, which is the shape
        # a native `gh` produces when its output is captured in PowerShell.
        ps_log = slash_path(self.gh_log)
        ps_answers = slash_path(self.answers)
        (self.stub_bin / "gh.ps1").write_text(
            "$joined = $args -join ' '\n"
            f"Add-Content -LiteralPath '{ps_log}' -Value ('CALL ' + $joined) -Encoding utf8\n"
            "function Lines([string]$name) {\n"
            f"  $t = Get-Content -LiteralPath ('{ps_answers}/' + $name) -Raw\n"
            "  if ($t) { $t.TrimEnd(\"`n\").Split(\"`n\") }\n"
            "}\n"
            "if ($joined -like '*--method PATCH*') {\n"
            f"  exit ([int]((Get-Content -LiteralPath '{ps_answers}/patch_exit' -Raw).Trim()))\n"
            "}\n"
            "if ($joined -like '*/sub_issues*') { Lines 'subs'; exit 0 }\n"
            "if ($joined -like '*/pulls/*') { Lines 'body'; exit 0 }\n"
            "exit 0\n",
            encoding="utf-8",
            newline="\n",
        )

    def _init_clone(self) -> None:
        env = dict(os.environ)
        env["GIT_CONFIG_GLOBAL"] = str(self.root / "gitconfig-absent")
        env["GIT_CONFIG_SYSTEM"] = str(self.root / "gitconfig-absent")
        for args in (["init", "-q"], ["remote", "add", "origin", ORIGIN_URL]):
            subprocess.run(
                ["git", "-C", str(self.liplus), *args],
                check=True,
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

    def gh_calls(self) -> str:
        if not self.gh_log.is_file():
            return ""
        return self.gh_log.read_text(encoding="utf-8-sig", errors="replace")

    def cleanup(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)

    def run(
        self,
        adapter: str,
        *,
        tool_name: str = "Bash",
        command: str = "gh pr create --fill",
        tool_response: object = None,
    ) -> str:
        if adapter in ("claude_sh", "codex_sh"):
            if not BASH:
                require_runtime("bash", "claude / codex shell hooks")
            if not NODE:
                require_runtime("node", "payload parsing in the shell hooks")
        if adapter == "codex_ps1" and not PWSH:
            require_runtime("pwsh", "codex PowerShell hook")

        payload = {
            "hook_event_name": "PostToolUse",
            "tool_name": tool_name,
            "tool_input": {"command": command},
            "tool_response": (
                {"output": PR_URL} if tool_response is None else tool_response
            ),
        }
        hook = POST_TOOL_USE[adapter]
        env = dict(os.environ)
        env.pop("CODEX_PROJECT_DIR", None)
        env.pop("CLAUDE_PROJECT_DIR", None)
        if adapter == "codex_ps1":
            payload["cwd"] = slash_path(self.project)
            argv = [PWSH, "-NoProfile", "-NonInteractive", "-File", str(hook)]
            env["PATH"] = str(self.stub_bin) + os.pathsep + env.get("PATH", "")
        else:
            payload["cwd"] = posix_path(self.project)
            argv = [BASH, posix_path(hook)]
            env["HOME"] = posix_path(self.home)
            if adapter == "claude_sh":
                env["CLAUDE_PROJECT_DIR"] = posix_path(self.project)

        result = subprocess.run(
            argv,
            input=json.dumps(payload).encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            timeout=HOOK_TIMEOUT,
        )
        return result.stdout.decode("utf-8-sig", errors="replace")


def trace_line(test: unittest.TestCase, adapter: str, stdout: str) -> str:
    """The additionalContext value, checked for envelope shape and one line."""
    test.assertTrue(stdout.strip(), f"{adapter} emitted nothing after gh pr create matched")
    envelope = json.loads(stdout)
    specific = envelope["hookSpecificOutput"]
    test.assertEqual("PostToolUse", specific["hookEventName"], adapter)
    line = specific["additionalContext"]
    test.assertTrue(line.startswith(TRACE_PREFIX), f"{adapter}: {line!r}")
    test.assertNotIn("\n", line, f"{adapter} trace spans more than one line: {line!r}")
    return line


class FiringTraceTestCase(unittest.TestCase):

    def fixture(self) -> Fixture:
        fixture = Fixture()
        self.addCleanup(fixture.cleanup)
        return fixture

    def test_append_emits_appended_trace_and_patches_body(self) -> None:
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                fixture = self.fixture()
                fixture.answer(body="Implements #100.", subs="101\n102\n", patch_exit=0)
                line = trace_line(self, adapter, fixture.run(adapter))
                self.assertIn("PR #4242: sub-issue refs auto-appended", line)
                self.assertIn("parent #100", line)
                self.assertIn("Closes #101, Closes #102", line)
                calls = fixture.gh_calls()
                self.assertIn("--method PATCH", calls, adapter)
                self.assertIn("Closes #101", calls, adapter)
                self.assertIn("Closes #102", calls, adapter)

    def test_failed_patch_is_not_reported_as_appended(self) -> None:
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                fixture = self.fixture()
                fixture.answer(body="Implements #100.", subs="101\n", patch_exit=1)
                line = trace_line(self, adapter, fixture.run(adapter))
                self.assertIn("PATCH of the body failed", line)
                self.assertIn("Closes #101", line)
                self.assertNotIn("auto-appended", line)
                self.assertIn("--method PATCH", fixture.gh_calls(), adapter)

    def test_each_no_append_exit_names_its_reason(self) -> None:
        cases = (
            ("already referenced", dict(body="Implements #100. Closes #101", subs="101\n"),
             None, "every sub-issue of parent #100 is already referenced"),
            ("no sub-issues", dict(body="Implements #100.", subs=""),
             None, "parent #100 has no sub-issues"),
            ("no parent ref", dict(body="No issue reference here.", subs="101\n"),
             None, "body carries no #<issue> reference"),
            ("empty body", dict(body="", subs="101\n"),
             None, "body could not be read or is empty"),
            ("output absent", dict(body="Implements #100.", subs="101\n"),
             {"stdout": PR_URL}, "tool_response.output is absent or empty"),
            ("output without URL", dict(body="Implements #100.", subs="101\n"),
             {"output": "aborted: you must first push the current branch"},
             "carries no /pull/<number> URL"),
        )
        for adapter in ADAPTERS:
            for name, answers, response, expected in cases:
                with self.subTest(adapter=adapter, case=name):
                    fixture = self.fixture()
                    fixture.answer(patch_exit=0, **answers)
                    line = trace_line(
                        self, adapter, fixture.run(adapter, tool_response=response)
                    )
                    self.assertIn(expected, line)
                    self.assertNotIn("auto-appended", line)
                    self.assertNotIn("--method PATCH", fixture.gh_calls(), adapter)

    def test_unrelated_tool_calls_emit_nothing(self) -> None:
        cases = (
            ("other command", dict(command="git status",
                                   tool_response={"output": "nothing to commit"})),
            ("mention in output only", dict(command="echo hi",
                                            tool_response={"output": "gh pr create " + PR_URL})),
            ("mention past first line", dict(command="echo hi\ngh pr create --fill")),
            ("non-Bash tool", dict(tool_name="Read")),
        )
        for adapter in ADAPTERS:
            for name, kwargs in cases:
                with self.subTest(adapter=adapter, case=name):
                    fixture = self.fixture()
                    fixture.answer(body="Implements #100.", subs="101\n", patch_exit=0)
                    stdout = fixture.run(adapter, **kwargs)
                    self.assertEqual("", stdout.strip(), f"{adapter} emitted on {name}")
                    self.assertEqual("", fixture.gh_calls(), f"{adapter} called gh on {name}")


if __name__ == "__main__":
    unittest.main()
