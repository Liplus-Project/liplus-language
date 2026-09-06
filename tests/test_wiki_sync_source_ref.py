"""The wiki sync reads `docs/` from `origin/main`, never from the caller's working tree.

Spec source: `skills/operations-on-wiki-sync/SKILL.md` Sync Steps, mirrored in
`docs/4.-Operations.md` の「リリース後の Wiki 同期」手順. Issue #1805.

The defect this pins. The mirror source used to be whatever `docs/` the caller's
working tree happened to hold. A clone sitting behind `origin/main` — a stale
checkout, or the detached HEAD that tag-based Li+ sync leaves behind — is a state
normal operation reaches, and mirroring from it rolls merged `docs/` changes back
on the wiki. None of the three Pre-sync Verification assertions report it: they
measure ownership and reference resolution, and an old body is owned exactly as a
current one is. The repair names the source by ref instead of adding a fourth
assertion, so reading a stale tree is structurally unreachable rather than
checked for.

What is pinned. The reference algorithm and the apply snippet are lifted out of
the skill body and executed against a synthetic repository whose working tree is
deliberately stale, so the assertions read the behaviour of the literal an agent
would follow rather than a paraphrase of it. Three separately-failing properties:
the enumeration comes from the ref (a file added upstream is copied even though
the working tree has never seen it), the content comes from the ref (a file the
working tree holds at an older revision is mirrored at its upstream content), and
`docs/Decision-Structure.md` — which builds the wiki-only list — is read from the
ref as well (an entry indexed only upstream is not escalated as unclassified).

The fetch step is pinned textually. It is a STOP gate over a network call, so
there is no in-process behaviour to observe; what the check can hold is that the
procedure names the fetch ahead of every ref read and names failure as STOP.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "operations-on-wiki-sync" / "SKILL.md"
DOCS_MIRROR = ROOT / "docs" / "4.-Operations.md"
SOURCE_REF = "origin/main"


def _fenced_block_after(body: str, marker: str) -> str:
    """The first ``` fence opened after `marker`, dedented."""
    start = body.index(marker)
    fence = re.compile(r"^\s*```\s*$", re.MULTILINE)
    opening = fence.search(body, start)
    assert opening is not None, f"no fence opens after {marker!r}"
    closing = fence.search(body, opening.end())
    assert closing is not None, f"fence opened after {marker!r} is never closed"
    return textwrap.dedent(body[opening.end() : closing.start()]).strip("\n")


def reference_algorithm() -> str:
    return _fenced_block_after(SKILL.read_text(encoding="utf-8"), "Reference algorithm:")


def apply_snippet() -> str:
    return _fenced_block_after(
        SKILL.read_text(encoding="utf-8"), "5. Apply the drift set"
    )


def _bash_candidates() -> list[str]:
    """Every plausible bash, in preference order.

    `bash` on PATH is the answer on Linux and in CI. On a Windows host it can
    resolve to the WSL launcher, which fails before running anything when no
    distribution is installed, so Git's own bash is tried alongside it.
    """
    candidates: list[str] = []
    on_path = shutil.which("bash")
    if on_path:
        candidates.append(on_path)
    git = shutil.which("git")
    if git:
        root = Path(git).resolve().parent.parent
        for relative in ("bin/bash.exe", "usr/bin/bash.exe"):
            candidate = root / relative
            if candidate.exists():
                candidates.append(str(candidate))
    return candidates


def working_bash() -> str | None:
    for candidate in _bash_candidates():
        try:
            probe = subprocess.run(
                (candidate, "-c", "shopt -s nullglob && echo ok"),
                capture_output=True,
                timeout=30,
            )
        except (OSError, subprocess.SubprocessError):
            continue
        if probe.returncode == 0 and probe.stdout.strip() == b"ok":
            return candidate
    return None


