"""Every `skills/<name>/SKILL.md` path named on an instruction surface resolves to a file,
and every `` `<path>.md` <Section Name> `` cross-reference resolves to a referenceable
position inside that file.

Spec source: `rules/operations/main-agent-procedures.md` The bar and its pair (path
resolution) and `docs/K.-Source-File-Format.md` (referenceable position, section-name
resolution).

Why this is a CI check rather than per-edit attention. That section's maintenance rule
moves a canonical off a skill surface and leaves a pointer, and its delete branch removes
the skill outright when neither reader survives. Both halves rewrite cross-references
across `rules/`, `skills/` and `adapter/`, and a missed one leaves a pointer resolving to
nothing. Nothing else reports that: a dangling pointer raises no failure at runtime, the
agent simply reads a name and finds no file, which is the silent-failure shape
`rules/model/subtractive-structural-beauty.md` puts on the replace-with-a-structure side.
The same is true one level down: a section name renamed or deleted out from under a
reference leaves the file resolving while the position inside it does not, and CI stayed
green through that too until this second check was added (issue #1792).

Scope is the three instruction surfaces the agent loads and runs. `docs/` is excluded on
purpose: it is a record surface, and it names skills that were deliberately deleted
(`skills/operations-on-merge/SKILL.md` in `docs/4.-Operations.md` and
`docs/L.-Hop-Count-Instrument.md`) as history of a past relocation. Asserting over prose
that legitimately names absent files would require a carve-out per mention, and a check
with prose carve-outs stops being a check.

The scan is deliberately blind to the actor axis, so it cannot fail on a skill that the
axis places out of scope. It asserts resolution only.

Section-name resolution is content-driven, not lexical: the reference format carries no
terminator symbol marking where a section name ends, so the candidate is read as the
longest word run following `` `<path>.md` `` that resolves against an actual position in
the target file, tried from longest to shortest one word at a time. What counts as a
resolvable position (a markdown heading, or a line-start label ending at a delimiter) is
specified in `docs/K.-Source-File-Format.md`; this file only asserts resolution and does
not restate that norm. There is no per-reference exception list: a reference that does
not resolve is fixed at the reference or at its target, not waived here.
"""

from __future__ import annotations

import bisect
import functools
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INSTRUCTION_SURFACES = ("rules", "skills", "adapter")
SCANNED_SUFFIXES = (".md", ".sh", ".ps1")
SKILL_REFERENCE = re.compile(r"skills/([a-z0-9-]+)/SKILL\.md")

# A section-name reference is triggered by a backtick-quoted `.md` path immediately
# followed (same line) by a capitalized word — the shape `` `<path>.md` Section Name ``.
SECTION_REFERENCE_TRIGGER = re.compile(r"`([\w./+-]+\.md)`[ \t]+(?=[A-Z])")
HEADING_LINE = re.compile(r"^#{1,4}(?!#)[ \t]+(.+?)\s*$")
LABEL_DELIMITER = re.compile(r"--|[:.—]")
SECTION_CANDIDATE_WORD_CAP = 15
TRAILING_PUNCTUATION = ")]},.:;'\"*"


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


def _heading_positions(text: str) -> list[str]:
    """Any-level (H1-H4) markdown heading text, one referenceable position per line."""
    positions = []
    for line in text.splitlines():
        match = HEADING_LINE.match(line)
        if match:
            positions.append(match.group(1))
    return positions


def _label_positions(text: str) -> list[str]:
    """Line-start label text, extracted up to the first delimiter (or end of line).

    Leading whitespace and an optional `**` wrap are stripped before the delimiter scan;
    a trailing `**` closing the same wrap is stripped from the extracted label.
    """
    positions = []
    for line in text.splitlines():
        body = line.lstrip()
        if not body:
            continue
        if body.startswith("**"):
            body = body[2:]
        match = LABEL_DELIMITER.search(body)
        label = body[: match.start()] if match else body
        label = label.rstrip()
        if label.endswith("**"):
            label = label[:-2].rstrip()
        if label:
            positions.append(label)
    return positions


@functools.lru_cache(maxsize=None)
def referenceable_positions(target: Path) -> tuple[str, ...]:
    text = target.read_text(encoding="utf-8")
    return tuple(_heading_positions(text) + _label_positions(text))


def resolve_section_reference(target: Path, tail: str) -> str | None:
    """Longest word-prefix of `tail` that resolves against a referenceable position in
    `target` (equal to it, or a prefix of it), tried from longest to shortest. Returns
    None when no candidate resolves.
    """
    positions = referenceable_positions(target)
    tokens = tail.split()[:SECTION_CANDIDATE_WORD_CAP]
    for k in range(len(tokens), 0, -1):
        candidate = " ".join(tokens[:k]).rstrip(TRAILING_PUNCTUATION)
        if not candidate:
            continue
        for position in positions:
            if position == candidate or position.startswith(candidate):
                return candidate
    return None


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

    def test_every_section_name_reference_resolves(self) -> None:
        for path in scanned_files():
            text = path.read_text(encoding="utf-8")
            lines = text.splitlines()
            line_offsets: list[int] = []
            offset = 0
            for line in lines:
                line_offsets.append(offset)
                offset += len(line) + 1

            for match in SECTION_REFERENCE_TRIGGER.finditer(text):
                raw_target = match.group(1)
                target = ROOT / raw_target
                line_index = bisect.bisect_right(line_offsets, match.start()) - 1
                tail = lines[line_index][match.end() - line_offsets[line_index] :]
                with self.subTest(
                    source=str(path.relative_to(ROOT)),
                    target=raw_target,
                    line=line_index + 1,
                ):
                    self.assertTrue(
                        target.is_file(),
                        f"{path.relative_to(ROOT)}:{line_index + 1} references "
                        f"`{raw_target}`, which does not resolve to a file",
                    )
                    if not target.is_file():
                        continue
                    resolved = resolve_section_reference(target, tail)
                    self.assertIsNotNone(
                        resolved,
                        f"{path.relative_to(ROOT)}:{line_index + 1} references "
                        f"`{raw_target}` {tail[:80]!r}, but no word-prefix of that "
                        "text resolves to a referenceable position (heading or "
                        "line-start label, see docs/K.-Source-File-Format.md) in "
                        "the target",
                    )


if __name__ == "__main__":
    unittest.main()
