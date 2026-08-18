"""Every `skills/<name>/SKILL.md` path named on an instruction surface resolves to a file.

Spec source: `rules/operations/main-agent-procedures.md` The bar and its pair.

Why this is a CI check rather than per-edit attention. That section's maintenance rule
moves a canonical off a skill surface and leaves a pointer, and its delete branch removes
the skill outright when neither reader survives. Both halves rewrite cross-references
across `rules/`, `skills/` and `adapter/`, and a missed one leaves a pointer resolving to
nothing. Nothing else reports that: a dangling pointer raises no failure at runtime, the
agent simply reads a name and finds no file, which is the silent-failure shape
`rules/model/subtractive-structural-beauty.md` puts on the replace-with-a-structure side.

Scope is the three instruction surfaces the agent loads and runs. `docs/` is excluded on
purpose: it is a record surface, and it names skills that were deliberately deleted
(`skills/operations-on-merge/SKILL.md` in `docs/4.-Operations.md` and
`docs/L.-Hop-Count-Instrument.md`) as history of a past relocation. Asserting over prose
that legitimately names absent files would require a carve-out per mention, and a check
with prose carve-outs stops being a check.

The scan is deliberately blind to the actor axis, so it cannot fail on a skill that the
axis places out of scope. It asserts resolution only.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INSTRUCTION_SURFACES = ("rules", "skills", "adapter")
SCANNED_SUFFIXES = (".md", ".sh", ".ps1")
SKILL_REFERENCE = re.compile(r"skills/([a-z0-9-]+)/SKILL\.md")


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


class SkillReferenceResolutionTest(unittest.TestCase):
    def test_the_scan_reaches_the_instruction_surfaces(self) -> None:
        """A scan that silently matches nothing would pass the assertion below."""
        files = scanned_files()
        self.assertNotEqual(files, [])
        referencing = [
            path
            for path in files
            if SKILL_REFERENCE.search(path.read_text(encoding="utf-8"))
        ]
        self.assertNotEqual(referencing, [])

    def test_every_referenced_skill_exists(self) -> None:
        for path in scanned_files():
            text = path.read_text(encoding="utf-8")
            for match in SKILL_REFERENCE.finditer(text):
                name = match.group(1)
                with self.subTest(source=str(path.relative_to(ROOT)), skill=name):
                    self.assertTrue(
                        (ROOT / "skills" / name / "SKILL.md").is_file(),
                        f"{path.relative_to(ROOT)} points at skills/{name}/SKILL.md, "
                        "which does not exist",
                    )


if __name__ == "__main__":
    unittest.main()
