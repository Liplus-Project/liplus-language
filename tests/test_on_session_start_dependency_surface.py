"""Behavioural coverage for the cold-start dependency ordering surface.

Target = the three `adapter/*/hooks/on-session-start.*` implementations
(claude bash / codex bash / codex PowerShell). Issue #1687.

The contract is `rules/evolution/cold-start-synthesis.md` Dependency Ordering
Surface: an open issue of the Li+ repository surfaces when at least one of its
`blockedBy` issues is open, with those open blockers named; a closed blocker
does not count; the result is read through GraphQL; the section sits in the
diff-only set.

What is pinned and what is not
------------------------------
The contract fixes which issues surface and which blockers they carry, and
delegates presentation to the adapter ("Material gathering and concrete
surfacing logic belong to the adapter cold-start path"). The assertions read
the judgment out of the emission -- which issue numbers surfaced, which blocker
references each carried, whether the scan-cap note appeared -- and do not match
the banner wording, the separator between an issue and its blockers, or the
order of the lines.

`gh` is a stub that answers `gh api graphql` with a fixture response and
returns nothing for every other call, so the run stays offline. The harness is
reused from `test_on_session_start_observation_surface`.
"""

from __future__ import annotations

import json
import os
import re
import sys
import unittest

from test_on_session_start_observation_surface import (
    ADAPTERS,
    NODE,
    Workspace,
    emitted_sections,
    posix_path,
)


HOME_REPO = "Liplus-Project/liplus-language"


def issue_node(number: int, title: str, blockers: list[tuple[int, str, str]]) -> dict:
    """One `issues.nodes[]` element; a blocker is (number, state, repository)."""
    return {
        "number": number,
        "title": title,
        "blockedBy": {
            "nodes": [
                {"number": n, "state": state, "repository": {"nameWithOwner": repo}}
                for n, state, repo in blockers
            ]
        },
    }


def graphql_response(nodes: list[dict], has_next_page: bool = False) -> dict:
    return {
        "data": {
            "repository": {
                "issues": {"pageInfo": {"hasNextPage": has_next_page}, "nodes": nodes}
            }
        }
    }


MIXED_NODES = [
    # open blocker in this repo + closed blocker: only the open one is named
    issue_node(101, "Waits on two", [(90, "OPEN", HOME_REPO), (91, "CLOSED", HOME_REPO)]),
    # every blocker closed: not blocked any more, does not surface
    issue_node(102, "Blockers all closed", [(92, "CLOSED", HOME_REPO)]),
    # no blockers at all
    issue_node(103, "Free to start", []),
    # open blocker in another repository: named with owner/repo
    issue_node(104, "Waits across repos", [(224, "OPEN", "Liplus-Project/github-rag-mcp")]),
]


class DependencyWorkspace(Workspace):
    """Workspace whose `gh` answers the GraphQL call with a fixture file."""

    def __init__(self) -> None:
        super().__init__()
        self.response = self.root / "graphql.json"
        self._write_graphql_gh_stub()

    def set_response(self, payload: dict | None) -> None:
        if payload is None:
            if self.response.exists():
                self.response.unlink()
            return
        self.response.write_text(json.dumps(payload), encoding="utf-8")

    def _write_graphql_gh_stub(self) -> None:
        stub_py = self.stub_bin / "gh_stub.py"
        stub_py.write_text(
            "import sys\n"
            "from pathlib import Path\n"
            f"response = Path({str(self.response)!r})\n"
            "if sys.argv[1:3] == ['api', 'graphql'] and response.is_file():\n"
            "    sys.stdout.write(response.read_text(encoding='utf-8'))\n",
            encoding="utf-8",
        )
        unix_stub = self.stub_bin / "gh"
        unix_stub.write_text(
            "#!/bin/sh\n"
            f'if [ "$1" = api ] && [ "$2" = graphql ] && [ -f "{posix_path(self.response)}" ]; then\n'
            f'  cat "{posix_path(self.response)}"\n'
            "fi\n"
            "exit 0\n",
            encoding="utf-8",
        )
        os.chmod(unix_stub, 0o755)
        (self.stub_bin / "gh.cmd").write_text(
            f'@"{sys.executable}" "{stub_py}" %*\r\n', encoding="ascii"
        )


