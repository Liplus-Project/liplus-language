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

What is pinned and what is not
------------------------------
The contract (`rules/evolution/cold-start-synthesis.md:47-51`) fixes the date
conditions, the pending filter and the overdue-wins fold; the presentation is
explicitly delegated to the adapter (same file, :55). So the assertions here
read the *judgment* out of the emission — which descriptor surfaces, under which
state, against which date, with which PR reference — and deliberately do not
match the banner text, the bullet prefix, the field names restated inside the
parentheses, the `[PR #N]` suffix notation, or the order of the entries. The
`DUE` / `OVERDUE (human judgment needed)` label words are matched, because those
are specified on the docs side (`docs/6.-Adapter.md:74`), not chosen here.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
import time
import unittest
from datetime import date, timedelta
from pathlib import Path
from typing import NamedTuple


ROOT = Path(__file__).resolve().parents[1]

HOOKS = {
    "claude_sh": ROOT / "adapter" / "claude" / "hooks" / "on-session-start.sh",
    "codex_sh": ROOT / "adapter" / "codex" / "hooks" / "on-session-start.sh",
    "codex_ps1": ROOT / "adapter" / "codex" / "hooks" / "on-session-start.ps1",
}
ADAPTERS = tuple(HOOKS)

HOOK_TIMEOUT = 180

BASH = shutil.which("bash")
PWSH = shutil.which("pwsh")
NODE = shutil.which("node")

# Emission-mode probe. The shell hooks fall back to a full emit whenever the
# diff-only machinery cannot run; the marker path is reachable only from the
# other branch, so tests that need diff-only assert this string is absent.
FAIL_SAFE_MARK = "Fail-safe full emit"

# `rules/evolution/cold-start-synthesis.md:26` — "A single 'No new orientation
# material since last session' line is emitted". The line is the contract; the
# banner it sits under is not.
NO_NEW_MATERIAL = "No new orientation material"


def require_runtime(binary: str, covered: str) -> None:
    """Skip locally, fail on CI.

    A developer host without `pwsh` should still be able to run the rest of the
    suite. On CI the same condition would silently drop the coverage this file
    exists to provide, so there it is an error instead.
    """
    message = f"{binary} is required to exercise the {covered}"
    if os.environ.get("CI"):
        raise AssertionError(f"{message}; it is missing on this CI runner")
    raise unittest.SkipTest(f"{message}; not available on this host")


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


# --------------------------------------------------------------------------
# Emission parsing
# --------------------------------------------------------------------------

def _is_section_rule(line: str) -> bool:
    return len(line) >= 10 and set(line) == {"━"}


def emitted_sections(hook_output: str) -> list[tuple[str, str]]:
    """(banner, body) for every rule-delimited section in the emission."""
    sections: list[tuple[str, str]] = []
    lines = hook_output.replace("\r\n", "\n").split("\n")
    index = 0
    while index < len(lines):
        line = lines[index]
        if line.startswith("━━━ ") and line.endswith(" ━━━") and not _is_section_rule(line):
            banner = line[4:-4].strip()
            index += 1
            body: list[str] = []
            while index < len(lines) and not _is_section_rule(lines[index]):
                body.append(lines[index])
                index += 1
            sections.append((banner, "\n".join(body)))
        index += 1
    return sections


def observation_section(hook_output: str) -> str | None:
    """Body of the observation section, or None when the hook stayed silent.

    Located by topic rather than by exact banner text: the banner is an adapter
    choice, and pinning it made every assertion in this file depend on one
    string. A rename should fail the test that actually cares, not all of them.
    """
    for banner, body in emitted_sections(hook_output):
        if "observation" in banner.lower():
            return body
    return None


def no_new_material_marker(hook_output: str) -> str | None:
    """The no-new-material marker line, or None when it was not emitted."""
    for _banner, body in emitted_sections(hook_output):
        lines = [line for line in body.split("\n") if line.strip()]
        if len(lines) == 1 and NO_NEW_MATERIAL in lines[0]:
            return lines[0]
    return None


class SurfacedEntry(NamedTuple):
    """The judgment reported for one observation entry."""

    state: str  # "DUE" or "OVERDUE"
    date: str  # the ISO date the judgment was made against
    pr: str | None  # PR reference, or None when the entry carries none


