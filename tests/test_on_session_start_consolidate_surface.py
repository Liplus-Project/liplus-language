"""Behavioural coverage for the cold-start memory consolidate due surface.

Target = the three `adapter/*/hooks/on-session-start.*` implementations
(claude bash / codex bash / codex PowerShell). Issue #2165.

The firing condition is fixed at `rules/evolution/memory-entry-format.md`
Consolidate Trigger, the surface at `rules/evolution/cold-start-synthesis.md`
Consolidate Due Surface, and the hook-side reading of the index at
`docs/6.-Adapter.md` (memory consolidate due surface). This file observes the
three ports on identical fixtures and asserts they reach the same judgment.

What is observed and what is not
--------------------------------
Observed: the judgment each port emits for a record dated 13, 14 and 40 days
back, today and in the future; for an index whose head is not a record line
(no record line, a record line only below the head, a date that is not a
calendar date, a differently cased label); for an absent index; for an index
with a BOM and CRLF line ends; for heads on both sides of the record-line
bound (#2182) -- space, tab and non-ASCII characters around the label and the date,
CR other than one at the line end, UTF-16 and UTF-32 encodings, and the years
0000, 0001 and 9999 -- each checked for the same judgment on every port; and
whether memory files change across a run.
The `DUE` label word is matched because `docs/6.-Adapter.md` specifies it. The banner text, the bullet prefix and the
wording around the date are adapter choices (`docs/2.-Evolution.md` Cold-start
Synthesis, hook output contract) and are read through the judgment only: which
state, which last-run date, how many days.

The fixture, the hook runner and the workspace layout are reused from
`test_on_session_start_observation_surface`, for the reason
`test_on_session_start_tally_surface` gives: the surfaces run in the same hooks
over the same workspace layout, and a second copy of that harness would be the
copy that drifts.
"""

from __future__ import annotations

import re
import unittest
from typing import NamedTuple

from test_on_session_start_observation_surface import (
    ADAPTERS,
    FAIL_SAFE_MARK,
    NODE,
    ObservationSurfaceTestCase,
    Workspace,
    emitted_sections,
    iso,
    no_new_material_marker,
    require_runtime,
)


RECORD = "**Last consolidate run:**"


def consolidate_section(hook_output: str) -> str | None:
    """Body of the consolidate section, or None when the hook stayed silent.

    Located by topic rather than by exact banner text, as the sibling surface
    modules do: the banner is an adapter choice.
    """
    for banner, body in emitted_sections(hook_output):
        if "consolidate" in banner.lower():
            return body
    return None


class Judgment(NamedTuple):
    last_run: str | None  # the ISO date reported back, None for the no-line arm
    days: int | None      # the elapsed days reported back, None for the no-line arm


_DUE_LINE_RE = re.compile(r"(?<![A-Za-z])DUE(?![A-Za-z])")
_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
_DAYS_RE = re.compile(r"(\d+)\s+days?\b")
# The resolved index path, as the emission names it. Matched by its filename
# rather than by a spelling: the three ports render one path three ways.
_INDEX_PATH_RE = re.compile(r"\S*MEMORY\.md")


def judgment(section_body: str | None) -> Judgment | None:
    """What the hook judged, or None when nothing surfaced.

    Exactly one DUE line is expected: the surface is about one index, so a
    second line would be a port reporting one condition twice.
    """
    if section_body is None:
        return None
    due_lines = [line for line in section_body.split("\n") if _DUE_LINE_RE.search(line)]
    if len(due_lines) != 1:
        raise AssertionError(f"expected exactly one DUE line, got {due_lines!r}")
    line = _INDEX_PATH_RE.sub("", due_lines[0])
    date_match = _DATE_RE.search(line)
    days_match = _DAYS_RE.search(line)
    return Judgment(
        last_run=date_match.group(0) if date_match else None,
        days=int(days_match.group(1)) if days_match else None,
    )


NO_LINE = Judgment(last_run=None, days=None)


class ConsolidateSurfaceTestCase(ObservationSurfaceTestCase):
    """Fixture writer + per-adapter runner for the consolidate surface."""

    def resolve_memory(self, workspace: Workspace | None = None) -> None:
        """Make the shared memory directory resolve through the self-eval path.

        Keeps the resolution axis out of the cases that observe parsing and
        classification only; resolution has its own cases below.
        """
        workspace = workspace if workspace is not None else self.ws
        workspace.write(workspace.shared_memory, "self-evaluation_log.md", "# log\n")

    def write_index(
        self,
        content: str,
        workspace: Workspace | None = None,
        encoding_prefix: bytes = b"",
        newline: str = "\n",
    ) -> None:
        workspace = workspace if workspace is not None else self.ws
        self.resolve_memory(workspace)
        target = workspace.shared_memory / "MEMORY.md"
        target.write_bytes(encoding_prefix + content.replace("\n", newline).encode("utf-8"))

    def index_with_last_run(self, day_offset: int) -> str:
        return f"{RECORD} {iso(day_offset)}\n\n- [Some entry](some-entry.md) - hook\n"

    def judgments_for_all_adapters(self) -> dict[str, Judgment | None]:
        found: dict[str, Judgment | None] = {}
        for adapter in ADAPTERS:
            self.ws.clear_state()
            found[adapter] = judgment(consolidate_section(self.run_hook(adapter)))
        return found

    def assert_every_adapter(self, expected: Judgment | None) -> None:
        for adapter, found in self.judgments_for_all_adapters().items():
            with self.subTest(adapter=adapter):
                self.assertEqual(found, expected)