def dependency_section(hook_output: str) -> str | None:
    """Body of the dependency section, or None when the hook stayed silent."""
    for banner, body in emitted_sections(hook_output):
        if "blocked" in banner.lower():
            return body
    return None


_ISSUE_RE = re.compile(r"^#(\d+)\b")
_REF_RE = re.compile(r"(?:(\S+/\S+?))?#(\d+)")


def surfaced(section_body: str | None) -> dict[int, set[str]]:
    """Issue number -> blocker references carried on its line.

    A reference is `#<n>` for this repository and `<owner>/<repo>#<n>` for
    another, which is what the contract asks each blocker to be named as.
    """
    result: dict[int, set[str]] = {}
    for line in (section_body or "").split("\n"):
        line = line.strip()
        match = _ISSUE_RE.match(line)
        if not match:
            continue
        rest = line[match.end():]
        # Blocker refs are what follows the title; a title carrying `#n` would
        # be read as a ref, and no fixture title does.
        refs = {
            (repo + "#" if repo else "#") + number
            for repo, number in _REF_RE.findall(rest)
        }
        result[int(match.group(1))] = refs
    return result


def scan_cap_noted(section_body: str | None) -> bool:
    return any(
        line.strip() and not _ISSUE_RE.match(line.strip())
        for line in (section_body or "").split("\n")
    )


class DependencySurfaceTest(unittest.TestCase):
    def new_workspace(self) -> DependencyWorkspace:
        ws = DependencyWorkspace()
        self.addCleanup(ws.cleanup)
        return ws

    def require_node(self, adapter: str) -> None:
        # The bash ports filter with node; without it the section is empty by
        # design, which is not the behaviour these cases observe.
        if adapter != "codex_ps1" and not NODE:
            if os.environ.get("CI"):
                raise AssertionError("node is required for the bash dependency filter on CI")
            self.skipTest("node not available on this host")

    def test_open_blockers_only_surface(self) -> None:
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                self.require_node(adapter)
                ws = self.new_workspace()
                ws.set_response(graphql_response(MIXED_NODES))
                body = dependency_section(ws.run(adapter))
                self.assertEqual(
                    surfaced(body),
                    {101: {"#90"}, 104: {"Liplus-Project/github-rag-mcp#224"}},
                    body,
                )
                self.assertIn("Waits on two", body or "")
                self.assertFalse(scan_cap_noted(body), body)

    def test_no_blocked_issue_is_silent(self) -> None:
        nodes = [issue_node(103, "Free to start", []), issue_node(102, "Closed", [(92, "CLOSED", HOME_REPO)])]
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                self.require_node(adapter)
                ws = self.new_workspace()
                ws.set_response(graphql_response(nodes))
                self.assertIsNone(dependency_section(ws.run(adapter)))

    def test_query_failure_is_silent(self) -> None:
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                self.require_node(adapter)
                ws = self.new_workspace()
                ws.set_response(None)
                self.assertIsNone(dependency_section(ws.run(adapter)))

    def test_scan_cap_is_noted(self) -> None:
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                self.require_node(adapter)
                ws = self.new_workspace()
                ws.set_response(graphql_response(MIXED_NODES, has_next_page=True))
                body = dependency_section(ws.run(adapter))
                self.assertTrue(scan_cap_noted(body), body)
                self.assertEqual(set(surfaced(body)), {101, 104}, body)

    def test_section_is_in_diff_only_set(self) -> None:
        """Unchanged on the second run -> not re-emitted; changed -> re-emitted."""
        if not NODE:
            if os.environ.get("CI"):
                raise AssertionError("node is required for diff-only state on CI")
            self.skipTest("node not available on this host")
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                ws = self.new_workspace()
                ws.set_response(graphql_response(MIXED_NODES))
                self.assertIsNotNone(dependency_section(ws.run(adapter)))
                self.assertIsNone(dependency_section(ws.run(adapter)))
                changed = MIXED_NODES + [issue_node(105, "New wait", [(95, "OPEN", HOME_REPO)])]
                ws.set_response(graphql_response(changed))
                self.assertIn(105, surfaced(dependency_section(ws.run(adapter))))


if __name__ == "__main__":
    unittest.main()
