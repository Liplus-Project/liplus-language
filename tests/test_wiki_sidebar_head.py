"""The wiki sidebar's navigation head has its source in the repository.

Spec source: `skills/operations-on-wiki-sync/SKILL.md` Ownership Boundary (`_Sidebar.md`)
and Sync Steps step 4 / step 5, mirrored in `docs/4.-Operations.md` の「リリース後の
Wiki 同期」. Issue #1638.

What this observes, in two parts.

The head source against `docs/`. `docs/wiki/_Sidebar-head.md` is what the sync copies
above the wiki sidebar's Decision Structure section. A top-level `docs/` page it does
not link is a page the wiki sidebar will not list, and the sync's sidebar integrity
assertion stops the release on it. Checking here moves that stop to the PR that added
the page. Two names are not required in the head: `_Footer.md`, which the sidebar
integrity assertion also excludes, and `Decision-Structure.md`, whose sidebar row heads
the wiki-authored Decision Structure section rather than the head.

The rebuild itself. The step-4 reference algorithm and the step-5 apply snippet are
lifted out of the skill body and run against a synthetic repository and wiki, so what
is asserted is the literal an agent would follow: the head is replaced from the ref,
the wiki-authored section is carried over byte-for-byte, a wiki sidebar with no
boundary line stops the run with the sidebar untouched, and a ref with no head file
leaves the sidebar as the wiki holds it.
"""

from __future__ import annotations

import re
import subprocess
import tempfile
import unittest
from pathlib import Path

from test_wiki_sync_source_ref import (
    ROOT,
    _git,
    _write,
    apply_snippet,
    reference_algorithm,
    working_bash,
)


DOCS = ROOT / "docs"
HEAD = DOCS / "wiki" / "_Sidebar-head.md"
NOT_IN_HEAD = {"_Footer", "Decision-Structure"}
MARKDOWN_LINK = re.compile(r"\]\(([^)\s]+)\)")
NATIVE_LINK = re.compile(r"\[\[([^\]]+)\]\]")


def boundary_line() -> str:
    """The boundary literal as the skill's own reference algorithm writes it."""
    match = re.search(r"grep -nxF '([^']+)'", reference_algorithm())
    assert match is not None, "the reference algorithm names no boundary line"
    return match.group(1)


def link_targets(text: str) -> set[str]:
    targets = set(MARKDOWN_LINK.findall(text))
    for inner in NATIVE_LINK.findall(text):
        targets.add(inner.split("|", 1)[-1])
    return {target.split("#", 1)[0] for target in targets}


class HeadSourceTest(unittest.TestCase):
    """The head source links every top-level page, and only top-level pages."""

    def setUp(self) -> None:
        self.assertTrue(HEAD.exists(), f"{HEAD.relative_to(ROOT)} is missing")
        self.text = HEAD.read_text(encoding="utf-8")
        self.pages = {path.stem for path in DOCS.glob("*.md")}

    def test_every_top_level_page_is_in_the_head(self) -> None:
        missing = sorted(self.pages - NOT_IN_HEAD - link_targets(self.text))
        self.assertEqual(
            missing,
            [],
            "top-level docs/ pages absent from docs/wiki/_Sidebar-head.md "
            "(skills/operations-on-wiki-sync/SKILL.md Ownership Boundary, _Sidebar.md)",
        )

    def test_every_head_target_is_a_top_level_page(self) -> None:
        stray = sorted(link_targets(self.text) - self.pages)
        self.assertEqual(
            stray,
            [],
            "docs/wiki/_Sidebar-head.md links targets that are not top-level docs/ pages "
            "(skills/operations-on-wiki-sync/SKILL.md Ownership Boundary, _Sidebar.md)",
        )

    def test_the_head_does_not_carry_the_boundary_line(self) -> None:
        self.assertNotIn(
            boundary_line(),
            [line.rstrip("\r") for line in self.text.splitlines()],
            "the rebuild would locate the wiki-authored part inside the copied head",
        )

    def test_the_head_ends_with_one_newline(self) -> None:
        """The rebuild adds one empty line; a missing newline would glue the heading to the last item."""
        self.assertTrue(self.text.endswith("\n"))
        self.assertFalse(self.text.endswith("\n\n"))


