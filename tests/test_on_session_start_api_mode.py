"""Behavioural coverage for the session-start hooks in api mode. Issue #2031.

Target = the three `adapter/*/hooks/on-session-start.*` implementations
(claude bash / codex bash / codex PowerShell).

What was observed: with `LI_PLUS_MODE=api` and no `liplus-language` clone in the
workspace, the claude hook exited before emitting anything, and the codex ports
emitted `LI_PLUS_UPDATE_STATUS=needed reason=liplus-source-unresolved` and
exited. Both treated the missing clone as "Li+ not installed yet", which it is
not in api mode.

What is pinned:
- api mode without a clone reaches the same emission as clone mode: the update
  status marker, the language contract block, and the material read out of the
  Li+ source (cold-start anchor, Decision-Structure head, and on codex the rules
  injection).
- that source is the adapter tag's tree fetched as a GitHub tarball through
  `gh`, kept at `.liplus-extract/<tag>/`, and read from there on a later run
  without fetching again.
- clone mode without a clone keeps its pre-#2031 exit, on every port.

`gh` is a stub that serves one fixture tarball for the tarball endpoint and
returns nothing for every other call, so the run stays offline. The channel is
`release` so the target tag resolves through that stub and not over the
network.
"""

from __future__ import annotations

import io
import os
import shutil
import sys
import tarfile
import unittest
from pathlib import Path

from test_on_session_start_observation_surface import (
    ADAPTERS,
    Workspace,
    emitted_sections,
    posix_path,
)


TAG = "build-2099-01-01.1"
ANCHOR_TOKEN = "APIMODE-ANCHOR-TOKEN"
RULE_TOKEN = "APIMODE-RULE-TOKEN"
DECISION_TOKEN = "APIMODE-DECISION-TOKEN"


def fixture_tarball(path: Path) -> None:
    """A GitHub-shaped source tarball: one top-level directory, then the tree."""
    top = "Liplus-Project-liplus-language-0000000"
    files = {
        "rules/evolution/cold-start-synthesis.md": (
            "---\nalwaysApply: true\n---\n\n# Cold-start Synthesis\n\n"
            f"{ANCHOR_TOKEN} anchor body.\n"
        ),
        "rules/model/probe.md": f"# Probe\n\n{RULE_TOKEN}\n",
        "docs/Decision-Structure.md": f"# Decision Structure\n\n{DECISION_TOKEN}\n",
    }
    with tarfile.open(path, "w:gz") as archive:
        for name, text in files.items():
            data = text.encode("utf-8")
            info = tarfile.TarInfo(f"{top}/{name}")
            info.size = len(data)
            archive.addfile(info, io.BytesIO(data))


class ApiModeWorkspace(Workspace):
    """Host workspace in api mode: no clone, a gh stub serving the tarball."""

    def __init__(self) -> None:
        super().__init__()
        shutil.rmtree(self.liplus)
        self.tarball = self.root / "source.tar.gz"
        fixture_tarball(self.tarball)
        self._write_tarball_gh_stub()

    def _write_tarball_gh_stub(self) -> None:
        endpoint = f"repos/Liplus-Project/liplus-language/tarball/{TAG}"
        stub_py = self.stub_bin / "gh_stub.py"
        stub_py.write_text(
            "import sys\n"
            "from pathlib import Path\n"
            f"tarball = Path({str(self.tarball)!r})\n"
            f"if sys.argv[1:3] == ['api', {endpoint!r}] and tarball.is_file():\n"
            "    sys.stdout.buffer.write(tarball.read_bytes())\n",
            encoding="utf-8",
        )
        unix_stub = self.stub_bin / "gh"
        unix_stub.write_text(
            "#!/bin/sh\n"
            f'if [ "$1" = api ] && [ "$2" = "{endpoint}" ] && [ -f "{posix_path(self.tarball)}" ]; then\n'
            f'  cat "{posix_path(self.tarball)}"\n'
            "fi\n"
            "exit 0\n",
            encoding="utf-8",
        )
        os.chmod(unix_stub, 0o755)
        (self.stub_bin / "gh.cmd").write_text(
            f'@"{sys.executable}" "{stub_py}" %*\r\n', encoding="ascii"
        )

    def configure(self, mode: str) -> None:
        self.write(
            self.workspace,
            "Li+config.md",
            "\n".join(
                [
                    "LI_PLUS_REPO=https://github.com/Liplus-Project/liplus-language",
                    f"LI_PLUS_MODE={mode}",
                    "LI_PLUS_CHANNEL=release",
                    "LI_PLUS_BASE_LANGUAGE=ja",
                    "LI_PLUS_PROJECT_LANGUAGE=ja",
                ]
            )
            + "\n",
        )
        sentinel = f"# --- Li+ BEGIN ({TAG}) ---\nbody\n# --- Li+ END ---\n"
        self.write(self.workspace / ".claude", "CLAUDE.md", sentinel)
        self.write(self.workspace, "AGENTS.md", sentinel)

    @property
    def extract_root(self) -> Path:
        return self.workspace / ".liplus-extract"


def has_marker(output: str) -> bool:
    return any(line.startswith("LI_PLUS_UPDATE_STATUS=") for line in output.splitlines())


def section_body(output: str, topic: str) -> str:
    for banner, body in emitted_sections(output):
        if topic in banner:
            return body
    return ""


class ApiModeSessionStartTestCase(unittest.TestCase):
    def new_workspace(self, mode: str) -> ApiModeWorkspace:
        ws = ApiModeWorkspace()
        self.addCleanup(ws.cleanup)
        ws.configure(mode)
        return ws

    def test_api_mode_without_clone_emits_the_full_startup_material(self) -> None:
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                ws = self.new_workspace("api")
                output = ws.run(adapter)
                self.assertTrue(has_marker(output), "update status marker must be emitted")
                self.assertIn("LI_PLUS_BASE_LANGUAGE=ja", output)
                self.assertIn(ANCHOR_TOKEN, section_body(output, "Cold-start Synthesis ("))
                self.assertIn(DECISION_TOKEN, section_body(output, "Decision structure"))
                self.assertIn("rules/model/probe.md", section_body(output, "Rules tree"))
                if adapter != "claude_sh":
                    self.assertIn(RULE_TOKEN, output, "codex rules injection reads the fetched tree")
                self.assertNotIn("liplus-source-unresolved", output)

    def test_fetched_tree_is_cached_per_tag_and_reused(self) -> None:
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                ws = self.new_workspace("api")
                ws.run(adapter)
                cached = ws.extract_root / TAG
                self.assertTrue((cached / "rules" / "model" / "probe.md").is_file())
                leftovers = [p.name for p in ws.extract_root.iterdir() if p.name != TAG]
                self.assertEqual(leftovers, [], "no partial extraction may be left behind")

                # The stub can no longer serve the tarball: a second run that
                # still carries the anchor read it from the cache.
                ws.tarball.unlink()
                ws.clear_state()
                output = ws.run(adapter, matcher="resume")
                self.assertIn(ANCHOR_TOKEN, output)

    def test_clone_mode_without_clone_keeps_its_exit(self) -> None:
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                ws = self.new_workspace("clone")
                output = ws.run(adapter)
                if adapter == "claude_sh":
                    self.assertEqual(output.strip(), "", "claude exits silently pre-bootstrap")
                else:
                    self.assertIn("reason=liplus-source-unresolved", output)
                self.assertFalse(ws.extract_root.exists(), "clone mode fetched no tarball")


if __name__ == "__main__":
    unittest.main()