def _git(cwd: Path, *args: str) -> None:
    subprocess.run(
        ("git", *args),
        cwd=cwd,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


class SourceRefBehaviourTest(unittest.TestCase):
    """Run the skill's own snippets against a stale working tree."""

    @classmethod
    def setUpClass(cls) -> None:
        if shutil.which("git") is None:
            raise unittest.SkipTest("git is required to run the snippets")
        cls.bash = working_bash()
        if cls.bash is None:
            raise unittest.SkipTest("no working bash found to run the snippets")

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

        # Revision 1 — what the stale working tree will hold.
        _write(self.clone / "docs" / "Home.md", "home v1\n")
        _write(self.clone / "docs" / "Retired.md", "retired page\n")
        _write(
            self.clone / "docs" / "Decision-Structure.md",
            "| [`entry-one`](https://github.com/o/r/wiki/entry-one) | first |\n",
        )
        _git(self.clone, "add", "-A")
        _git(self.clone, "commit", "-m", "rev1")
        _git(self.clone, "push", "origin", "main")
        self.rev1 = subprocess.run(
            ("git", "rev-parse", "HEAD"),
            cwd=self.clone,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

        # Revision 2 — merged upstream, never checked out here.
        _write(self.clone / "docs" / "Home.md", "home v2\n")
        _write(self.clone / "docs" / "Added.md", "added upstream\n")
        (self.clone / "docs" / "Retired.md").unlink()
        _write(
            self.clone / "docs" / "Decision-Structure.md",
            "| [`entry-one`](https://github.com/o/r/wiki/entry-one) | first |\n"
            "| [`entry-two`](https://github.com/o/r/wiki/entry-two) | second |\n",
        )
        _git(self.clone, "add", "-A")
        _git(self.clone, "commit", "-m", "rev2")
        _git(self.clone, "push", "origin", "main")

        # The observed state: detached HEAD, behind origin/main, working tree clean.
        _git(self.clone, "checkout", "--detach", self.rev1)

        # The wiki side mirrors revision 1, plus its wiki-only pages.
        _write(self.wiki / "Home.md", "home v1\n")
        _write(self.wiki / "Retired.md", "retired page\n")
        _write(
            self.wiki / "Decision-Structure.md",
            "| [`entry-one`](https://github.com/o/r/wiki/entry-one) | first |\n",
        )
        _write(self.wiki / "_Sidebar.md", "sidebar\n")
        _write(self.wiki / "entry-one.md", "entry one body\n")
        _write(self.wiki / "entry-two.md", "entry two body\n")

    def _run_snippets(self) -> tuple[list[str], list[str]]:
        script = "\n".join(
            (
                reference_algorithm(),
                'for n in "${to_copy[@]}"; do echo "TO_COPY $n"; done',
                'for n in "${unclassified[@]}"; do echo "UNCLASSIFIED $n"; done',
                # The apply runs unconditionally here. Step 5's STOP on a non-empty
                # `unclassified` is prose the agent obeys, not a branch inside the
                # snippet, and what these assertions read is where a copied byte came
                # from — which the escalation ordering does not bear on.
                apply_snippet(),
            )
        ).replace("{tmpdir}", str(self.wiki).replace("\\", "/"))
        run = subprocess.run(
            (self.bash, "-c", script),
            cwd=self.clone,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        self.assertEqual(run.returncode, 0, run.stderr)
        to_copy = [
            line.split(" ", 1)[1]
            for line in run.stdout.splitlines()
            if line.startswith("TO_COPY ")
        ]
        unclassified = [
            line.split(" ", 1)[1]
            for line in run.stdout.splitlines()
            if line.startswith("UNCLASSIFIED ")
        ]
        return to_copy, unclassified

    def test_the_working_tree_really_is_stale(self) -> None:
        """Without this, every assertion below could pass on a current tree."""
        self.assertEqual(
            (self.clone / "docs" / "Home.md").read_text(encoding="utf-8"), "home v1\n"
        )
        self.assertFalse((self.clone / "docs" / "Added.md").exists())
        self.assertTrue((self.clone / "docs" / "Retired.md").exists())
        head = subprocess.run(
            ("git", "symbolic-ref", "-q", "HEAD"),
            cwd=self.clone,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(head.returncode, 0, "HEAD is expected to be detached")

    def test_content_is_mirrored_from_the_ref_not_the_stale_tree(self) -> None:
        to_copy, _ = self._run_snippets()
        self.assertIn("Home.md", to_copy)
        self.assertEqual(
            (self.wiki / "Home.md").read_text(encoding="utf-8"),
            "home v2\n",
            "the wiki was written from the working tree, rolling the page back",
        )

    def test_enumeration_comes_from_the_ref(self) -> None:
        to_copy, unclassified = self._run_snippets()
        self.assertIn(
            "Added.md",
            to_copy,
            "a page added upstream was missed because the tree has never seen it",
        )
        self.assertIn(
            "Retired.md",
            unclassified,
            "a page removed upstream must reach the human, not stay docs/-owned",
        )

    def test_the_decision_structure_index_is_read_from_the_ref(self) -> None:
        _, unclassified = self._run_snippets()
        self.assertNotIn(
            "entry-two.md",
            unclassified,
            "the wiki-only list was built from the stale index",
        )
        self.assertNotIn("entry-one.md", unclassified)
        self.assertNotIn("_Sidebar.md", unclassified)


class FetchGateTest(unittest.TestCase):
    """The fetch is what makes the ref reads current, and its failure is STOP."""

    def setUp(self) -> None:
        body = SKILL.read_text(encoding="utf-8")
        self.steps = body[body.index("## Sync Steps") :]

    def test_fetch_is_the_first_step(self) -> None:
        first = re.search(
            r"^ *1\. (?P<text>.+(?:\n(?! *\d+\. ).*)*)", self.steps, re.MULTILINE
        )
        assert first is not None
        self.assertIn("git fetch origin", first.group("text"))
        self.assertIn("STOP", first.group("text"))

    def test_no_ref_read_precedes_the_fetch(self) -> None:
        """Within the numbered procedure — the preamble names the ref to explain it."""
        numbered = self.steps[self.steps.index("\n  1. ") :]
        fetch = numbered.index("git fetch origin")
        for read in ("SRC_REF:docs/", "ls-tree"):
            self.assertLess(fetch, numbered.index(read), f"{read} precedes the fetch")

    def test_the_source_ref_is_main_not_a_release_tag(self) -> None:
        """Release is the sync's trigger, not the selector of its content."""
        self.assertIn(f"SRC_REF={SOURCE_REF}", reference_algorithm())
        self.assertNotIn("release_tag", reference_algorithm())


class NoWorkingTreeReadTest(unittest.TestCase):
    """Every `docs/` read in the executable body is qualified by the ref."""

    def _code_lines(self) -> list[str]:
        lines: list[str] = []
        for snippet in (reference_algorithm(), apply_snippet()):
            for line in snippet.splitlines():
                stripped = line.strip()
                if stripped and not stripped.startswith("#"):
                    lines.append(stripped)
        return lines

    def test_docs_reads_name_the_ref(self) -> None:
        seen = 0
        for line in self._code_lines():
            for match in re.finditer(r"docs/", line):
                seen += 1
                before = line[: match.start()]
                qualified = (
                    before.endswith(":")
                    or "ls-tree" in before
                    # content_same takes a path *inside* the ref; it prefixes $SRC_REF.
                    or before.endswith('content_same "')
                )
                self.assertTrue(
                    qualified,
                    f"unqualified working-tree read of docs/ in: {line}",
                )
        self.assertNotEqual(seen, 0, "the snippets were not extracted")

    def test_the_mirror_docs_carry_the_same_source(self) -> None:
        mirror = DOCS_MIRROR.read_text(encoding="utf-8")
        section = mirror[mirror.index("#### リリース後の Wiki 同期") :]
        section = section[: section.index("**Windows 固有")]
        self.assertIn("git fetch origin", section)
        self.assertIn(f"{SOURCE_REF}:docs/", section)
        self.assertIn(f"git ls-tree {SOURCE_REF} docs/", section)


if __name__ == "__main__":
    unittest.main()
