"""Behavioural coverage for the cold-start promotion tally expiry surface.

Target = the three `adapter/*/hooks/on-session-start.*` implementations
(claude bash / codex bash / codex PowerShell). Issue #1894.

The surface exists because `rules/evolution/promotion-judgment.md` Threshold
Rules fixed the verdict for a closed 3d window without fixing who reaches it or
when. The contract that repairs that is `rules/evolution/cold-start-synthesis.md`
Promotion Tally Expiry Surface, and this file asserts the three ports implement
it identically.

What is pinned and what is not
------------------------------
The contract fixes the date conditions (`expires <= today` surfaces,
`expires < today` is overdue, overdue wins) and that the occurrence count is
carried. Presentation is delegated to the adapter by the same section
("Material gathering and concrete surfacing logic belong to the adapter
cold-start path"), so the assertions below read the judgment out of the
emission -- which descriptor surfaced, under which label, with which count --
and do not match the banner text, the bullet prefix, or the order of the lines.
The `DUE` / `OVERDUE` label words are matched because `docs/6.-Adapter.md`
specifies them.

The fixture, the hook runner and the workspace layout are reused from
`test_on_session_start_observation_surface`: the two surfaces run in the same
hooks over the same workspace layout, so a second copy of that harness would be
the copy that drifts. Their file resolution is not shared -- since #2018 the
tally resolves under `$HOME/.liplus/tally/` and the observation surface through
`MEMORY_DIR` -- which is itself asserted by `TallyResolutionTest` below.
"""

from __future__ import annotations

import re
import unittest
from typing import NamedTuple

from test_on_session_start_observation_surface import (
    ADAPTERS,
    NO_NEW_MATERIAL,
    ObservationSurfaceTestCase,
    emitted_sections,
    iso,
    observation_section,
)


def tally_section(hook_output: str) -> str | None:
    """Body of the tally expiry section, or None when the hook stayed silent.

    Located by topic rather than by exact banner text, for the same reason the
    observation-surface module does it: the banner is an adapter choice.
    """
    for banner, body in emitted_sections(hook_output):
        if "tally" in banner.lower():
            return body
    return None


class SurfacedCluster(NamedTuple):
    label: str          # "DUE" or "OVERDUE"
    expires: str        # the ISO date the hook reported back
    occurrences: int    # the count the hook derived from the fixture


_LABEL_RE = re.compile(r"\b(OVERDUE|DUE)\b")
# The resolved tally path, as the emission names it. Matched by its filename
# rather than by a spelling: the three ports render one path three ways (an MSYS
# path from the bash ports, a drive-letter one from PowerShell).
_TALLY_PATH_RE = re.compile(r"\S*promotion_tally\.md")
_EXPIRES_RE = re.compile(r"expires\s+(\d{4}-\d{2}-\d{2})")
_COUNT_RE = re.compile(r"(\d+)")


def surfaced_clusters(
    section_body: str | None,
    descriptors: tuple[str, ...],
) -> dict[str, SurfacedCluster]:
    """Descriptor -> what the hook judged about it.

    A descriptor absent from the result is a cluster the hook did not surface.
    Lines are matched by descriptor rather than by position, so the order of the
    emission stays an adapter choice.
    """
    found: dict[str, SurfacedCluster] = {}
    if not section_body:
        return found
    for line in section_body.split("\n"):
        for descriptor in descriptors:
            if descriptor not in line:
                continue
            label = _LABEL_RE.search(line)
            if label is None:
                raise AssertionError(f"no DUE/OVERDUE label on {line!r}")
            expires = _EXPIRES_RE.search(line)
            # The count is the last bare integer after the descriptor; the only
            # other numbers on the line sit inside the ISO date, which precedes
            # the descriptor in every port's rendering and is claimed by
            # `_EXPIRES_RE` regardless.
            tail = line.split(descriptor, 1)[1]
            count = _COUNT_RE.findall(tail)
            found[descriptor] = SurfacedCluster(
                label=label.group(1),
                expires=expires.group(1) if expires else "",
                occurrences=int(count[-1]) if count else -1,
            )
    return found


