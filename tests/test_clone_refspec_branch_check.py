"""Behavioural coverage for the cold-start clone branch-fetch surface.

Target = the three `adapter/*/hooks/on-session-start.*` implementations
(claude bash / codex bash / codex PowerShell) and the prose surfaces carrying
the same decision. Issue #1911.

The defect this pins: `remote.origin.fetch` decides which refs a fetch moves,
and a clone configured with tag mappings only still resolves tags. So
`fetch --tags` on Li+update.md's clone-mode `exists` path succeeds, a later bare
`git fetch origin` succeeds as a no-op, and nothing raises while every branch
stays where it was. One such clone sat 374 commits behind for close to five
months, and it surfaced by accident rather than through any check.

What is pinned
--------------
The reporting destination as much as the detection. The finding goes to the
cold-start surface class that carries no section key and sits outside the
diff-only set, alongside the observation and tally surfaces, and it is
explicitly NOT stacked on `LI_PLUS_UPDATE_STATUS` -- that marker is the trigger
condition for step 2 of the adapter startup procedure and branches on the status
alone, so a reason there would let a detection-only check start the update
walkthrough. Both directions are asserted: the surface fires, and the marker
stays clean.

Detection, and only detection: the run must leave the fixture's refspec
configuration untouched. The predicate is "at least one refspec whose source
side is under `refs/heads/`", so a single-branch clone passes -- it does track a
branch. Two states are silent because neither is evidence about a refspec: a
directory that is not a clone (api mode), and a host without `git`.

Being outside the diff-only set is what a state-driven trigger needs, and it is
asserted on a second run against the same workspace: a fingerprinted section
would surface the clone once and then go silent for exactly as long as the
defect persisted. The same run pins the no-new-material marker suppression,
since a session pairing a broken clone with "no new orientation material" would
contradict itself.

A port left behind makes the same workspace report differently depending on
which host adapter ran, which is the shape #1804 produced once already, so the
surface is asserted on all three ports and the decision's prose surfaces are
asserted to name it.
"""

from __future__ import annotations

import shutil
import subprocess
import unittest
from pathlib import Path

from test_on_session_start_observation_surface import (
    ADAPTERS,
    Workspace,
    emitted_sections,
    no_new_material_marker,
    require_runtime,
)
from test_config_value_parity import update_status_line


ROOT = Path(__file__).resolve().parents[1]

# The surface is located by topic, not by banner text: the banner is an adapter
# choice (`rules/evolution/cold-start-synthesis.md` delegates presentation), and
# pinning it would make every assertion here depend on one string.
SURFACE_TOPIC = "clone"

# What the emitted body must carry to be actionable: the key that is misconfigured
# and the ref namespace no refspec sources.
BODY_TOKENS = ("remote.origin.fetch", "refs/heads/")

WILDCARD = "+refs/heads/*:refs/remotes/origin/*"
SINGLE_BRANCH = "+refs/heads/main:refs/remotes/origin/main"
TAG_ONLY = "+refs/tags/build-2026-04-12.8:refs/tags/build-2026-04-12.8"

PORTS = (
    "adapter/claude/hooks/on-session-start.sh",
    "adapter/codex/hooks/on-session-start.sh",
    "adapter/codex/hooks/on-session-start.ps1",
)

