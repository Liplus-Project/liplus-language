"""Agent Skills spec: the frontmatter `description` of every skill stays within 1024 characters.

Spec source: `docs/K.-Source-File-Format.md` (skill `description` fixed form).
The limit is a hard constraint of the Agent Skills standard, and the handling of an
over-limit value (truncation or validation error) is host-dependent, so the check is
kept in CI rather than in per-edit attention.
"""

from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DESCRIPTION_MAX_CHARS = 1024


def frontmatter_lines(text: str) -> list[str]:
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return []
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return lines[1:index]
    return []


def description_value(text: str) -> str | None:
    """Return the `description` value of a SKILL.md frontmatter, or None when absent.

    Single-line values and multi-line values (block scalar or wrapped continuation)
    both resolve, so the length check does not depend on the current one-line layout.
    """
    lines = frontmatter_lines(text)
    for index, line in enumerate(lines):
        if not line.startswith("description:"):
            continue
        head = line[len("description:") :].strip()
        parts = [] if head[:1] in ("", "|", ">") else [head]
        for continuation in lines[index + 1 :]:
            if continuation.strip() and not continuation[:1].isspace():
                break
            parts.append(continuation.strip())
        return " ".join(part for part in parts if part)
    return None


class SkillDescriptionLimitTest(unittest.TestCase):
    def setUp(self) -> None:
        self.descriptions = {
            path.parent.name: description_value(path.read_text(encoding="utf-8"))
            for path in sorted((ROOT / "skills").glob("*/SKILL.md"))
        }

    def test_every_skill_declares_a_description(self) -> None:
        self.assertNotEqual(self.descriptions, {})
        for name, description in self.descriptions.items():
            with self.subTest(skill=name):
                self.assertIsNotNone(description)
                self.assertNotEqual(description, "")

    def test_description_stays_within_the_character_limit(self) -> None:
        for name, description in self.descriptions.items():
            with self.subTest(skill=name):
                self.assertLessEqual(len(description or ""), DESCRIPTION_MAX_CHARS)

    def test_extractor_resolves_both_frontmatter_layouts(self) -> None:
        layouts = {
            "single_line": "---\nname: x\ndescription: Invoke when A. Provides B.\nlayer: L2-evolution\n---\n",
            "block_scalar": "---\nname: x\ndescription: >-\n  Invoke when A.\n  Provides B.\nlayer: L2-evolution\n---\n",
            "wrapped_continuation": "---\nname: x\ndescription: Invoke when A.\n  Provides B.\nlayer: L2-evolution\n---\n",
        }
        for name, text in layouts.items():
            with self.subTest(layout=name):
                self.assertEqual(description_value(text), "Invoke when A. Provides B.")
        self.assertIsNone(description_value("---\nname: x\nlayer: L2-evolution\n---\n"))


if __name__ == "__main__":
    unittest.main()