class TallySurfaceTestCase(ObservationSurfaceTestCase):
    """Fixture writer + per-adapter runner for the tally surface."""

    def write_tally_file(self, *clusters: tuple[str, str, int]) -> tuple[str, ...]:
        """Write `promotion_tally.md` from (descriptor, expires, occurrences).

        Written to the host-level tally directory, which is where every port
        resolves it (#2018). Nothing is planted in memory: the tally surface no
        longer resolves through `MEMORY_DIR`, so these cases observe parsing and
        classification only. Resolution has its own case below.
        """
        lines: list[str] = []
        descriptors: list[str] = []
        for descriptor, expires, occurrences in clusters:
            descriptors.append(descriptor)
            lines.append(f"## cluster: {descriptor}")
            lines.append(f"first_observation: {iso(-3)}")
            lines.append(f"expires: {expires}")
            lines.append("occurrences:")
            for index in range(occurrences):
                lines.append(f"  - {iso(-3)} self-eval#{index} axis=frame")
            lines.append("")
        self.ws.write(self.ws.tally_dir, "promotion_tally.md", "\n".join(lines))
        return tuple(descriptors)

    def without_resolved_path(self, section: str | None) -> str | None:
        """The section with the resolved tally path replaced by a fixed token.

        Every port names the file it read, and one path has three spellings
        across the three ports. Parity is over the judgment, not over the host
        spelling of a path; the path itself is asserted separately below.
        """
        if section is None:
            return None
        return _TALLY_PATH_RE.sub("<tally file>", section)

    def tally_for_all_adapters(self) -> dict[str, str | None]:
        sections: dict[str, str | None] = {}
        for adapter in ADAPTERS:
            self.ws.clear_state()
            sections[adapter] = tally_section(self.run_hook(adapter))
        return sections


class ExpiryJudgmentTest(TallySurfaceTestCase):
    def test_overdue_due_and_open_windows_are_classified(self) -> None:
        """`expires < today` -> OVERDUE, `expires == today` -> DUE, later -> silent."""
        descriptors = self.write_tally_file(
            ("window closed two days ago", iso(-2), 4),
            ("window closes today", iso(0), 2),
            ("window still open", iso(+3), 1),
        )
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                self.ws.clear_state()
                clusters = surfaced_clusters(
                    tally_section(self.run_hook(adapter)), descriptors
                )
                self.assertEqual(clusters[descriptors[0]].label, "OVERDUE")
                self.assertEqual(clusters[descriptors[1]].label, "DUE")
                self.assertNotIn(descriptors[2], clusters)

    def test_occurrence_count_is_carried(self) -> None:
        """The count selects the Threshold Rules row, so it must reach the reader."""
        descriptors = self.write_tally_file(("counted cluster", iso(-1), 4))
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                self.ws.clear_state()
                clusters = surfaced_clusters(
                    tally_section(self.run_hook(adapter)), descriptors
                )
                self.assertEqual(clusters[descriptors[0]].occurrences, 4)

    def test_notes_bullets_are_not_counted_as_occurrences(self) -> None:
        """occurrences: and notes: both use "- " bullets; only the former counts.

        Regression for #1929: the aggregation counted every "- " line seen
        after the cluster header, so a cluster's notes: section inflated its
        reported count past the Threshold Rules row the real occurrence count
        falls under.
        """
        self.ws.write(
            self.ws.tally_dir,
            "promotion_tally.md",
            "\n".join(
                [
                    "## cluster: real count is four",
                    f"first_observation: {iso(-3)}",
                    f"expires: {iso(-1)}",
                    "occurrences:",
                    f"  - {iso(-3)} self-eval#0 axis=frame",
                    f"  - {iso(-3)} self-eval#1 axis=frame",
                    f"  - {iso(-2)} self-eval#2 axis=frame",
                    f"  - {iso(-2)} self-eval#3 axis=frame",
                    "",
                    "notes:",
                    "  - an aside that should not be counted",
                    "  - another aside line",
                    "  - a third aside line",
                    "",
                ]
            ),
        )
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                self.ws.clear_state()
                clusters = surfaced_clusters(
                    tally_section(self.run_hook(adapter)), ("real count is four",)
                )
                self.assertEqual(clusters["real count is four"].occurrences, 4)

    def test_disposition_log_bullets_are_not_counted_as_occurrences(self) -> None:
        """The region closes on its own content, not on the neighbour's shape.

        Regression for #1958: the counted region closed only at a top-level
        `key:` line or a `##` heading. The `<!-- disposition log -->` section
        `rules/evolution/promotion-judgment.md` Tally places at the end of the
        file is neither, so when the last cluster's final field was
        `occurrences:`, the log's `- ` lines were added to that cluster's count
        -- the value that selects which Threshold Rules row applies.
        """
        self.ws.write(
            self.ws.tally_dir,
            "promotion_tally.md",
            "\n".join(
                [
                    "## cluster: real count is two",
                    f"first_observation: {iso(-3)}",
                    f"expires: {iso(-1)}",
                    "occurrences:",
                    f"  - {iso(-3)} self-eval#0 axis=frame",
                    f"  - {iso(-2)} self-eval#1 axis=frame",
                    "",
                    "<!-- disposition log -->",
                    "- 2026-09-10 cluster `gone one` (first_observation 2026-09-07, 2 occurrences) -> deleted",
                    "- 2026-09-11 cluster `gone two` (first_observation 2026-09-08, 4 occurrences) -> issue #1",
                    "- 2026-09-12 cluster `gone three` (first_observation 2026-09-09, 5 occurrences) -> issue #2",
                    "",
                ]
            ),
        )
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                self.ws.clear_state()
                clusters = surfaced_clusters(
                    tally_section(self.run_hook(adapter)), ("real count is two",)
                )
                self.assertEqual(clusters["real count is two"].occurrences, 2)

    def test_blank_separated_occurrence_bullets_are_all_counted(self) -> None:
        """A blank line does not close the region; closing there under-counts.

        The opposite failure of the case above, and the reason the close
        condition is "neither a bullet nor blank" rather than "not a bullet":
        occurrence bullets appear blank-separated in the real tally file.
        """
        self.ws.write(
            self.ws.tally_dir,
            "promotion_tally.md",
            "\n".join(
                [
                    "## cluster: blank separated count is four",
                    f"first_observation: {iso(-3)}",
                    f"expires: {iso(-1)}",
                    "occurrences:",
                    f"  - {iso(-3)} self-eval#0 axis=frame",
                    "",
                    f"  - {iso(-3)} self-eval#1 axis=frame",
                    f"  - {iso(-2)} self-eval#2 axis=frame",
                    "",
                    f"  - {iso(-2)} self-eval#3 axis=frame",
                    "",
                ]
            ),
        )
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                self.ws.clear_state()
                clusters = surfaced_clusters(
                    tally_section(self.run_hook(adapter)),
                    ("blank separated count is four",),
                )
                self.assertEqual(
                    clusters["blank separated count is four"].occurrences, 4
                )

    def test_next_cluster_heading_still_closes_the_region(self) -> None:
        """The `##` boundary behaviour is unchanged by the new close condition.

        A cluster whose last field is `occurrences:` must not absorb the
        following cluster's bullets, and the following cluster must still be
        parsed with its own count.
        """
        self.ws.write(
            self.ws.tally_dir,
            "promotion_tally.md",
            "\n".join(
                [
                    "## cluster: first has two",
                    f"expires: {iso(-1)}",
                    "occurrences:",
                    f"  - {iso(-3)} self-eval#0 axis=frame",
                    f"  - {iso(-2)} self-eval#1 axis=frame",
                    "",
                    "## cluster: second has three",
                    f"expires: {iso(-1)}",
                    "occurrences:",
                    f"  - {iso(-3)} self-eval#0 axis=frame",
                    f"  - {iso(-2)} self-eval#1 axis=frame",
                    f"  - {iso(-1)} self-eval#2 axis=frame",
                    "",
                ]
            ),
        )
        descriptors = ("first has two", "second has three")
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                self.ws.clear_state()
                clusters = surfaced_clusters(
                    tally_section(self.run_hook(adapter)), descriptors
                )
                self.assertEqual(clusters["first has two"].occurrences, 2)
                self.assertEqual(clusters["second has three"].occurrences, 3)

    def test_no_cluster_past_its_window_is_a_silent_skip(self) -> None:
        self.write_tally_file(("window still open", iso(+2), 3))
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                self.ws.clear_state()
                self.assertIsNone(tally_section(self.run_hook(adapter)))

    def test_absent_tally_file_is_a_silent_skip(self) -> None:
        self.ws.write(self.ws.shared_memory, "self-evaluation_log.md", "# log\n")
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                self.ws.clear_state()
                self.assertIsNone(tally_section(self.run_hook(adapter)))