# The behaviour contract, the spec implementing the walkthrough-side check, and
# the two docs that mirror them.
PROSE = (
    "rules/evolution/cold-start-synthesis.md",
    "Li+update.md",
    "docs/C.-Update.md",
    "docs/6.-Adapter.md",
    "docs/2.-Evolution.md",
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
    """The decision reaches every surface that carries it."""

    def test_every_port_reads_the_fetch_refspec(self) -> None:
        """A port that emits without reading the config is not a check."""
        for surface in PORTS:
            with self.subTest(surface=surface):
                text = (ROOT / surface).read_text(encoding="utf-8")
                for token in BODY_TOKENS:
                    self.assertIn(token, text)

    def test_no_port_stacks_it_on_the_update_status_marker(self) -> None:
        """The destination was moved off the marker; no port may put it back.

        Read off the source rather than only off an emission: the marker's
        reason list is assembled from whatever axis blocks a port carries, so a
        fourth one added later would read as an ordinary axis at review time.
        """
        for surface in PORTS:
            with self.subTest(surface=surface):
                text = (ROOT / surface).read_text(encoding="utf-8")
                for line in text.split("\n"):
                    if "refs/heads/" in line:
                        self.assertNotIn("UPDATEREASON", line.upper().replace("$", "").replace("_", ""))

    def test_prose_surfaces_name_the_surface(self) -> None:
        for surface in PROSE:
            with self.subTest(surface=surface):
                text = (ROOT / surface).read_text(encoding="utf-8")
                self.assertIn("Clone Branch Fetch Surface", text)

    def test_contract_declares_the_absent_lifecycle(self) -> None:
        """The lifecycle fields are absent by design, and it must say so.

        Without that, a later reader repairs the "gap" by adding one, and an
        entry then stands after the condition it reports has cleared.
        """
        text = (ROOT / "rules/evolution/cold-start-synthesis.md").read_text(encoding="utf-8")
        section = text.split("## Clone Branch Fetch Surface", 1)[1]
        section = section.split("</clone-branch-fetch-surface>", 1)[0]
        self.assertIn("verdict_state", section)
        self.assertIn("expires", section)
        self.assertIn("state-driven", section)


class CloneRefspecBranchCheckTestCase(unittest.TestCase):
    def setUp(self) -> None:
        if not GIT:
            require_runtime("git", "clone refspec branch check")
        self.ws = self.new_workspace()

    def new_workspace(self) -> Workspace:
        workspace = Workspace()
        self.addCleanup(workspace.cleanup)
        # Past the codex ports' unresolved-source guard; without it those two
        # hooks exit before emitting any material at all.
        workspace.seed_coldstart_rule("CLONE-REFSPEC-FIXTURE")
        return workspace

    def output(self, adapter: str) -> str:
        out = self.ws.run(adapter, "startup")
        self.ws.clear_state()
        return out

    def surface(self, hook_output: str) -> str | None:
        for banner, body in emitted_sections(hook_output):
            if SURFACE_TOPIC in banner.lower():
                return body
        return None

    def assertReported(self, adapter: str) -> None:
        out = self.output(adapter)
        body = self.surface(out)
        self.assertIsNotNone(body, f"{adapter} surfaced nothing for a clone with no branch mapping")
        for token in BODY_TOKENS:
            self.assertIn(token, body)
        # The destination is the cold-start surface, not the update marker.
        line = update_status_line(out)
        if line is not None:
            self.assertNotIn("refs/heads", line)
            self.assertNotIn("refspec", line)

    def assertSilent(self, adapter: str) -> None:
        self.assertIsNone(self.surface(self.output(adapter)))

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
        """A single-branch clone tracks a branch, so it is not this condition."""
        make_clone(self.ws.liplus, SINGLE_BRANCH)
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                self.assertSilent(adapter)

    def test_tags_alongside_a_branch_are_silent(self) -> None:
        """A branch mapping decides, not the count of tag mappings."""
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
                self.output(adapter)
                self.assertEqual(configured_refspecs(self.ws.liplus), [TAG_ONLY])

    def test_state_driven_surface_survives_the_second_run(self) -> None:
        """Still surfaced on a second startup, and it suppresses the marker.

        This is why the finding is not an ordinary diff-only section: the body
        does not change while the defect persists, so a fingerprinted section
        would report once and then stay silent for exactly as long as the clone
        stayed broken. The second run is also where the no-new-material marker
        would appear, and a session pairing it with a broken clone would
        contradict itself.
        """
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                workspace = self.new_workspace()
                make_clone(workspace.liplus, TAG_ONLY)
                first = workspace.run(adapter, "startup")
                self.assertIsNotNone(self.surface(first))
                second = workspace.run(adapter, "startup")
                body = self.surface(second)
                self.assertIsNotNone(body, f"{adapter} went silent on the second run")
                for token in BODY_TOKENS:
                    self.assertIn(token, body)
                self.assertIsNone(
                    no_new_material_marker(second),
                    f"{adapter} paired a surfaced clone with the no-new-material marker",
                )

                # Control: the same fixture with a healthy clone does reach the
                # marker on its second run. Without it, the assertion above
                # would also pass on a fixture that never got as far as
                # emitting one, and would be reporting nothing.
                control = self.new_workspace()
                make_clone(control.liplus, WILDCARD)
                control.run(adapter, "startup")
                self.assertIsNotNone(
                    no_new_material_marker(control.run(adapter, "startup")),
                    f"{adapter} fixture never reaches the marker; the assertion above proves nothing",
                )


if __name__ == "__main__":
    unittest.main()