class SidebarRebuildBehaviourTest(unittest.TestCase):
    """Run the skill's own snippets against a synthetic repository and wiki."""

    HEAD_V2 = "- [Home](Home)\n\n**Reference**\n\n- [A. Doc](A.-Doc)\n- [B. New](B.-New)\n"
    WIKI_HEAD = "- [Home](Home)\n\n**Reference**\n\n- [A. Doc](A.-Doc)\n"

    @classmethod
    def setUpClass(cls) -> None:
        cls.bash = working_bash()
        if cls.bash is None:
            raise unittest.SkipTest("no working bash found to run the snippets")
        cls.boundary = boundary_line()

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.base = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

        upstream = self.base / "upstream.git"
        self.clone = self.base / "clone"
        self.wiki = self.base / "wiki"
        self.wiki.mkdir()

        _git(self.base, "init", "--bare", "--initial-branch=main", str(upstream))
        _git(self.base, "clone", str(upstream), str(self.clone))
        _git(self.clone, "config", "user.name", "test")
        _git(self.clone, "config", "user.email", "test@example.invalid")

        index = "| [`entry-one`](https://github.com/o/r/wiki/entry-one) | first |\n"
        pages = {
            "Home.md": "home\n",
            "A.-Doc.md": "a\n",
            "B.-New.md": "b\n",
            "Decision-Structure.md": index,
        }
        for name, body in pages.items():
            _write(self.clone / "docs" / name, body)
            _write(self.wiki / name, body)
        _write(self.clone / "docs" / "wiki" / "_Sidebar-head.md", self.HEAD_V2)
        _git(self.clone, "add", "-A")
        _git(self.clone, "commit", "-m", "rev1")
        _git(self.clone, "push", "origin", "main")
        _git(self.clone, "fetch", "origin")

        self.tail = (
            f"{self.boundary}\n\n"
            "- [Decision Structure](Decision-Structure)\n"
            "- [entry one](entry-one)\n"
        )
        _write(self.wiki / "entry-one.md", "entry one body\n")
        _write(self.wiki / "_Sidebar.md", f"{self.WIKI_HEAD}\n{self.tail}")

    def _run(self) -> "subprocess.CompletedProcess[str]":
        script = "\n".join((reference_algorithm(), apply_snippet())).replace(
            "{tmpdir}", str(self.wiki).replace("\\", "/")
        )
        return subprocess.run(
            (self.bash, "-c", script),
            cwd=self.clone,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

    def _sidebar(self) -> str:
        return (self.wiki / "_Sidebar.md").read_bytes().decode("utf-8")

    def test_the_head_is_copied_and_the_section_is_kept(self) -> None:
        run = self._run()
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertEqual(self._sidebar(), f"{self.HEAD_V2}\n{self.tail}")

    def test_a_second_run_writes_nothing(self) -> None:
        self._run()
        after_first = (self.wiki / "_Sidebar.md").stat().st_mtime_ns
        run = self._run()
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertEqual(self._sidebar(), f"{self.HEAD_V2}\n{self.tail}")
        self.assertEqual((self.wiki / "_Sidebar.md").stat().st_mtime_ns, after_first)

    def test_a_missing_boundary_stops_with_the_sidebar_untouched(self) -> None:
        before = "- [Home](Home)\n- [entry one](entry-one)\n"
        _write(self.wiki / "_Sidebar.md", before)
        run = self._run()
        self.assertNotEqual(run.returncode, 0, "the rebuild ran with no located section")
        self.assertIn("sidebar:", run.stdout)
        self.assertEqual(self._sidebar(), before)

    def test_a_ref_without_the_head_leaves_the_sidebar_alone(self) -> None:
        (self.clone / "docs" / "wiki" / "_Sidebar-head.md").unlink()
        _git(self.clone, "add", "-A")
        _git(self.clone, "commit", "-m", "rev2")
        _git(self.clone, "push", "origin", "main")
        _git(self.clone, "fetch", "origin")
        before = self._sidebar()
        run = self._run()
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertEqual(self._sidebar(), before)


if __name__ == "__main__":
    unittest.main()