class AdapterParityTest(TallySurfaceTestCase):
    def test_three_ports_agree_on_identical_input(self) -> None:
        self.write_tally_file(
            ("overdue cluster", iso(-4), 5),
            ("due cluster", iso(0), 3),
            ("open cluster", iso(+1), 1),
        )
        sections = self.tally_for_all_adapters()
        reference = sections["claude_sh"]
        self.assertIsNotNone(reference)
        for adapter, section in sections.items():
            with self.subTest(adapter=adapter):
                self.assertEqual(
                    self.without_resolved_path(section),
                    self.without_resolved_path(reference),
                    f"{adapter} disagrees with claude_sh",
                )

    def test_every_port_names_the_file_it_read(self) -> None:
        """Each port names the path it resolved, in its own emission.

        The claim is fixed at `rules/evolution/cold-start-synthesis.md` Promotion
        Tally Expiry Surface ("The emission names the resolved path"). The three
        ports spell one path three ways, so what is observed here is that each
        emission carries a `promotion_tally.md` under a `.liplus` directory, not
        that the three strings agree.
        """
        self.write_tally_file(("named path", iso(-1), 3))
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                self.ws.clear_state()
                section = tally_section(self.run_hook(adapter))
                self.assertIsNotNone(section)
                match = _TALLY_PATH_RE.search(section)
                self.assertIsNotNone(match, f"no path named in {section!r}")
                named = match.group(0).replace("\\", "/").lower()
                self.assertTrue(
                    named.endswith(".liplus/tally/promotion_tally.md"), named
                )

    def test_header_case_is_read_case_sensitively(self) -> None:
        """`## Cluster:` is not the header literal; no port may accept it.

        The PowerShell port defaults to case-insensitive comparison, which split
        the three adapters on the sibling observation surface (#1562 F2). The
        same asymmetry is reachable here.
        """
        self.ws.write(
            self.ws.tally_dir,
            "promotion_tally.md",
            "\n".join(
                [
                    "## Cluster: wrong case header",
                    f"Expires: {iso(-2)}",
                    "occurrences:",
                    f"  - {iso(-2)} self-eval#0 axis=frame",
                    "",
                ]
            ),
        )
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                self.ws.clear_state()
                self.assertIsNone(tally_section(self.run_hook(adapter)))

    def test_empty_descriptor_is_dropped_by_every_port(self) -> None:
        """A `## cluster:` header with no descriptor names nothing to judge."""
        self.ws.write(
            self.ws.tally_dir,
            "promotion_tally.md",
            "\n".join(
                [
                    "## cluster:",
                    f"expires: {iso(-2)}",
                    "occurrences:",
                    f"  - {iso(-2)} self-eval#0 axis=frame",
                    "",
                ]
            ),
        )
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                self.ws.clear_state()
                self.assertIsNone(tally_section(self.run_hook(adapter)))


