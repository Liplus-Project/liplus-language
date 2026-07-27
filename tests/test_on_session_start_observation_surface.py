"""Behavioural coverage for the cold-start self-evolution observation surface.

Target = the three `adapter/*/hooks/on-session-start.*` implementations
(claude bash / codex bash / codex PowerShell). Issue #1562.

The first case set is the four behavioural defects brake 1 found on PR #1560:

  F2  PowerShell `-match` / `-ne` are case-insensitive by default while the awk
      ports are case-sensitive, so `Pending` / `PR:` / `Verdict_State:` split the
      three adapters on identical input.
  F4  An `## observation:` header with an empty descriptor was dropped by awk
      (`flush()` name guard) and surfaced by PowerShell.
  F3  The memory directory was resolved only when `self-evaluation_log.md`
      existed, so an unrelated file's absence silenced the observation surface.
  G2  The candidate scan stopped at the first *existing* directory rather than
      the first *populated* one, so an empty higher-precedence memory directory
      shadowed a populated lower-precedence one.

Each hook is executed as a real process against a filesystem fixture; there is
no external dependency (`gh` is stubbed, dates are relative to today).
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

HOOKS = {
    "claude_sh": ROOT / "adapter" / "claude" / "hooks" / "on-session-start.sh",
    "codex_sh": ROOT / "adapter" / "codex" / "hooks" / "on-session-start.sh",
    "codex_ps1": ROOT / "adapter" / "codex" / "hooks" / "on-session-start.ps1",
}
ADAPTERS = tuple(HOOKS)

OBSERVATION_BANNER = "Self-evolution observation (due / overdue)"
HOOK_TIMEOUT = 180

BASH = shutil.which("bash")
PWSH = shutil.which("pwsh")


def posix_path(path: Path) -> str:
    """Drive-letter path -> MSYS form, so it survives a `:`-separated PATH."""
    text = str(path).replace("\\", "/")
    match = re.match(r"^([A-Za-z]):/(.*)$", text)
    if match:
        return "/" + match.group(1).lower() + "/" + match.group(2)
    return text


def slash_path(path: Path) -> str:
    """Native path with forward slashes; accepted by PowerShell on every host."""
    return str(path).replace("\\", "/")


def iso(day_offset: int) -> str:
    return (date.today() + timedelta(days=day_offset)).isoformat()


def _is_section_rule(line: str) -> bool:
    return len(line) >= 10 and set(line) == {"━"}


def observation_section(hook_output: str) -> str | None:
    """Body of the observation section, or None when the hook stayed silent."""
    lines = hook_output.replace("\r\n", "\n").split("\n")
    for index, line in enumerate(lines):
        if line.startswith("━━━ ") and OBSERVATION_BANNER in line:
            body: list[str] = []
            for follow in lines[index + 1 :]:
                if _is_section_rule(follow):
                    return "\n".join(body)
                body.append(follow)
            return "\n".join(body)
    return None


def entry_lines(section_body: str | None) -> list[str]:
    if section_body is None:
        return []
    return [line for line in section_body.split("\n") if line.startswith("  - ")]


class Workspace:
    """Filesystem fixture shaped like a Li+ host workspace."""

    def __init__(self) -> None:
        self.root = Path(tempfile.mkdtemp(prefix="liplus-hook-"))
        self.home = self.root / "home"
        self.workspace = self.root / "ws"
        self.liplus = self.workspace / "liplus-language"
        self.liplus.mkdir(parents=True)
        self.stub_bin = self.home / ".local" / "bin"
        self.stub_bin.mkdir(parents=True)
        self._write_gh_stub()

        slug = re.sub(r"[:/\\]", "-", posix_path(self.workspace))
        # Memory directory candidates, in each adapter's own precedence order.
        self.claude_primary = self.home / ".claude" / "projects" / slug / "memory"
        self.shared_memory = self.workspace / "memory"
        self.codex_secondary = self.liplus / "memory"

    # -- fixture construction -------------------------------------------------

    def _write_gh_stub(self) -> None:
        """`gh` returns nothing: keeps the run offline and deterministic.

        The bash hooks prepend `$HOME/.local/bin` to PATH themselves; the
        PowerShell run gets the same directory prepended by `_env_for`.
        """
        unix_stub = self.stub_bin / "gh"
        unix_stub.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        os.chmod(unix_stub, 0o755)
        (self.stub_bin / "gh.cmd").write_text("@echo off\r\nexit /b 0\r\n", encoding="ascii")

    def write(self, directory: Path, name: str, content: str = "") -> Path:
        directory.mkdir(parents=True, exist_ok=True)
        target = directory / name
        target.write_text(content, encoding="utf-8")
        return target

    def memory_candidates(self, adapter: str) -> tuple[Path, Path]:
        """(higher precedence, lower precedence) memory directory for an adapter."""
        if adapter == "claude_sh":
            return self.claude_primary, self.shared_memory
        return self.shared_memory, self.codex_secondary

    def cleanup(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)

    # -- hook execution -------------------------------------------------------

    def _env_for(self, adapter: str) -> dict[str, str]:
        env = dict(os.environ)
        env.pop("CODEX_PROJECT_DIR", None)
        if adapter == "claude_sh":
            env["HOME"] = posix_path(self.home)
            env["CLAUDE_PROJECT_DIR"] = posix_path(self.workspace)
        elif adapter == "codex_sh":
            env["HOME"] = posix_path(self.home)
        else:
            env["PATH"] = str(self.stub_bin) + os.pathsep + env.get("PATH", "")
        return env

    def _command_and_stdin(self, adapter: str) -> tuple[list[str], str]:
        hook = HOOKS[adapter]
        if adapter == "claude_sh":
            return [BASH, posix_path(hook)], json.dumps({"matcher": "startup"})
        if adapter == "codex_sh":
            payload = {"cwd": posix_path(self.workspace), "source": "startup"}
            return [BASH, posix_path(hook)], json.dumps(payload)
        payload = {"cwd": slash_path(self.workspace), "source": "startup"}
        return [PWSH, "-NoProfile", "-NonInteractive", "-File", str(hook)], json.dumps(payload)

    @staticmethod
    def _missing_runtime(binary: str, covered: str) -> None:
        """Skip locally, fail on CI.

        A developer host without `pwsh` should still be able to run the rest of
        the suite. On CI the same condition would silently drop the coverage
        this file exists to provide, so there it is an error instead.
        """
        message = f"{binary} is required to exercise the {covered}"
        if os.environ.get("CI"):
            raise AssertionError(f"{message}; it is missing on this CI runner")
        raise unittest.SkipTest(f"{message}; not available on this host")

    def run(self, adapter: str) -> str:
        """Run one hook and return its emitted context text."""
        if adapter in ("claude_sh", "codex_sh") and not BASH:
            self._missing_runtime("bash", "claude / codex shell hooks")
        if adapter == "codex_ps1" and not PWSH:
            self._missing_runtime("pwsh", "codex PowerShell hook")

        command, stdin_payload = self._command_and_stdin(adapter)
        completed = subprocess.run(
            command,
            input=stdin_payload.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=self._env_for(adapter),
            timeout=HOOK_TIMEOUT,
        )
        stdout = completed.stdout.decode("utf-8", errors="replace")
        if adapter == "claude_sh":
            return stdout
        # Codex hooks wrap the whole emission in the SessionStart JSON envelope.
        try:
            envelope = json.loads(stdout)
        except json.JSONDecodeError as error:
            raise AssertionError(
                f"{adapter} did not emit JSON: {error}\nstdout={stdout!r}\n"
                f"stderr={completed.stderr.decode('utf-8', errors='replace')!r}"
            ) from error
        return envelope["hookSpecificOutput"]["additionalContext"]


class ObservationSurfaceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.new_workspace()

    def new_workspace(self) -> Workspace:
        """Fresh fixture; several tests need one per adapter layout."""
        self.ws = Workspace()
        self.addCleanup(self.ws.cleanup)
        return self.ws

    def write_observation_file(self, *lines: str) -> None:
        """Observation fixture in the shared memory directory.

        `self-evaluation_log.md` is written alongside it so that the memory
        directory resolves through the primary (self-eval) path. That keeps the
        directory-resolution axis out of the way: tests in this shape observe
        parsing and classification only. Resolution has its own test case.
        """
        self.ws.write(self.ws.shared_memory, "self-evaluation_log.md", "# log\n")
        self.ws.write(
            self.ws.shared_memory, "self-evolution-observation.md", "\n".join(lines)
        )

    def run_hook(self, adapter: str, workspace: Workspace | None = None) -> str:
        """Run a hook, guarding against a local-midnight rollover.

        Fixture dates are offsets from `date.today()` while the hooks read their
        own clock. A rollover between the two would silently reclassify the
        boundary entries, so the run is discarded instead of reported as a
        behavioural failure.
        """
        workspace = workspace if workspace is not None else self.ws
        started_on = date.today()
        output = workspace.run(adapter)
        if date.today() != started_on:
            self.skipTest("local date rolled over mid-test; fixture offsets are stale")
        return output

    def sections_for_all_adapters(self) -> dict[str, str | None]:
        return {adapter: observation_section(self.run_hook(adapter)) for adapter in ADAPTERS}

    def assert_adapters_agree(self, sections: dict[str, str | None]) -> None:
        reference = sections["claude_sh"]
        for adapter, section in sections.items():
            with self.subTest(adapter=adapter):
                self.assertEqual(
                    section,
                    reference,
                    f"{adapter} disagrees with claude_sh on identical input",
                )


class DueOverdueJudgmentTest(ObservationSurfaceTestCase):
    """Coverage area 3: due / overdue classification and silent skip."""

    def test_adapters_agree_on_due_overdue_and_skipped_entries(self) -> None:
        self.write_observation_file(
            "## observation: past-expiry",
            "pr: 1500",
            f"expires: {iso(-2)}",
            f"next_check: {iso(-9)}",
            "verdict_state: pending",
            "",
            "## observation: due-today",
            "pr: 1501",
            f"expires: {iso(7)}",
            f"next_check: {iso(0)}",
            "verdict_state: pending",
            "",
            "## observation: due-without-pr",
            f"expires: {iso(7)}",
            f"next_check: {iso(-1)}",
            "verdict_state: pending",
            "",
            "## observation: not-yet-due",
            "pr: 1503",
            f"expires: {iso(7)}",
            f"next_check: {iso(1)}",
            "verdict_state: pending",
            "",
            "## observation: already-settled",
            "pr: 1504",
            f"expires: {iso(-5)}",
            f"next_check: {iso(-5)}",
            "verdict_state: settle",
            "",
        )
        sections = self.sections_for_all_adapters()
        self.assert_adapters_agree(sections)
        self.assertEqual(
            entry_lines(sections["claude_sh"]),
            [
                # past expiry folds into OVERDUE only, never reported twice
                f"  - OVERDUE (expires {iso(-2)}, human judgment needed): past-expiry [PR #1500]",
                # next_check == today is due (the comparison is <=, not <)
                f"  - DUE (next_check {iso(0)}): due-today [PR #1501]",
                # a missing pr field drops the suffix instead of printing an empty one
                f"  - DUE (next_check {iso(-1)}): due-without-pr",
            ],
        )

    def test_absent_observation_file_is_a_silent_skip(self) -> None:
        # The memory directory resolves (self-evaluation_log.md is present) but
        # carries no observation file: no section at all, not an empty one.
        self.ws.write(self.ws.shared_memory, "self-evaluation_log.md", "# log\n")
        for adapter, section in self.sections_for_all_adapters().items():
            with self.subTest(adapter=adapter):
                self.assertIsNone(section)

    def test_no_open_check_window_is_a_silent_skip(self) -> None:
        self.write_observation_file(
            "## observation: future",
            "pr: 1600",
            f"expires: {iso(14)}",
            f"next_check: {iso(7)}",
            "verdict_state: pending",
            "",
            "## observation: resolved",
            "pr: 1601",
            f"expires: {iso(-14)}",
            f"next_check: {iso(-14)}",
            "verdict_state: settle",
            "",
        )
        for adapter, section in self.sections_for_all_adapters().items():
            with self.subTest(adapter=adapter):
                self.assertIsNone(section)


class AdapterParityTest(ObservationSurfaceTestCase):
    """Coverage area 1: identical output for identical input (PR #1560 F2 / F4)."""

    def test_verdict_state_case_variants_are_not_pending(self) -> None:
        self.write_observation_file(
            "## observation: capitalised-state",
            "pr: 1700",
            f"expires: {iso(7)}",
            f"next_check: {iso(-1)}",
            "verdict_state: Pending",
            "",
            "## observation: upper-state",
            "pr: 1701",
            f"expires: {iso(7)}",
            f"next_check: {iso(-1)}",
            "verdict_state: PENDING",
            "",
        )
        sections = self.sections_for_all_adapters()
        self.assert_adapters_agree(sections)
        self.assertEqual(entry_lines(sections["claude_sh"]), [])

    def test_field_name_case_variants_are_not_recognised(self) -> None:
        self.write_observation_file(
            # Verdict_State is not the field name, so the entry has no
            # verdict_state at all and must not be treated as pending.
            "## observation: capitalised-field",
            "pr: 1800",
            f"expires: {iso(7)}",
            f"next_check: {iso(-1)}",
            "Verdict_State: pending",
            "",
            # PR is not the field name either: the entry is still due, but it
            # must be reported without a [PR #...] suffix.
            "## observation: capitalised-pr-field",
            "PR: 1801",
            f"expires: {iso(7)}",
            f"next_check: {iso(-1)}",
            "verdict_state: pending",
            "",
        )
        sections = self.sections_for_all_adapters()
        self.assert_adapters_agree(sections)
        self.assertEqual(
            entry_lines(sections["claude_sh"]),
            [f"  - DUE (next_check {iso(-1)}): capitalised-pr-field"],
        )

    def test_empty_descriptor_entry_is_dropped(self) -> None:
        self.write_observation_file(
            "## observation:",
            "pr: 1900",
            f"expires: {iso(7)}",
            f"next_check: {iso(-1)}",
            "verdict_state: pending",
            "",
            "## observation: well-formed",
            "pr: 1901",
            f"expires: {iso(7)}",
            f"next_check: {iso(-1)}",
            "verdict_state: pending",
            "",
        )
        sections = self.sections_for_all_adapters()
        self.assert_adapters_agree(sections)
        self.assertEqual(
            entry_lines(sections["claude_sh"]),
            [f"  - DUE (next_check {iso(-1)}): well-formed [PR #1901]"],
        )


class MemoryDirResolutionTest(ObservationSurfaceTestCase):
    """Coverage area 2: memory directory resolution (PR #1560 F3 / G2)."""

    DUE_ENTRY = "\n".join(
        [
            "## observation: reachable",
            "pr: 2000",
            "expires: {expires}",
            "next_check: {next_check}",
            "verdict_state: pending",
            "",
        ]
    )

    def due_entry(self) -> str:
        return self.DUE_ENTRY.format(expires=iso(7), next_check=iso(-1))

    def expected_entry_lines(self) -> list[str]:
        return [f"  - DUE (next_check {iso(-1)}): reachable [PR #2000]"]

    def test_resolution_does_not_depend_on_self_evaluation_log(self) -> None:
        # No self-evaluation_log.md anywhere: the observation surface must still
        # find its own file rather than inherit an unrelated file's absence.
        self.ws.write(
            self.ws.shared_memory, "self-evolution-observation.md", self.due_entry()
        )
        sections = self.sections_for_all_adapters()
        self.assert_adapters_agree(sections)
        self.assertEqual(entry_lines(sections["claude_sh"]), self.expected_entry_lines())

    def test_empty_higher_precedence_directory_does_not_shadow(self) -> None:
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                workspace = self.new_workspace()
                higher, lower = workspace.memory_candidates(adapter)
                higher.mkdir(parents=True, exist_ok=True)
                workspace.write(lower, "self-evolution-observation.md", self.due_entry())
                section = observation_section(self.run_hook(adapter, workspace))
                self.assertEqual(entry_lines(section), self.expected_entry_lines())

    def test_higher_precedence_directory_without_marker_files_does_not_shadow(self) -> None:
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                workspace = self.new_workspace()
                higher, lower = workspace.memory_candidates(adapter)
                workspace.write(higher, "notes.md", "unrelated\n")
                workspace.write(lower, "self-evolution-observation.md", self.due_entry())
                section = observation_section(self.run_hook(adapter, workspace))
                self.assertEqual(entry_lines(section), self.expected_entry_lines())


if __name__ == "__main__":
    unittest.main()