class FiringConditionTest(ConsolidateSurfaceTestCase):
    def test_fourteen_days_is_due(self) -> None:
        """Boundary day of the Consolidate Trigger window: surfaced."""
        self.write_index(self.index_with_last_run(-14))
        self.assert_every_adapter(Judgment(last_run=iso(-14), days=14))

    def test_thirteen_days_is_silent(self) -> None:
        self.write_index(self.index_with_last_run(-13))
        self.assert_every_adapter(None)

    def test_recorded_today_is_silent(self) -> None:
        self.write_index(self.index_with_last_run(0))
        self.assert_every_adapter(None)

    def test_long_overdue_reports_the_elapsed_days(self) -> None:
        self.write_index(self.index_with_last_run(-40))
        self.assert_every_adapter(Judgment(last_run=iso(-40), days=40))

    def test_date_later_than_today_is_silent(self) -> None:
        self.write_index(self.index_with_last_run(+5))
        self.assert_every_adapter(None)

    def test_only_the_head_line_is_read(self) -> None:
        """A stale record line below a recent head does not surface."""
        self.write_index(f"{RECORD} {iso(-2)}\n{RECORD} {iso(-30)}\n")
        self.assert_every_adapter(None)

    def test_blank_lines_ahead_of_the_head_are_skipped(self) -> None:
        self.write_index(f"\n\n{RECORD} {iso(-2)}\n")
        self.assert_every_adapter(None)


class NoLineTest(ConsolidateSurfaceTestCase):
    """The no-line arm of Consolidate Trigger, as the hooks read the index head."""

    def test_index_without_the_line_is_due(self) -> None:
        self.write_index("- [Some entry](some-entry.md) - hook\n")
        self.assert_every_adapter(NO_LINE)

    def test_record_line_below_the_head_is_no_line(self) -> None:
        """A recent record line that is not the index head does not count."""
        self.write_index(f"# Memory index\n\n{RECORD} {iso(-1)}\n")
        self.assert_every_adapter(NO_LINE)

    def test_index_absent_in_a_resolved_memory_directory_is_due(self) -> None:
        self.resolve_memory()
        self.assert_every_adapter(NO_LINE)

    def test_date_that_is_not_a_calendar_date_counts_as_no_line(self) -> None:
        year = iso(0)[:4]
        self.write_index(f"{RECORD} {year}-02-30\n")
        self.assert_every_adapter(NO_LINE)

    def test_record_without_a_date_counts_as_no_line(self) -> None:
        self.write_index(f"{RECORD} never\n")
        self.assert_every_adapter(NO_LINE)

    def test_record_label_is_case_sensitive(self) -> None:
        """A lower-cased label reads as no line on every port."""
        self.write_index(f"**last consolidate run:** {iso(-1)}\n")
        self.assert_every_adapter(NO_LINE)


class EncodingTest(ConsolidateSurfaceTestCase):
    def test_bom_and_crlf_do_not_hide_the_line(self) -> None:
        """A BOM-prefixed CRLF index is read as its LF form is."""
        self.write_index(
            self.index_with_last_run(-15),
            encoding_prefix=b"\xef\xbb\xbf",
            newline="\r\n",
        )
        self.assert_every_adapter(Judgment(last_run=iso(-15), days=15))

    def test_bom_and_crlf_on_a_recent_line_stay_silent(self) -> None:
        self.write_index(
            self.index_with_last_run(-1),
            encoding_prefix=b"\xef\xbb\xbf",
            newline="\r\n",
        )
        self.assert_every_adapter(None)


