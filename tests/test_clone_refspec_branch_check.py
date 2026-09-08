"""Behavioural coverage for the clone-mode branch-fetch check.

Target = the three `adapter/*/hooks/on-session-start.*` implementations
(claude bash / codex bash / codex PowerShell) and the two prose surfaces that
carry the same decision. Issue #1911.

The defect this pins: `remote.origin.fetch` decides which refs a fetch moves,
and a clone configured with tag mappings only still resolves tags. So
`fetch --tags` on Li+update.md's clone-mode `exists` path succeeds, a later bare
`git fetch origin` succeeds as a no-op, and the sentinel-tag axis -- which reads
tags -- keeps emitting `unnecessary` while every branch stays where it was. One
such clone sat 374 commits behind for close to five months, and it surfaced by
accident rather than through any check.

What is pinned
--------------
Detection, and only detection: the axis reports
`clone-refspec-no-branch-mapping` on the `LI_PLUS_UPDATE_STATUS` reason surface
and repairs nothing, so the assertions read the reason out of the marker and
also assert the fixture's refspec configuration is unchanged by the run. The
predicate is "at least one refspec whose source side is under `refs/heads/`",
so a single-branch clone passes -- it does track a branch. Two states are
silent because neither is evidence about a refspec: a directory that is not a
clone (api mode), and a host without `git`.

The reason token is asserted across all five surfaces because a port left
behind makes the same workspace report differently depending on which host
adapter ran, which is the shape #1804 produced once already.
"""

from __future__ import annotations

import shutil
import subprocess
import unittest
from pathlib import Path

from test_on_session_start_observation_surface import (
    ADAPTERS,
    Workspace,
    require_runtime,
)
from test_config_value_parity import update_status_line


ROOT = Path(__file__).resolve().parents[1]

REASON = "clone-refspec-no-branch-mapping"

WILDCARD = "+refs/heads/*:refs/remotes/origin/*"
SINGLE_BRANCH = "+refs/heads/main:refs/remotes/origin/main"
TAG_ONLY = "+refs/tags/build-2026-04-12.8:refs/tags/build-2026-04-12.8"

# The three hook ports, plus the spec they implement and the doc that mirrors it.
SURFACES = (
    "adapter/claude/hooks/on-session-start.sh",
    "adapter/codex/hooks/on-session-start.sh",
    "adapter/codex/hooks/on-session-start.ps1",
    "Li+update.md",
    "docs/C.-Update.md",
)

GIT = shutil.which("git")


def make_clone(directory: Path, *refspecs: str) -> None:
    """A real repository at `directory` carrying exactly `refspecs`.

    `git remote add` writes the wildcard mapping itself, so it is removed first
    and the fixture's own set added back. No refspec at all is a valid fixture:
    it is the state a clone reaches when the key is dropped entirely.
    """
    directory.mkdir(parents=True, exist_ok=True)
    run = lambda *args: subprocess.run(  # noqa: E731
        [GIT, "-C", str(directory), *args],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    subprocess.run(
        [GIT, "init", "-q", str(directory)],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    run("remote", "add", "origin", "https://example.invalid/liplus-language.git")
    subprocess.run(
        [GIT, "-C", str(directory), "config", "--unset-all", "remote.origin.fetch"],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    for refspec in refspecs:
        run("config", "--add", "remote.origin.fetch", refspec)


def configured_refspecs(directory: Path) -> list[str]:
    completed = subprocess.run(
        [GIT, "-C", str(directory), "config", "--get-all", "remote.origin.fetch"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed.stdout.decode("utf-8").split()


class CloneRefspecParityTestCase(unittest.TestCase):
    """The reason token reaches every surface carrying this decision."""

    def test_every_surface_names_the_reason(self) -> None:
        for surface in SURFACES:
            with self.subTest(surface=surface):
                text = (ROOT / surface).read_text(encoding="utf-8")
                self.assertIn(REASON, text)

    def test_every_port_reads_the_fetch_refspec(self) -> None:
        """A port that emits the token without reading the config is not a check."""
        for surface in SURFACES[:3]:
            with self.subTest(surface=surface):
                text = (ROOT / surface).read_text(encoding="utf-8")
                self.assertIn("remote.origin.fetch", text)
                self.assertIn("refs/heads/", text)


class CloneRefspecBranchCheckTestCase(unittest.TestCase):
    def setUp(self) -> None:
        if not GIT:
            require_runtime("git", "clone refspec branch check")
        self.ws = Workspace()
        self.addCleanup(self.ws.cleanup)
        # Past the codex ports' unresolved-source guard; without it those two
        # hooks exit before any Li+ marker is emitted.
        self.ws.seed_coldstart_rule("CLONE-REFSPEC-FIXTURE")

    def reasons(self, adapter: str) -> str:
        output = self.ws.run(adapter, "startup")
        self.ws.clear_state()
        line = update_status_line(output)
        self.assertIsNotNone(line, f"{adapter} emitted no update status marker")
        return line

    def assertReported(self, adapter: str) -> None:
        self.assertIn(REASON, self.reasons(adapter))

    def assertSilent(self, adapter: str) -> None:
        self.assertNotIn(REASON, self.reasons(adapter))

    def test_tag_only_refspec_is_reported(self) -> None:
        """The measured state: tags resolve, no branch mapping exists."""
        make_clone(self.ws.liplus, TAG_ONLY)
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                self.assertReported(adapter)

    def test_no_refspec_at_all_is_reported(self) -> None:
        make_clone(self.ws.liplus)
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                self.assertReported(adapter)

    def test_wildcard_refspec_is_silent(self) -> None:
        make_clone(self.ws.liplus, WILDCARD)
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                self.assertSilent(adapter)

    def test_single_branch_refspec_is_silent(self) -> None:
        """A single-branch clone tracks a branch, so it is not this defect."""
        make_clone(self.ws.liplus, SINGLE_BRANCH)
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                self.assertSilent(adapter)

    def test_tags_alongside_a_branch_are_silent(self) -> None:
        """The wildcard's presence decides, not the count of tag mappings."""
        make_clone(self.ws.liplus, TAG_ONLY, WILDCARD)
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                self.assertSilent(adapter)

    def test_directory_that_is_not_a_clone_is_silent(self) -> None:
        """api mode: the directory exists and holds no repository."""
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                self.assertSilent(adapter)

    def test_detection_does_not_repair(self) -> None:
        """No port writes the missing refspec back."""
        make_clone(self.ws.liplus, TAG_ONLY)
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                self.reasons(adapter)
                self.assertEqual(configured_refspecs(self.ws.liplus), [TAG_ONLY])


if __name__ == "__main__":
    unittest.main()