_LABEL_RE = re.compile(r"(?<![A-Za-z])(OVERDUE|DUE)(?![A-Za-z])")
_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
_PR_RE = re.compile(r"PR\D{0,3}(\d+)")
_HEADER_RE = re.compile(r"^##\s*observation:\s*(.*)$")


def declared_descriptors(lines) -> tuple[str, ...]:
    """Every non-empty descriptor an observation fixture declares."""
    found = []
    for line in lines:
        match = _HEADER_RE.match(line)
        if match and match.group(1).strip():
            found.append(match.group(1).strip())
    return tuple(found)


def surfaced_entries(
    section_body: str | None, descriptors: tuple[str, ...]
) -> dict[str, SurfacedEntry]:
    """Read the surfaced judgments out of a section body, layout-agnostically.

    `descriptors` is every descriptor the fixture wrote, so the returned mapping
    answers both directions at once: what surfaced, and what did not. A reported
    line that cannot be attributed to exactly one declared descriptor (an empty
    descriptor leaking through, for instance) is an error rather than a silent
    zero.
    """
    if section_body is None:
        return {}
    found: dict[str, SurfacedEntry] = {}
    for line in section_body.split("\n"):
        label = _LABEL_RE.search(line)
        if not label:
            continue
        names = [
            name
            for name in descriptors
            if re.search(rf"(?<![\w-]){re.escape(name)}(?![\w-])", line)
        ]
        if len(names) != 1:
            raise AssertionError(
                f"surfaced line matches {len(names)} declared descriptors, expected 1: "
                f"{line!r} (declared: {list(descriptors)})"
            )
        if names[0] in found:
            raise AssertionError(f"descriptor {names[0]!r} surfaced more than once")
        date_match = _DATE_RE.search(line)
        pr_match = _PR_RE.search(line)
        found[names[0]] = SurfacedEntry(
            state=label.group(1),
            date=date_match.group(0) if date_match else "",
            pr=pr_match.group(1) if pr_match else None,
        )
    return found


