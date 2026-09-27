"""Behavioural coverage for the disposition log retention trim.

Target = the three `adapter/*/hooks/on-session-start.*` implementations
(claude bash / codex bash / codex PowerShell). Issue #2107.

What this observes: `rules/evolution/promotion-judgment.md` Tally fixes the
retention of the `<!-- disposition log -->` section at 14 days from each line's
deletion date and places the removal on the adapter's hook, not on the writer.
Each case plants a tally file, runs one port, and reads the file back. Dates are
offsets from `date.today()`; `run_hook` discards a run that straddles midnight.

Not observed here: the tally expiry surface, which has its own module
(`test_on_session_start_tally_surface`). The fixture harness is reused from
`test_on_session_start_observation_surface` for the same reason that module
gives.
"""

from __future__ import annotations

import unittest

from test_on_session_start_observation_surface import (
    ADAPTERS,
    ObservationSurfaceTestCase,
    iso,
)


TALLY_NAME = "promotion_tally.md"
MARKER = "<!-- disposition log -->"


def log_line(day_offset: int, descriptor: str) -> str:
    return (
        f"- {iso(day_offset)} cluster `{descriptor}` "
        f"(first_observation {iso(day_offset - 3)}, 2 occurrences) -> sub-threshold deletion"
    )


def normalized_lines(raw: bytes) -> list[str]:
    """File content as lines, independent of CRLF and of a final newline.

    The awk ports end the last line with a newline when they rewrite the file and
    the PowerShell port writes it back as read, so byte identity across ports is
    asserted only where the file is not rewritten at all.
    """
    return raw.decode("utf-8").replace("\r\n", "\n").rstrip("\n").split("\n")


class DispositionLogRetentionTest(ObservationSurfaceTestCase):
    def write_tally(self, text: str, newline: str = "\n") -> None:
        target = self.ws.tally_dir / TALLY_NAME
        self.ws.tally_dir.mkdir(parents=True, exist_ok=True)
        target.write_bytes(text.replace("\n", newline).encode("utf-8"))

    def tally_bytes(self) -> bytes:
        return (self.ws.tally_dir / TALLY_NAME).read_bytes()

    def run_on_fresh_fixture(self, adapter: str, text: str, newline: str = "\n") -> bytes:
        self.new_workspace()
        self.write_tally(text, newline)
        self.run_hook(adapter)
        leftovers = sorted(p.name for p in self.ws.tally_dir.iterdir() if p.name != TALLY_NAME)
        self.assertEqual(leftovers, [], f"{adapter} left files beside the tally")
        return self.tally_bytes()

    def test_lines_past_14_days_are_removed_and_nothing_else(self) -> None:
        cluster = [
            "## cluster: still-open",
            f"first_observation: {iso(-40)}",
            f"expires: {iso(-37)}",
            "occurrences:",
            # Occurrence bullets carry dates too. This one sits above the
            # marker, 40 days old, and is expected to stay.
            f"  - {iso(-40)} self-eval#1 axis=frame",
            "",
        ]
        log = [
            MARKER,
            log_line(-30, "thirty-days"),
            log_line(-15, "fifteen-days"),
            log_line(-14, "fourteen-days"),
            log_line(-1, "yesterday"),
            log_line(0, "today"),
            log_line(3, "future"),
            # An impossible calendar date is not read as old.
            "- 2020-02-30 cluster `impossible-date` (first_observation 2020-02-27, 1 occurrences) -> sub-threshold deletion",
            "- undated bullet kept as written",
        ]
        text = "\n".join(cluster + log) + "\n"
        expected = cluster + [
            MARKER,
            log_line(-14, "fourteen-days"),
            log_line(-1, "yesterday"),
            log_line(0, "today"),
            log_line(3, "future"),
            "- 2020-02-30 cluster `impossible-date` (first_observation 2020-02-27, 1 occurrences) -> sub-threshold deletion",
            "- undated bullet kept as written",
        ]
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                self.assertEqual(normalized_lines(self.run_on_fresh_fixture(adapter, text)), expected)

    def test_a_heading_after_the_log_ends_the_trimmed_region(self) -> None:
        # The log is specified as the last section. A cluster written after it
        # anyway keeps its dated bullets: the region closes at the heading.
        text = "\n".join(
            [
                MARKER,
                log_line(-20, "old"),
                "## cluster: misplaced",
                "occurrences:",
                f"- {iso(-20)} self-eval#2 axis=frame",
            ]
        ) + "\n"
        expected = [
            MARKER,
            "## cluster: misplaced",
            "occurrences:",
            f"- {iso(-20)} self-eval#2 axis=frame",
        ]
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                self.assertEqual(normalized_lines(self.run_on_fresh_fixture(adapter, text)), expected)

    def test_file_is_left_byte_identical_when_nothing_is_old(self) -> None:
        # No final newline and CRLF endings: a rewrite would be visible in the
        # bytes, so equality shows the file was not rewritten.
        text = "\n".join([MARKER, log_line(-14, "edge"), log_line(-2, "recent")])
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                original = text.replace("\n", "\r\n").encode("utf-8")
                self.assertEqual(self.run_on_fresh_fixture(adapter, text, "\r\n"), original)

    def test_a_file_without_the_marker_is_not_touched(self) -> None:
        text = "\n".join(["## cluster: only", "occurrences:", f"- {iso(-60)} self-eval#3 axis=frame"]) + "\n"
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                self.assertEqual(self.run_on_fresh_fixture(adapter, text), text.encode("utf-8"))

    def test_crlf_lines_keep_their_endings_when_rewritten(self) -> None:
        text = "\n".join([MARKER, log_line(-20, "old"), log_line(-1, "recent")]) + "\n"
        expected = "\r\n".join([MARKER, log_line(-1, "recent")]) + "\r\n"
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                self.assertEqual(
                    self.run_on_fresh_fixture(adapter, text, "\r\n"),
                    expected.encode("utf-8"),
                )


if __name__ == "__main__":
    unittest.main()