class RecordLineBoundTest(ConsolidateSurfaceTestCase):
    """Heads on both sides of the record-line bound (#2182).

    The bound is fixed at `docs/6.-Adapter.md` (memory consolidate due
    surface). Each case writes the heads it lists and observes the judgment
    of the three ports on each. The no-line cases carry a recent date, so a
    port that read the head would stay silent instead.
    """

    def write_raw_index(self, data: bytes) -> None:
        self.resolve_memory()
        (self.ws.shared_memory / "MEMORY.md").write_bytes(data)

    def assert_no_line_for_heads(self, heads: dict[str, str]) -> None:
        for name, head in heads.items():
            with self.subTest(head=name):
                self.write_index(head + "\n- [Some entry](some-entry.md) - hook\n")
                self.assert_every_adapter(NO_LINE)

    def test_space_and_tab_around_the_label_and_the_date_are_no_line(self) -> None:
        recent = iso(-1)
        self.assert_no_line_for_heads({
            "leading space": f" {RECORD} {recent}",
            "leading tab": f"\t{RECORD} {recent}",
            "no gap": f"{RECORD}{recent}",
            "two spaces": f"{RECORD}  {recent}",
            "tab gap": f"{RECORD}\t{recent}",
            "trailing space": f"{RECORD} {recent} ",
            "trailing tab": f"{RECORD} {recent}\t",
            "trailing text": f"{RECORD} {recent} (by Lin)",
        })

    def test_non_ascii_characters_in_the_head_are_no_line(self) -> None:
        recent = iso(-1)
        fullwidth = recent.translate({ord(d): 0xFF10 + int(d) for d in "0123456789"})
        self.assert_no_line_for_heads({
            "U+00A0 gap": f"{RECORD}\u00a0{recent}",
            "U+3000 gap": f"{RECORD}\u3000{recent}",
            "U+3000 ahead": f"\u3000{RECORD} {recent}",
            "U+3000 after": f"{RECORD} {recent}\u3000",
            "U+3000-only line ahead": f"\u3000\n{RECORD} {recent}",
            "U+FEFF ahead of the second line": f"\n\ufeff{RECORD} {recent}",
            "fullwidth digits": f"{RECORD} {fullwidth}",
        })

    def test_space_and_tab_only_lines_ahead_are_blank(self) -> None:
        self.write_index(f" \n\t\n \t \n{RECORD} {iso(-1)}\n")
        self.assert_every_adapter(None)

    def test_one_cr_at_the_line_end_is_read(self) -> None:
        recent = iso(-1)
        for name, data in {
            "CRLF": f"{RECORD} {recent}\r\n- x\r\n",
            "CR at the end of the file": f"{RECORD} {recent}\r",
            "CR-only line ahead": f"\r\n{RECORD} {recent}\r\n",
        }.items():
            with self.subTest(case=name):
                self.write_raw_index(data.encode("utf-8"))
                self.assert_every_adapter(None)

    def test_any_other_cr_is_no_line(self) -> None:
        recent = iso(-1)
        for name, data in {
            "two CRs at the end": f"{RECORD} {recent}\r\r\n",
            "lone CR ahead": f"\r{RECORD} {recent}\n",
            "lone CR as the gap": f"{RECORD}\r{recent}\n",
            "lone CR inside the date": f"{RECORD} {recent[:4]}\r{recent[4:]}\n",
            "CR-CR line ahead": f"\r\r\n{RECORD} {recent}\n",
        }.items():
            with self.subTest(case=name):
                self.write_raw_index(data.encode("utf-8"))
                self.assert_every_adapter(NO_LINE)

    def test_trailing_nul_is_no_line(self) -> None:
        self.write_raw_index(f"{RECORD} {iso(-1)}\x00\n".encode("utf-8"))
        self.assert_every_adapter(NO_LINE)

    def test_utf16_and_utf32_indexes_are_no_line(self) -> None:
        content = f"{RECORD} {iso(-1)}\n- x\n"
        for name, data in {
            "UTF-16LE with BOM": b"\xff\xfe" + content.encode("utf-16-le"),
            "UTF-16BE with BOM": b"\xfe\xff" + content.encode("utf-16-be"),
            "UTF-16LE without BOM": content.encode("utf-16-le"),
            "UTF-32LE with BOM": b"\xff\xfe\x00\x00" + content.encode("utf-32-le"),
        }.items():
            with self.subTest(case=name):
                self.write_raw_index(data)
                self.assert_every_adapter(NO_LINE)

    def test_year_zero_and_years_outside_four_digits_are_no_line(self) -> None:
        self.assert_no_line_for_heads({
            value: f"{RECORD} {value}"
            for value in ("0000-03-01", "0000-02-29", "0000-01-15", "10000-01-01", "999-01-01")
        })

    def test_non_calendar_date_in_year_9999_is_no_line(self) -> None:
        self.assert_no_line_for_heads({"9999-02-29": f"{RECORD} 9999-02-29"})

    def test_year_one_is_read_with_the_same_day_count(self) -> None:
        self.write_index(f"{RECORD} 0001-01-01\n")
        found = self.judgments_for_all_adapters()
        for adapter, judged in found.items():
            with self.subTest(adapter=adapter):
                self.assertIsNotNone(judged)
                self.assertEqual(judged.last_run, "0001-01-01")
                self.assertIsNotNone(judged.days)
        self.assertEqual(len(set(found.values())), 1, found)

    def test_year_9999_is_read(self) -> None:
        """The last day of year 9999 is read, and is later than today: silent."""
        self.write_index(f"{RECORD} 9999-12-31\n")
        self.assert_every_adapter(None)


