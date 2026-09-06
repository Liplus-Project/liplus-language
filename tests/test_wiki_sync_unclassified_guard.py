"""The wiki sync's `unclassified` STOP has an executable form, and it classifies.

Spec source: `skills/operations-on-wiki-sync/SKILL.md` Sync Steps step 4, mirrored
in `docs/4.-Operations.md` の「リリース後の Wiki 同期」手順. Issue #1806.

The defect this pins. The STOP stood on one prose sentence. The step-4 reference
implementation held no `exit`, no guard clause, and no read of `$unclassified` at
all: the array filled up and the block returned 0. Nothing downstream re-detected
it either — the first Pre-sync Verification assertion reads `git status --short`,
and an unclassified page is tracked and unmodified in the wiki clone, so it shows
no line. `rules/model/subtractive-structural-beauty.md` Application notes sends a
procedure whose execution by a future agent is not guaranteed back to be replaced
by a structure, and this is that shape.

What the guard protects. Not deletion. Step 5 is a copy loop with no remove, so a
missed STOP took nothing off the wiki even when the remaining steps were run
mechanically; what it left was a silent pass-through — a stale page standing while
the mirror reported as synced. The assertions below hold both halves: the run
stops non-zero, and every page is still there when it does.

The classification. Each escalated name is reported with whether its slug has
history under `docs/` on the source ref. History present reads as a leftover from
a docs/-side rename or removal; history absent reads as a wiki-source page whose
deletion would destroy the source. Both branches must appear, because the reading
is what shortens the human's move from investigation to confirmation, and a
classifier that only ever emits one verdict has not made that move any shorter.
Neither branch deletes: naming which page is which stays the human's.
"""

from __future__ import annotations

import re
import subprocess
import tempfile
import unittest
from pathlib import Path

from test_wiki_sync_source_ref import (
    DOCS_MIRROR,
    SKILL,
    _git,
    _write,
    reference_algorithm,
    working_bash,
)


class UnclassifiedGuardBehaviourTest(unittest.TestCase):
    """Run the skill's own step-4 snippet against a wiki holding both kinds of orphan."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.bash = working_bash()
        if cls.bash is None:
            raise unittest.SkipTest("no working bash found to run the snippet")

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

        # Revision 1 — `Leftover-Rename.md` exists under docs/ here and nowhere later,
        # so the ref carries an A and a D for it: the history-present branch.
        _write(self.clone / "docs" / "Home.md", "home\n")
        _write(self.clone / "docs" / "Leftover-Rename.md", "old name\n")
        _write(self.clone / "docs" / "Decision-Structure.md", index)
        _git(self.clone, "add", "-A")
        _git(self.clone, "commit", "-m", "rev1")

        # Revision 2 — the rename lands; the old docs/ name is gone from the tree.
        _write(self.clone / "docs" / "New-Name.md", "new name\n")
        (self.clone / "docs" / "Leftover-Rename.md").unlink()
        _git(self.clone, "add", "-A")
        _git(self.clone, "commit", "-m", "rev2")
        _git(self.clone, "push", "origin", "main")
        _git(self.clone, "fetch", "origin")

        # The wiki: docs/-owned pages, a wiki-only entry the index names, and the two
        # orphans. `unmerged-entry.md` is the benign case — a Decision Structure entry
        # pushed to the wiki before its index row merged — and has never been a docs/
        # file, so it takes the history-absent branch.
        _write(self.wiki / "Home.md", "home\n")
        _write(self.wiki / "New-Name.md", "new name\n")
        _write(self.wiki / "Decision-Structure.md", index)
        _write(self.wiki / "_Sidebar.md", "sidebar\n")
        _write(self.wiki / "entry-one.md", "entry one body\n")
        _write(self.wiki / "Leftover-Rename.md", "old name\n")
        _write(self.wiki / "unmerged-entry.md", "entry pushed ahead of its index row\n")

        self.pages_before = sorted(p.name for p in self.wiki.glob("*.md"))

    def _run_guard(self) -> "subprocess.CompletedProcess[str]":
        script = reference_algorithm().replace(
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

    def _reported(self) -> dict:
        """name -> the parenthesised reading the guard printed for it."""
        run = self._run_guard()
        found = {}
        for line in run.stdout.splitlines():
            match = re.match(r"unclassified: (?P<name>\S+) \((?P<reading>.+)\)$", line)
            if match:
                found[match.group("name")] = match.group("reading")
        return found

    def test_a_non_empty_unclassified_set_exits_non_zero(self) -> None:
        run = self._run_guard()
        self.assertNotEqual(
            run.returncode,
            0,
            "the block returned success with unclassified pages standing: "
            f"stdout={run.stdout!r} stderr={run.stderr!r}",
        )

    def test_every_escalated_page_is_named(self) -> None:
        self.assertEqual(
            sorted(self._reported()), ["Leftover-Rename.md", "unmerged-entry.md"]
        )

    def test_nothing_on_the_wiki_is_deleted(self) -> None:
        self._run_guard()
        self.assertEqual(
            sorted(p.name for p in self.wiki.glob("*.md")), self.pages_before
        )

    def test_docs_history_present_and_absent_are_told_apart(self) -> None:
        reported = self._reported()
        self.assertIn("history present", reported["Leftover-Rename.md"])
        self.assertIn("no docs/ history", reported["unmerged-entry.md"])

    def test_an_empty_unclassified_set_passes_through(self) -> None:
        """Without this, an unconditional exit would satisfy every assertion above."""
        (self.wiki / "Leftover-Rename.md").unlink()
        (self.wiki / "unmerged-entry.md").unlink()
        run = self._run_guard()
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(self._reported(), {})


class GuardSpecTextTest(unittest.TestCase):
    """The two literals around the guard, on both surfaces."""

    def setUp(self) -> None:
        self.skill = SKILL.read_text(encoding="utf-8")
        self.steps = self.skill[self.skill.index("## Sync Steps") :]
        mirror = DOCS_MIRROR.read_text(encoding="utf-8")
        section = mirror[mirror.index("#### リリース後の Wiki 同期") :]
        self.mirror = section[: section.index("**Windows 固有")]

    def test_the_no_drift_condition_carries_no_unclassified_term(self) -> None:
        """Dead after the guard: step 5 is only reached with the set empty."""
        no_drift = re.search(r"^.*no drift.*$", self.steps, re.MULTILINE)
        assert no_drift is not None
        self.assertIn("Empty `to_copy` = no drift", no_drift.group(0))
        self.assertNotIn("empty `unclassified`", no_drift.group(0))

    def test_the_guard_reads_docs_history_from_the_source_ref(self) -> None:
        algorithm = reference_algorithm()
        self.assertIn("--diff-filter=AD", algorithm)
        self.assertIn('"$SRC_REF" -- "docs/$name"', algorithm)

    def test_the_mirror_carries_the_guard_and_the_shrunk_condition(self) -> None:
        self.assertIn("非ゼロ終了", self.mirror)
        self.assertIn("--diff-filter=AD", self.mirror)
        self.assertIn("to_copy が空 = drift なし", self.mirror)


if __name__ == "__main__":
    unittest.main()