class Workspace:
    """Filesystem fixture shaped like a Li+ host workspace."""

    # Diff-only state each hook leaves behind. A second run against the same
    # workspace reads it, which is the only way into the diff-only branch.
    # The two codex hooks intentionally share one path (they are two ports of
    # one adapter), so a two-run test must use a fresh workspace per adapter.
    STATE_RELATIVE = {
        "claude_sh": ".claude/state/last-cold-start-emit.json",
        "codex_sh": ".codex/state/last-cold-start-emit.json",
        "codex_ps1": ".codex/state/last-cold-start-emit.json",
    }

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
        self.claude_projects = self.home / ".claude" / "projects"
        self.claude_primary = self.claude_projects / slug / "memory"
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

    def seed_coldstart_rule(self, token: str) -> Path:
        """Minimal `rules/evolution/cold-start-synthesis.md` in the fixture clone.

        The fixture's `liplus-language` directory is otherwise empty, so the
        always-emitted anchor has an empty body and "the rule literal is
        re-anchored" cannot be observed at all. `token` is planted past the
        frontmatter and the H1 so it survives every port's strip.
        """
        return self.write(
            self.liplus / "rules" / "evolution",
            "cold-start-synthesis.md",
            "---\nalwaysApply: true\n---\n\n# Cold-start Synthesis\n\n"
            f"{token} anchor body.\n",
        )

    def memory_candidates(self, adapter: str) -> tuple[Path, Path]:
        """(higher precedence, lower precedence) memory directory for an adapter."""
        if adapter == "claude_sh":
            return self.claude_primary, self.shared_memory
        return self.shared_memory, self.codex_secondary

    def state_file(self, adapter: str) -> Path:
        return self.workspace / self.STATE_RELATIVE[adapter]

    def clear_state(self) -> None:
        """Remove every adapter's cold-start state file.

        `codex_sh` and `codex_ps1` map to one path, so leaving it behind makes
        the next adapter's first run look like a second run.
        """
        for adapter in ADAPTERS:
            path = self.state_file(adapter)
            if path.is_file():
                path.unlink()

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

    def _command_and_stdin(self, adapter: str, matcher: str) -> tuple[list[str], str]:
        """Hook invocation plus the SessionStart payload the host actually sends.

        The shape is production's, not the hook's convenience. `matcher` is the
        settings.json filter key, not a payload field: the host reports how the
        session started in `source`, alongside a `hook_event_name` fixed at
        `"SessionStart"`. Feeding the claude hook a `{"matcher": ...}` object is
        what kept #1632 F1 green in CI — it read `payload.matcher` and fell back
        to `payload.hook_event_name`, so every production resume / clear /
        compact resolved to the startup default while the test passed.
        """
        hook = HOOKS[adapter]
        payload = {
            "session_id": "test-session",
            "hook_event_name": "SessionStart",
            "source": matcher,
        }
        if adapter == "claude_sh":
            payload["cwd"] = posix_path(self.workspace)
            payload["transcript_path"] = posix_path(self.root / "transcript.jsonl")
            return [BASH, posix_path(hook)], json.dumps(payload)
        if adapter == "codex_sh":
            payload["cwd"] = posix_path(self.workspace)
            return [BASH, posix_path(hook)], json.dumps(payload)
        payload["cwd"] = slash_path(self.workspace)
        return [PWSH, "-NoProfile", "-NonInteractive", "-File", str(hook)], json.dumps(payload)

    def run(self, adapter: str, matcher: str = "startup") -> str:
        """Run one hook and return its emitted context text."""
        if adapter in ("claude_sh", "codex_sh") and not BASH:
            require_runtime("bash", "claude / codex shell hooks")
        if adapter == "codex_ps1" and not PWSH:
            require_runtime("pwsh", "codex PowerShell hook")

        command, stdin_payload = self._command_and_stdin(adapter, matcher)
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
        self.observation_descriptors: tuple[str, ...] = ()
        self.new_workspace()

    def new_workspace(self) -> Workspace:
        """Fresh fixture; several tests need one per adapter layout."""
        self.ws = Workspace()
        self.addCleanup(self.ws.cleanup)
        return self.ws

    def observation_text(self, *lines: str) -> str:
        """Record the fixture's descriptors and render it as file content."""
        self.observation_descriptors = declared_descriptors(lines)
        return "\n".join(lines)

    def write_observation_file(self, *lines: str) -> None:
        """Observation fixture in the shared memory directory.

        `self-evaluation_log.md` is written alongside it so that the memory
        directory resolves through the primary (self-eval) path. That keeps the
        directory-resolution axis out of the way: tests in this shape observe
        parsing and classification only. Resolution has its own test case.
        """
        self.ws.write(self.ws.shared_memory, "self-evaluation_log.md", "# log\n")
        self.ws.write(
            self.ws.shared_memory,
            "self-evolution-observation.md",
            self.observation_text(*lines),
        )

    def run_hook(
        self,
        adapter: str,
        workspace: Workspace | None = None,
        matcher: str = "startup",
    ) -> str:
        """Run a hook, guarding against a local-midnight rollover.

        Fixture dates are offsets from `date.today()` while the hooks read their
        own clock. A rollover between the two would silently reclassify the
        boundary entries, so the run is discarded instead of reported as a
        behavioural failure.
        """
        workspace = workspace if workspace is not None else self.ws
        started_on = date.today()
        output = workspace.run(adapter, matcher)
        if date.today() != started_on:
            self.skipTest("local date rolled over mid-test; fixture offsets are stale")
        return output

    def sections_for_all_adapters(self) -> dict[str, str | None]:
        """Run every adapter against this fixture, one adapter at a time.

        `codex_sh` and `codex_ps1` share one state-file path (`STATE_RELATIVE`),
        so a previous adapter's run would put the next one into diff-only mode
        on what should be its first run. Clearing the state between adapters
        keeps each run a first run.
        """
        sections: dict[str, str | None] = {}
        for adapter in ADAPTERS:
            self.ws.clear_state()
            sections[adapter] = observation_section(self.run_hook(adapter))
        return sections

    def assert_adapters_agree(self, sections: dict[str, str | None]) -> None:
        reference = sections["claude_sh"]
        for adapter, section in sections.items():
            with self.subTest(adapter=adapter):
                self.assertEqual(
                    section,
                    reference,
                    f"{adapter} disagrees with claude_sh on identical input",
                )

    def require_section(self, hook_output: str) -> str:
        """Fail with the emitted banners listed, instead of a bare `None`."""
        section = observation_section(hook_output)
        if section is None:
            banners = [banner for banner, _body in emitted_sections(hook_output)]
            self.fail(f"no observation section was emitted; banners seen: {banners}")
        return section

    def surfaced(self, section_body: str | None) -> dict[str, SurfacedEntry]:
        return surfaced_entries(section_body, self.observation_descriptors)


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
            self.surfaced(sections["claude_sh"]),
            {
                # past expiry folds into OVERDUE only, never reported twice
                "past-expiry": SurfacedEntry("OVERDUE", iso(-2), "1500"),
                # next_check == today is due (the comparison is <=, not <)
                "due-today": SurfacedEntry("DUE", iso(0), "1501"),
                # a missing pr field carries no PR reference
                "due-without-pr": SurfacedEntry("DUE", iso(-1), None),
                # not-yet-due and already-settled stay off the surface
            },
        )

    def test_expiry_exactly_today_is_not_yet_overdue(self) -> None:
        # `expires < today` is a strict comparison. Its `<=` sibling on
        # next_check is pinned above; this is the other half of that boundary.
        self.write_observation_file(
            "## observation: expiring-today",
            "pr: 2100",
            f"expires: {iso(0)}",
            f"next_check: {iso(0)}",
            "verdict_state: pending",
            "",
            "## observation: expiring-today-checked-later",
            "pr: 2101",
            f"expires: {iso(0)}",
            f"next_check: {iso(3)}",
            "verdict_state: pending",
            "",
        )
        sections = self.sections_for_all_adapters()
        self.assert_adapters_agree(sections)
        self.assertEqual(
            self.surfaced(sections["claude_sh"]),
            # DUE via next_check, not OVERDUE via expires; and with the check
            # window still shut, an expires-today entry does not surface at all.
            {"expiring-today": SurfacedEntry("DUE", iso(0), "2100")},
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
        self.assertEqual(self.surfaced(sections["claude_sh"]), {})

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
            # must be reported without a PR reference.
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
            self.surfaced(sections["claude_sh"]),
            {"capitalised-pr-field": SurfacedEntry("DUE", iso(-1), None)},
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
        # A leaked empty-descriptor line cannot be attributed to any declared
        # descriptor, so `surfaced` raises rather than quietly returning one entry.
        self.assertEqual(
            self.surfaced(sections["claude_sh"]),
            {"well-formed": SurfacedEntry("DUE", iso(-1), "1901")},
        )


class MemoryDirResolutionTest(ObservationSurfaceTestCase):
    """Coverage area 2: memory directory resolution (PR #1560 F3 / G2)."""

    def setUp(self) -> None:
        super().setUp()
        self.observation_descriptors = ("reachable",)

    def due_entry(self) -> str:
        return "\n".join(
            [
                "## observation: reachable",
                "pr: 2000",
                f"expires: {iso(7)}",
                f"next_check: {iso(-1)}",
                "verdict_state: pending",
                "",
            ]
        )

    def expected(self) -> dict[str, SurfacedEntry]:
        return {"reachable": SurfacedEntry("DUE", iso(-1), "2000")}

    def test_resolution_does_not_depend_on_self_evaluation_log(self) -> None:
        # No self-evaluation_log.md anywhere: the observation surface must still
        # find its own file rather than inherit an unrelated file's absence.
        self.ws.write(
            self.ws.shared_memory, "self-evolution-observation.md", self.due_entry()
        )
        sections = self.sections_for_all_adapters()
        self.assert_adapters_agree(sections)
        self.assertEqual(self.surfaced(sections["claude_sh"]), self.expected())

    def test_empty_higher_precedence_directory_does_not_shadow(self) -> None:
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                workspace = self.new_workspace()
                higher, lower = workspace.memory_candidates(adapter)
                higher.mkdir(parents=True, exist_ok=True)
                workspace.write(lower, "self-evolution-observation.md", self.due_entry())
                section = self.require_section(self.run_hook(adapter, workspace))
                self.assertEqual(self.surfaced(section), self.expected())

    def test_higher_precedence_directory_without_marker_files_does_not_shadow(self) -> None:
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                workspace = self.new_workspace()
                higher, lower = workspace.memory_candidates(adapter)
                workspace.write(higher, "notes.md", "unrelated\n")
                workspace.write(lower, "self-evolution-observation.md", self.due_entry())
                section = self.require_section(self.run_hook(adapter, workspace))
                self.assertEqual(self.surfaced(section), self.expected())

    def test_claude_glob_fallback_skips_unpopulated_project_slugs(self) -> None:
        """Third-stage fallback in `adapter/claude/hooks/on-session-start.sh`.

        Neither named candidate resolves, so the hook scans
        `~/.claude/projects/*/memory` newest-first. The populated-not-merely-
        existing rule applies there too, which the two named-candidate cases
        above cannot reach. Claude-only: the codex hooks have no glob stage.
        """
        workspace = self.new_workspace()
        populated = workspace.claude_projects / "other-project" / "memory"
        empty = workspace.claude_projects / "empty-project" / "memory"
        workspace.write(populated, "self-evolution-observation.md", self.due_entry())
        empty.mkdir(parents=True, exist_ok=True)
        # `ls -1td` orders by mtime, so make the empty slug strictly newer: it is
        # visited first and must be stepped over rather than claimed.
        now = time.time()
        os.utime(empty, (now, now))
        os.utime(populated, (now - 600, now - 600))

        section = self.require_section(self.run_hook("claude_sh", workspace))
        self.assertEqual(self.surfaced(section), self.expected())


class NoNewMaterialMarkerTest(ObservationSurfaceTestCase):
    """Coverage area 4: the marker's interaction with the observation surface.

    `rules/evolution/cold-start-synthesis.md:26` — the marker fires when no
    section changed AND no observation entry was surfaced. Both halves live in
    the diff-only branch, which is entered only when a prior run left a state
    file behind, so each test here runs one hook twice against one workspace.
    """

    def prepared_workspace(self, adapter: str, observation: str | None) -> Workspace:
        workspace = self.new_workspace()
        # A stable non-empty section: it gives the second run a fingerprint to
        # compare, so "nothing changed" is a real comparison and not vacuous.
        workspace.write(workspace.shared_memory, "self-evaluation_log.md", "# log\n")
        if observation is not None:
            workspace.write(
                workspace.shared_memory, "self-evolution-observation.md", observation
            )
        return workspace

    def run_twice(self, adapter: str, observation: str | None) -> tuple[str, str]:
        if adapter in ("claude_sh", "codex_sh") and not NODE:
            require_runtime("node", "diff-only state handling in the shell hooks")
        workspace = self.prepared_workspace(adapter, observation)

        first = self.run_hook(adapter, workspace)
        self.assertIn(
            FAIL_SAFE_MARK, first, "first run should be the fail-safe full emit"
        )
        self.assertTrue(
            workspace.state_file(adapter).is_file(),
            f"{adapter} did not persist {workspace.state_file(adapter)}; "
            "the second run cannot reach diff-only mode",
        )

        started_on = date.today()
        second = self.run_hook(adapter, workspace)
        if date.today() != started_on:
            self.skipTest("local date rolled over between runs; fixture offsets are stale")
        self.assertNotIn(
            FAIL_SAFE_MARK,
            second,
            f"{adapter} fell back to a full emit on the second run, so the "
            "marker branch was never evaluated",
        )
        return first, second

    def test_marker_appears_when_nothing_changed_and_nothing_is_due(self) -> None:
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                first, second = self.run_twice(adapter, observation=None)
                self.assertIsNone(
                    no_new_material_marker(first),
                    "the marker belongs to diff-only mode, not to the full emit",
                )
                self.assertIsNone(observation_section(second))
                self.assertIsNotNone(
                    no_new_material_marker(second),
                    "an unchanged session with nothing due must still mark the boundary",
                )

    def test_surfaced_observation_suppresses_the_marker(self) -> None:
        observation = self.observation_text(
            "## observation: still-open",
            "pr: 2200",
            f"expires: {iso(-3)}",
            f"next_check: {iso(-10)}",
            "verdict_state: pending",
            "",
        )
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                _first, second = self.run_twice(adapter, observation=observation)
                section = self.require_section(second)
                self.assertEqual(
                    self.surfaced(section),
                    {"still-open": SurfacedEntry("OVERDUE", iso(-3), "2200")},
                    "the observation surface is outside the diff set and must "
                    "re-emit while the entry is unresolved",
                )
                self.assertIsNone(
                    no_new_material_marker(second),
                    "surfacing an overdue entry and declaring no new material in "
                    "the same emission is self-contradictory",
                )


class MatcherResolutionTest(ObservationSurfaceTestCase):
    """Coverage area 5: SessionStart matcher resolution (#1632 F1 / F6).

    `rules/evolution/cold-start-synthesis.md:28-29` — on a non-startup matcher
    "Only the cold-start rule literal is re-anchored. The work context is
    continuous; the diff-only set is not re-evaluated"; `docs/6.-Adapter.md`
    adds that the state file is not updated.

    Both halves are read out of behaviour rather than out of banner text. A
    token planted in the cold-start rule stands for the anchor, a token planted
    in the self-evaluation log stands for the diff-only set, and the state file
    is compared byte for byte. The diff-set token is *changed between the two
    runs* on purpose: an unchanged section is suppressed by diff-only mode
    anyway, so a still-startup hook would look identical to a correct one.
    Changing it makes the two paths diverge — a hook that resolved the matcher
    would stay silent, a hook that fell back to startup re-emits and rewrites.
    """

    # `fork` is claude-only here. It is registered in the Claude settings
    # template (F6) against the documented SessionStart matcher set; the codex
    # hooks.json matcher set is out of this issue's scope and unchanged.
    NON_STARTUP = {
        "claude_sh": ("resume", "clear", "compact", "fork"),
        "codex_sh": ("resume", "clear", "compact"),
        "codex_ps1": ("resume", "clear", "compact"),
    }

    ANCHOR_TOKEN = "QQANCHORTOKENQQ"
    FIRST_TOKEN = "QQDIFFSETONEQQ"
    SECOND_TOKEN = "QQDIFFSETTWOQQ"

    def prepared_workspace(self, adapter: str) -> Workspace:
        if adapter in ("claude_sh", "codex_sh") and not NODE:
            require_runtime("node", "diff-only state handling in the shell hooks")
        workspace = self.new_workspace()
        workspace.seed_coldstart_rule(self.ANCHOR_TOKEN)
        self.write_self_eval(workspace, self.FIRST_TOKEN)
        return workspace

    def write_self_eval(self, workspace: Workspace, token: str) -> None:
        workspace.write(
            workspace.shared_memory,
            "self-evaluation_log.md",
            f"# Self-Evaluation Log\n\n## entry\n{token}\n",
        )

    def test_non_startup_matcher_reanchors_only_and_leaves_state_untouched(self) -> None:
        for adapter in ADAPTERS:
            for matcher in self.NON_STARTUP[adapter]:
                with self.subTest(adapter=adapter, matcher=matcher):
                    workspace = self.prepared_workspace(adapter)

                    startup = self.run_hook(adapter, workspace)
                    self.assertIn(
                        self.FIRST_TOKEN,
                        startup,
                        "the startup run must emit the diff-only set, otherwise "
                        "the non-startup assertion below is vacuous",
                    )
                    state = workspace.state_file(adapter)
                    self.assertTrue(
                        state.is_file(),
                        f"{adapter} did not persist {state}; the state-untouched "
                        "assertion has nothing to compare",
                    )
                    before = state.read_bytes()

                    # Move the diff-only set, so a hook that re-evaluated it
                    # cannot be mistaken for one that correctly stayed silent.
                    self.write_self_eval(workspace, self.SECOND_TOKEN)
                    emission = self.run_hook(adapter, workspace, matcher=matcher)

                    self.assertIn(
                        self.ANCHOR_TOKEN,
                        emission,
                        f"{adapter} did not re-anchor the cold-start rule "
                        f"literal on matcher {matcher!r}",
                    )
                    self.assertNotIn(
                        self.SECOND_TOKEN,
                        emission,
                        f"{adapter} re-evaluated the diff-only set on matcher "
                        f"{matcher!r}; the payload reports it in `source`, so a "
                        "hook reading `matcher` falls back to startup",
                    )
                    self.assertEqual(
                        before,
                        state.read_bytes(),
                        f"{adapter} rewrote the cold-start state file on matcher "
                        f"{matcher!r}; the diff baseline must not move on a "
                        "continuous session",
                    )


if __name__ == "__main__":
    unittest.main()
