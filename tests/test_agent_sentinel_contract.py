"""Contract tests for the sentinel-owned region in adapter agent sources.

Scope = the source files under `adapter/*/agents/` and the literal of
`Li+update.md`. These assert the region's structural invariants and the
presence of the clauses 4c.6 / 4x.5 promise.

Which sources carry a region is decided by the criterion in 4c.6, so the
carrier set is whatever that criterion currently admits — possibly empty. The
per-source shape assertions are conditional on it and go vacuous when it is;
branch (b)'s replacement semantic does not, because it runs against the
synthetic carriers below rather than against the live set.

Not covered, and not statically coverable: the bootstrap's runtime behavior.
`Li+update.md` is prose an AI executes, so branch (a) creation, the branch (c)
ask and its two outcomes, "no stale removal", and the directory create / skip
steps have no assertion here. Branch (b)'s replacement is exercised only
against this module's own `apply_region_update()`, which is a proxy for the
procedure and not the procedure itself. Reading is the detector for those
(`rules/evolution/initiator-autonomy.md` Governed surface); green here does
not mean a bootstrap run behaved as specified.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TAG_TOKEN = "{LI_PLUS_TAG}"
BEGIN_LITERAL = "Li+ BEGIN"
END_LITERAL = "Li+ END"
BEGIN_TAG_RE = re.compile(r"Li\+ BEGIN \(([^)]*)\)")

# Li+update.md 4c.6 names these as the worked example of the question-2 branch
# (Li+-owned criteria interleaved with a Character_Instance literal, so no one
# contiguous region separates them). Pinning them here tests a claim the spec
# already makes by name; it is not a second enumeration of the criterion.
NAMED_NON_CARRIERS = (
    "adapter/claude/agents/dialogue-evaluator.md",
    "adapter/codex/agents/dialogue-evaluator.toml",
)

# Instance-surface keys the Codex region must leave outside itself.
CODEX_INSTANCE_KEYS = ("name = ", "description = ", "model_reasoning_effort = ", "sandbox_mode = ")


# One synthetic carrier per port, shaped as 4c.6 / 4x.5 require. These exist so
# the branch (b) replacement semantic is exercised whether or not the live
# carrier set is empty; they are not a claim about which real source carries a
# region, which only the 4c.6 criterion decides.
SYNTHETIC_CARRIERS = {
    "synthetic.md": (
        "---\n"
        "name: synthetic\n"
        "description: synthetic carrier fixture\n"
        "tools: Read\n"
        "---\n"
        "\n"
        "<!-- --- Li+ BEGIN ({LI_PLUS_TAG}) --- -->\n"
        "\n"
        "Owned criteria body.\n"
        "\n"
        "<!-- --- Li+ END --- -->\n"
    ),
    "synthetic.toml": (
        "# Source: adapter/codex/agents/synthetic.toml\n"
        "\n"
        'name = "synthetic"\n'
        'description = "synthetic carrier fixture"\n'
        'model_reasoning_effort = "high"\n'
        'sandbox_mode = "read-only"\n'
        "\n"
        "# --- Li+ BEGIN ({LI_PLUS_TAG}) ---\n"
        'developer_instructions = """\n'
        "Owned criteria body.\n"
        '"""\n'
        "# --- Li+ END ---\n"
    ),
}


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

    def test_every_agent_source_is_a_carrier_or_a_create_only_file(self) -> None:
        # No third state: a file either holds one well-formed owned region or
        # holds neither sentinel. A half-written region would be copied whole
        # by the Create-only branch and never refreshed by a tag bump.
        for name, text in self.sources.items():
            with self.subTest(source=name):
                if BEGIN_LITERAL in text:
                    self.assertIn(END_LITERAL, text)
                else:
                    self.assertNotIn(END_LITERAL, text)

    def test_named_non_carriers_carry_no_region(self) -> None:
        for name in NAMED_NON_CARRIERS:
            with self.subTest(source=name):
                self.assertIn(name, self.sources)
                self.assertNotIn(BEGIN_LITERAL, self.sources[name])
                self.assertNotIn(END_LITERAL, self.sources[name])

    def test_non_carrier_toml_keeps_its_tag_in_the_source_header(self) -> None:
        for name, text in self.sources.items():
            if not name.endswith(".toml") or BEGIN_LITERAL in text:
                continue
            with self.subTest(source=name):
                header = text.splitlines()[0]
                self.assertTrue(header.startswith("# Source: "))
                self.assertIn(TAG_TOKEN, header)

    def test_codex_region_wraps_developer_instructions_only(self) -> None:
        for name, text in self.carriers().items():
            if not name.endswith(".toml"):
                continue
            with self.subTest(source=name):
                before, section, _ = split_region(text)
                # The criteria body is the region; the instance surface is not.
                self.assertIn('developer_instructions = """', section)
                self.assertNotIn('developer_instructions = """', before)
                self.assertTrue(section.rstrip().endswith("---"))
                self.assertIn('"""', section[section.index('developer_instructions = """') + 30 :])
                for key in CODEX_INSTANCE_KEYS:
                    self.assertIn(key, before)
                    self.assertNotIn(key, section)

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

    def test_tag_bump_replaces_the_region_and_preserves_everything_outside(self) -> None:
        for name, source in {**SYNTHETIC_CARRIERS, **self.carriers()}.items():
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
                "4x.5. Generate .codex/agents/ files (sentinel-owned region mirror):",
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

    def test_update_procedure_keeps_the_promises_the_region_rests_on(self) -> None:
        update = (ROOT / "Li+update.md").read_text(encoding="utf-8")
        claude = update_section(
            update,
            "4c.6. Generate .claude/agents/ files (sentinel-owned region mirror):",
            "### Phase 4 codex",
        )
        # Branch (b) must promise verbatim preservation outside the region.
        self.assertIn("Preserve content outside this section verbatim", claude)
        # The 4c.1 trailer migration must stay excluded from this branch: it
        # would delete user content on a surface that has no legacy trailer.
        self.assertIn(
            "legacy webhook trailer migration does NOT apply on this branch", claude
        )
        # The carrier criterion must keep its second question; question 1 alone
        # classifies a mixed file as a carrier.
        self.assertIn("Can one contiguous region cover that body", claude)
        # Branch (c)'s "skip" must name what re-raises the ask.
        self.assertIn("Re-ask cadence", claude)


if __name__ == "__main__":
    unittest.main()
