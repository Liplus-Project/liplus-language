"""No instruction surface routes a procedure through a skill Li+ does not ship.

Spec source: `rules/evolution/memory-entry-format.md` Consolidate Trigger.

Li+ names its own skills one way: `skills/<name>/SKILL.md`, whose resolution
`tests/test_skill_reference_resolution.py` already asserts. A namespaced invocation
(`<namespace>:<skill>`) names a skill from somewhere else, and Li+ ships none of those.
Such a reference declares no dependency and carries no fallback, so on a host that lacks
the namespace the procedure stops there and the agent meeting the stop improvises a pass
nobody else can read. That is the silent-failure shape `rules/model/subtractive-structural-beauty.md`
Spec write applies (B) sends back to be repaired in the design rather than papered over
with a safety net.

Nothing else reports it. The reference is prose: no import fails, no check turns red, and
the agent simply reads a name that resolves to nothing on that host.

Scope is the three surfaces the agent loads and runs as instruction. `docs/` is excluded
for the reason the resolution test excludes it: it is a record surface, and a record of a
dependency that was removed legitimately names it.

METAVARIABLES holds tokens of the same lexical shape that are not invocations. It is a
fixed literal set, not a per-mention carve-out: a token that is new here fails the check
until someone decides which of the two it is, which is the review this check exists to
force.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INSTRUCTION_SURFACES = ("rules", "skills", "adapter")
SCANNED_SUFFIXES = (".md", ".sh", ".ps1")
NAMESPACED_TOKEN = re.compile(r"`([a-z][a-z0-9._-]*:[a-z][a-z0-9._-]*)`")
METAVARIABLES = frozenset({"path:line"})


def scanned_files() -> list[Path]:
    files: list[Path] = []
    for surface in INSTRUCTION_SURFACES:
        base = ROOT / surface
        if not base.exists():
            continue
        files.extend(
            path
            for path in sorted(base.rglob("*"))
            if path.is_file() and path.suffix in SCANNED_SUFFIXES
        )
    return files


class ExternalSkillDependencyTest(unittest.TestCase):
    def test_the_scan_reaches_the_instruction_surfaces(self) -> None:
        """A scan that silently matches nothing would pass the assertion below."""
        self.assertNotEqual(scanned_files(), [])

    def test_no_namespaced_skill_reference(self) -> None:
        for path in scanned_files():
            text = path.read_text(encoding="utf-8")
            for match in NAMESPACED_TOKEN.finditer(text):
                token = match.group(1)
                if token in METAVARIABLES:
                    continue
                with self.subTest(source=str(path.relative_to(ROOT)), token=token):
                    self.fail(
                        f"{path.relative_to(ROOT)} names `{token}`, a namespaced skill "
                        "reference. Li+ ships no namespaced skill: route the procedure "
                        "through a `skills/<name>/SKILL.md` Li+ ships, or through Li+'s "
                        "own discipline stated in place."
                    )


if __name__ == "__main__":
    unittest.main()