class TallyResolutionTest(TallySurfaceTestCase):
    """Where each port looks for the tally file (#2018).

    The tally is one counting surface per host while a memory directory resolves
    per workspace, so the two resolutions are separate. The separation is asserted
    from both sides: the tally is found with no memory directory at all, and a
    tally sitting at the pre-#2018 memory path is not found.

    The memory-side resolution is not asserted here, and its marker set is
    unchanged by #2018: a directory holding nothing but a pre-#2018 tally still
    claims `MEMORY_DIR`, which is the state `test_tally_at_the_pre_move_memory_path
    _is_not_read` runs against.
    """

    def cluster_text(self, descriptor: str) -> str:
        return "\n".join(
            [
                f"## cluster: {descriptor}",
                f"expires: {iso(-1)}",
                "occurrences:",
                f"  - {iso(-1)} self-eval#0 axis=frame",
                "",
            ]
        )

    def test_tally_resolves_with_no_memory_directory_at_all(self) -> None:
        """Nothing is planted in memory, and the tally must still be reached.

        Before #2018 the file was read through `MEMORY_DIR`, so an unresolved
        memory directory took this surface silent with it.
        """
        descriptors = ("lone cluster",)
        self.ws.write(
            self.ws.tally_dir, "promotion_tally.md", self.cluster_text(descriptors[0])
        )
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                self.ws.clear_state()
                clusters = surfaced_clusters(
                    tally_section(self.run_hook(adapter)), descriptors
                )
                self.assertIn(descriptors[0], clusters)

    def test_tally_at_the_pre_move_memory_path_is_not_read(self) -> None:
        """No fallback to `MEMORY_DIR/promotion_tally.md`.

        A path that still resolves is a path still written to, and a tally
        written into a memory directory is a count the rest of the host does not
        add to. The file being absent is what tells a caller reaching for the old
        path, so the surface stays silent here rather than reading it.
        """
        self.ws.write(self.ws.shared_memory, "self-evaluation_log.md", "# log\n")
        for candidate in (
            self.ws.claude_primary,
            self.ws.shared_memory,
            self.ws.codex_secondary,
        ):
            self.ws.write(
                candidate, "promotion_tally.md", self.cluster_text("old path cluster")
            )
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                self.ws.clear_state()
                self.assertIsNone(tally_section(self.run_hook(adapter)))



class NoNewMaterialMarkerTest(TallySurfaceTestCase):
    def test_surfaced_cluster_suppresses_the_marker(self) -> None:
        """Pairing an overdue cluster with "no new material" is self-contradictory.

        Run twice: the first run populates the diff state, the second is the one
        where every section is unchanged and the marker branch is reachable.
        """
        descriptors = self.write_tally_file(("overdue cluster", iso(-2), 4))
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                self.ws.clear_state()
                self.run_hook(adapter)
                output = self.run_hook(adapter)
                self.assertNotIn(NO_NEW_MATERIAL, output)
                clusters = surfaced_clusters(tally_section(output), descriptors)
                self.assertIn(descriptors[0], clusters)


if __name__ == "__main__":
    unittest.main()
