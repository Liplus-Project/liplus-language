from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TAG_TOKEN = "{LI_PLUS_TAG}"
BEGIN_LITERAL = "Li+ BEGIN"
END_LITERAL = "Li+ END"
BEGIN_TAG_RE = re.compile(r"Li\+ BEGIN \(([^)]*)\)")

# The two ports of the brake-2 evaluator. Its criteria body is what the
# Create-only mirror froze out of installed workspaces (#1740), so both ports
# must carry the owned region. Which OTHER sources carry one is decided by the
# criterion in Li+update.md 4c.6, not by a list here.
REQUIRED_CARRIERS = (
    "adapter/claude/agents/l1-gate-eval.md",
    "adapter/codex/agents/l1-gate-eval.toml",
)

SKILLS_DISABLE_MARKER = "# --- Skills disable enumeration (filled by bootstrap) ---"


def agent_sources() -> list[Path]:
    sources: list[Path] = []
    for adapter, pattern in (("claude", "*.md"), ("codex", "*.toml")):
        sources.extend(sorted((ROOT / "adapter" / adapter / "agents").glob(pattern)))
    return sources


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def split_region(text: str) -> tuple[str, str, str]:
    """Split into (before, owned region incl. both sentinel lines, after)."""
    begin = text.index(BEGIN_LITERAL)
    start = text.rindex("\n", 0, begin) + 1
    end = text.index("\n", text.index(END_LITERAL, begin)) + 1
    return text[:start], text[start:end], text[end:]


def render(text: str, tag: str) -> str:
    return text.replace(TAG_TOKEN, tag)


def apply_region_update(installed: str, rendered_source: str) -> str:
    """The 4c.6 / 4x.5 branch (b) replacement: region in, everything else kept."""
    before, _, after = split_region(installed)
    _, section, _ = split_region(rendered_source)
    return before + section + after


def normalized(text: str) -> str:
    return re.sub(r"\s+", " ", text)


def update_section(update: str, start: str, end: str) -> str:
    return normalized(update[update.index(start) : update.index(end, update.index(start))])


class AgentSentinelContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.sources = {rel(path): path.read_text(encoding="utf-8") for path in agent_sources()}
        self.assertNotEqual(self.sources, {})

    def carriers(self) -> dict[str, str]:
        return {name: text for name, text in self.sources.items() if BEGIN_LITERAL in text}

    def test_the_brake_2_evaluator_carries_the_owned_region_on_both_ports(self) -> None:
        for name in REQUIRED_CARRIERS:
            with self.subTest(source=name):
                self.assertIn(name, self.sources)
                text = self.sources[name]
                _, section, _ = split_region(text)
                self.assertIn("Li+ root criteria:", section)
                self.assertIn("verdict = PASS or DEVIATION", section)

    def test_each_region_is_a_single_well_formed_span(self) -> None:
        for name, text in self.carriers().items():
            with self.subTest(source=name):
                self.assertEqual(text.count(BEGIN_LITERAL), 1)
                self.assertEqual(text.count(END_LITERAL), 1)
                self.assertLess(text.index(BEGIN_LITERAL), text.index(END_LITERAL))
                before, section, after = split_region(text)
                self.assertEqual(before + section + after, text)
                self.assertTrue(section.endswith("\n"))

    def test_the_sentinel_is_the_only_tag_carrier_in_a_region_file(self) -> None:
        for name, text in self.carriers().items():
            with self.subTest(source=name):
                match = BEGIN_TAG_RE.search(text)
                self.assertIsNotNone(match)
                self.assertEqual(match.group(1), TAG_TOKEN)
                # A second tag outside the region would freeze at the install
                # tag, because only the region is rewritten on a tag bump.
                self.assertEqual(text.count(TAG_TOKEN), 1)

    def test_markdown_frontmatter_stays_outside_the_region(self) -> None:
        for name, text in self.carriers().items():
            if not name.endswith(".md"):
                continue
            with self.subTest(source=name):
                self.assertTrue(text.startswith("---\n"))
                frontmatter_close = text.index("\n---\n", 3) + len("\n---\n")
                self.assertLess(frontmatter_close, text.index(BEGIN_LITERAL))

    def test_codex_skills_disable_enumeration_stays_outside_the_region(self) -> None:
        text = self.sources["adapter/codex/agents/l1-gate-eval.toml"]
        self.assertIn(SKILLS_DISABLE_MARKER, text)
        self.assertGreater(text.index(SKILLS_DISABLE_MARKER), text.index(END_LITERAL))

    def test_tag_bump_replaces_the_region_and_preserves_everything_outside(self) -> None:
        for name, source in self.carriers().items():
            with self.subTest(source=name):
                before, old_section, after = split_region(render(source, "build-old"))
                installed = (
                    before
                    + "USER-OWNED-INSTANCE-LINE\n"
                    + old_section
                    + after
                    + "\nUSER-OWNED-TAIL\n"
                )
                rendered = render(source, "build-new")
                updated = apply_region_update(installed, rendered)

                self.assertIn("USER-OWNED-INSTANCE-LINE", updated)
                self.assertTrue(updated.endswith("\nUSER-OWNED-TAIL\n"))
                self.assertIn("build-new", updated)
                self.assertNotIn("build-old", updated)
                self.assertNotIn(TAG_TOKEN, updated)
                _, new_section, _ = split_region(rendered)
                self.assertEqual(split_region(updated)[1], new_section)

                # Re-applying the same tag is a no-op (branch (b) "skip").
                self.assertEqual(apply_region_update(updated, rendered), updated)

    def test_update_procedure_states_the_three_branch_region_judgment(self) -> None:
        update = (ROOT / "Li+update.md").read_text(encoding="utf-8")
        sections = {
            "4c.6": update_section(
                update,
                "4c.6. Generate .claude/agents/ files (sentinel-owned region mirror):",
                "### Phase 4 codex",
            ),
            "4x.5": update_section(
                update,
                "4x.5. Generate .codex/agents/ files "
                "(sentinel-owned region mirror + skills-disable enumeration):",
                "## Phase 5",
            ),
        }
        for step, section in sections.items():
            with self.subTest(step=step):
                self.assertIn('Source WITHOUT a "Li+ BEGIN" sentinel (Create-only)', section)
                self.assertIn('Source WITH a "Li+ BEGIN" sentinel', section)
                self.assertIn("If Target does not exist", section)
                self.assertRegex(section, r"matches (the )?current target tag[:,] skip")
                self.assertIn("ask user -- regenerate", section)


if __name__ == "__main__":
    unittest.main()
