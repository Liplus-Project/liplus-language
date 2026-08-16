"""Agent Skills spec: the frontmatter `description` of every skill keeps its fixed form.

Spec source: `docs/K.-Source-File-Format.md` (skill `description` fixed form).
The 1024-character limit is a hard constraint of the Agent Skills standard, and the
handling of an over-limit value (truncation or validation error) is host-dependent, so
the check is kept in CI rather than in per-edit attention.

The `. ` terminator is checked here for a different reason. It is what the condition
count reads: the count is the first sentence split on ` / `, so a description that loses
its terminator stops declaring a countable number of firing conditions. The two
description-trim passes (#1766, #1767) each had to preserve it by hand while compressing
the trailing "what it provides" sentence, and a trim that deleted that sentence outright
would take the terminator with it. `rules/model/subtractive-structural-beauty.md` puts a
procedure whose execution is not guaranteed on the replace-with-a-structure side; this is
that structure.
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


def unquote_flow_scalar(value: str) -> str:
    """Strip one matching pair of YAML flow-scalar quotes from `value`.

    One pair only. The goal is to keep the delimiters out of the length and
    non-empty checks, not to reimplement YAML escape decoding: a doubled inner
    quote stays doubled, which over-counts length and so errs strict.
    """
    for quote in ('"', "'"):
        if len(value) >= 2 and value.startswith(quote) and value.endswith(quote):
            return value[1:-1]
    return value


def description_value(text: str) -> str | None:
    """Return the `description` value of a SKILL.md frontmatter, or None when absent.

    Single-line values and multi-line values (block scalar or wrapped continuation)
    both resolve, so the length check does not depend on the current one-line layout.
    A quoted value resolves to its content, so `description: ""` reads as empty
    rather than as a two-character string. Quotes inside a block scalar are body
    text and are left alone.
    """
    lines = frontmatter_lines(text)
    for index, line in enumerate(lines):
        if not line.startswith("description:"):
            continue
        head = line[len("description:") :].strip()
        block_scalar = head[:1] in ("|", ">")
        parts = [] if head[:1] in ("", "|", ">") else [head]
        for continuation in lines[index + 1 :]:
            if continuation.strip() and not continuation[:1].isspace():
                break
            parts.append(continuation.strip())
        value = " ".join(part for part in parts if part)
        return value if block_scalar else unquote_flow_scalar(value)
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

    def test_description_keeps_the_condition_list_terminator(self) -> None:
        """A `. ` terminator with a non-empty tail after it, on every skill.

        The tail's content is not asserted — trimming it to a shorter sentence is the
        point of the trim passes. What is asserted is that a tail survives at all, since
        deleting it removes the `. ` the condition count reads from.
        """
        for name, description in self.descriptions.items():
            with self.subTest(skill=name):
                head, separator, tail = (description or "").partition(". ")
                self.assertEqual(separator, ". ")
                self.assertNotEqual(head.strip(), "")
                self.assertNotEqual(tail.strip(), "")

    def test_extractor_resolves_every_frontmatter_layout(self) -> None:
        layouts = {
            "single_line": "---\nname: x\ndescription: Invoke when A. Provides B.\nlayer: L2-evolution\n---\n",
            "block_scalar": "---\nname: x\ndescription: >-\n  Invoke when A.\n  Provides B.\nlayer: L2-evolution\n---\n",
            "wrapped_continuation": "---\nname: x\ndescription: Invoke when A.\n  Provides B.\nlayer: L2-evolution\n---\n",
            "double_quoted": '---\nname: x\ndescription: "Invoke when A. Provides B."\nlayer: L2-evolution\n---\n',
            "single_quoted": "---\nname: x\ndescription: 'Invoke when A. Provides B.'\nlayer: L2-evolution\n---\n",
            "quoted_wrapped": '---\nname: x\ndescription: "Invoke when A.\n  Provides B."\nlayer: L2-evolution\n---\n',
        }
        for name, text in layouts.items():
            with self.subTest(layout=name):
                self.assertEqual(description_value(text), "Invoke when A. Provides B.")
        self.assertIsNone(description_value("---\nname: x\nlayer: L2-evolution\n---\n"))

    def test_a_quoted_empty_value_reads_as_empty(self) -> None:
        for name, text in {
            "double_quoted": '---\nname: x\ndescription: ""\n---\n',
            "single_quoted": "---\nname: x\ndescription: ''\n---\n",
        }.items():
            with self.subTest(layout=name):
                self.assertEqual(description_value(text), "")

    def test_extractor_leaves_quotes_that_are_not_delimiters(self) -> None:
        cases = {
            "block_scalar_body": (
                '---\nname: x\ndescription: >-\n  "Invoke when A."\n---\n',
                '"Invoke when A."',
            ),
            "unbalanced": (
                '---\nname: x\ndescription: "Invoke when A.\n---\n',
                '"Invoke when A.',
            ),
            "mismatched_pair": (
                "---\nname: x\ndescription: \"Invoke when A.'\n---\n",
                "\"Invoke when A.'",
            ),
            "inner_only": (
                '---\nname: x\ndescription: Invoke when "A". Provides B.\n---\n',
                'Invoke when "A". Provides B.',
            ),
        }
        for name, (text, expected) in cases.items():
            with self.subTest(case=name):
                self.assertEqual(description_value(text), expected)


if __name__ == "__main__":
    unittest.main()