class ResolutionTest(ConsolidateSurfaceTestCase):
    def test_no_memory_directory_is_silent(self) -> None:
        """No memory file anywhere: no section is emitted."""
        self.assert_every_adapter(None)

    def test_index_alone_resolves_the_memory_directory(self) -> None:
        """A directory holding only MEMORY.md resolves as the memory directory.

        The higher-precedence candidate of each adapter holds a stale index and
        nothing else; the section surfaces from it. The marker set this
        observes is specified at `docs/6.-Adapter.md` (`MEMORY_DIR`
        resolution).
        """
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                workspace = self.new_workspace()
                higher, _lower = workspace.memory_candidates(adapter)
                workspace.write(higher, "MEMORY.md", f"{RECORD} {iso(-21)}\n")
                self.assertEqual(
                    judgment(consolidate_section(self.run_hook(adapter, workspace))),
                    Judgment(last_run=iso(-21), days=21),
                )


class ParityTest(ConsolidateSurfaceTestCase):
    def test_adapters_emit_the_same_section(self) -> None:
        """Same input, same body, the host spelling of the path aside."""
        self.write_index(self.index_with_last_run(-17))
        sections: dict[str, str | None] = {}
        for adapter in ADAPTERS:
            self.ws.clear_state()
            section = consolidate_section(self.run_hook(adapter))
            sections[adapter] = (
                None if section is None else _INDEX_PATH_RE.sub("<index>", section)
            )
        reference = sections["claude_sh"]
        self.assertIsNotNone(reference)
        for adapter, section in sections.items():
            with self.subTest(adapter=adapter):
                self.assertEqual(section, reference)

    def test_emission_names_the_index_it_read(self) -> None:
        self.write_index(self.index_with_last_run(-17))
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                self.ws.clear_state()
                section = consolidate_section(self.run_hook(adapter))
                self.assertIsNotNone(section)
                self.assertRegex(section, r"memory[\\/]MEMORY\.md")


class ReadOnlyTest(ConsolidateSurfaceTestCase):
    def test_hook_writes_nothing_into_memory(self) -> None:
        """Every memory file is byte-identical after each port's run."""
        self.write_index(self.index_with_last_run(-30))
        memory = self.ws.shared_memory
        before = {path.name: path.read_bytes() for path in memory.iterdir()}
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                self.ws.clear_state()
                self.assertIsNotNone(consolidate_section(self.run_hook(adapter)))
                after = {path.name: path.read_bytes() for path in memory.iterdir()}
                self.assertEqual(after, before)


class DiffOnlyTest(ConsolidateSurfaceTestCase):
    """Second startup run: the section and the marker, as `docs/6.-Adapter.md`
    (Diff-only output) specifies them for surfaces outside the diff set."""

    def run_twice(self, adapter: str, index: str) -> str:
        if adapter in ("claude_sh", "codex_sh") and not NODE:
            require_runtime("node", "diff-only state handling in the shell hooks")
        workspace = self.new_workspace()
        self.write_index(index, workspace)
        first = self.run_hook(adapter, workspace)
        self.assertIn(FAIL_SAFE_MARK, first, "first run should be the fail-safe full emit")
        second = self.run_hook(adapter, workspace)
        self.assertNotIn(
            FAIL_SAFE_MARK,
            second,
            f"{adapter} fell back to a full emit on the second run, so the "
            "marker branch was never evaluated",
        )
        return second

    def test_due_surface_re_emits_and_suppresses_the_marker(self) -> None:
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                second = self.run_twice(adapter, self.index_with_last_run(-20))
                self.assertEqual(
                    judgment(consolidate_section(second)),
                    Judgment(last_run=iso(-20), days=20),
                    "an unchanged index keeps the window open; the surface must re-emit",
                )
                self.assertIsNone(
                    no_new_material_marker(second),
                    "surfacing a due consolidate and declaring no new material in "
                    "the same emission is self-contradictory",
                )

    def test_recent_record_leaves_the_marker_reachable(self) -> None:
        """Control: without this, the suppression above proves nothing."""
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                second = self.run_twice(adapter, self.index_with_last_run(-1))
                self.assertIsNone(consolidate_section(second))
                self.assertIsNotNone(no_new_material_marker(second))


if __name__ == "__main__":
    unittest.main()
