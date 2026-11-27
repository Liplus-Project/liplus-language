"""Delivery-mode rendering of the Claude `settings.json` template (#2226).

Observed here: the literal JSON block in `adapter/claude/hooks-settings.md`,
rendered by the removal that its Delivery-mode rendering section states for
`LI_PLUS_WEBHOOK_DELIVERY=channel` (the six lines of the `type: "mcp_tool"`
object, and the `,` that ends the line before them), parses as JSON, leaves the
UserPromptSubmit `hooks` array with the `on-user-prompt.sh` command entry only,
and differs from the unrendered literal in that one entry and nothing else.
The unrendered literal carries the entry once.

The stated six-line count is held as a constant here, and the span it names in
the literal is checked to open with `{` and close with `}` at one indentation,
so an edit to the `mcp_tool` object that the stated removal no longer matches
fails here.

Where the rendering is fixed: `adapter/claude/hooks-settings.md`
Delivery-mode rendering, and `Li+update.md` 4c.4 for the bootstrap step that
compares against it.
"""

from __future__ import annotations

import copy
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SETTINGS_DOC = ROOT / "adapter" / "claude" / "hooks-settings.md"
UPDATE_DOC = ROOT / "Li+update.md"
MCP_TOOL_TYPE_LINE = '"type": "mcp_tool",'
OBJECT_LINES = 6


def template_literal() -> str:
    text = SETTINGS_DOC.read_text(encoding="utf-8")
    block = re.search(r"```json\n(.*?)\n```", text, re.S)
    if block is None:
        raise AssertionError("no JSON block in hooks-settings.md")
    return block.group(1)


def mcp_tool_object_span(lines: list[str]) -> tuple[int, int]:
    """Return [start, end) of the `mcp_tool` object, from its `{` to its `}`."""
    type_rows = [i for i, line in enumerate(lines) if line.strip() == MCP_TOOL_TYPE_LINE]
    if len(type_rows) != 1:
        raise AssertionError(f"expected one mcp_tool entry, found {len(type_rows)}")
    start = type_rows[0] - 1
    end = start + OBJECT_LINES
    return start, end


def render_channel(literal: str) -> str:
    lines = literal.split("\n")
    start, end = mcp_tool_object_span(lines)
    before = lines[start - 1]
    if not before.endswith(","):
        raise AssertionError(f"line before the mcp_tool object does not end in ',': {before!r}")
    lines[start - 1] = before[:-1]
    del lines[start:end]
    return "\n".join(lines)


def user_prompt_hooks(settings: dict) -> list[dict]:
    entries = settings["hooks"]["UserPromptSubmit"]
    return [hook for entry in entries for hook in entry["hooks"]]


class ChannelRenderingTestCase(unittest.TestCase):
    def test_stated_removal_matches_the_literal_object(self) -> None:
        lines = template_literal().split("\n")
        start, end = mcp_tool_object_span(lines)
        self.assertEqual(lines[start].strip(), "{")
        self.assertEqual(lines[end - 1].strip(), "}")
        self.assertEqual(lines[start].index("{"), lines[end - 1].index("}"))

    def test_channel_render_drops_the_mcp_tool_entry_only(self) -> None:
        literal = template_literal()
        full = json.loads(literal)
        rendered = json.loads(render_channel(literal))

        hooks = user_prompt_hooks(rendered)
        self.assertEqual([hook["type"] for hook in hooks], ["command"])
        self.assertIn("on-user-prompt.sh", hooks[0]["command"])

        expected = copy.deepcopy(full)
        for entry in expected["hooks"]["UserPromptSubmit"]:
            entry["hooks"] = [h for h in entry["hooks"] if h.get("type") != "mcp_tool"]
        self.assertEqual(rendered, expected)

    def test_unrendered_literal_carries_the_entry(self) -> None:
        hooks = user_prompt_hooks(json.loads(template_literal()))
        tools = [h for h in hooks if h["type"] == "mcp_tool"]
        self.assertEqual(len(tools), 1)
        self.assertEqual(tools[0]["server"], "github-webhook-mcp")
        self.assertEqual(tools[0]["tool"], "get_pending_status")


class RenderingIsNamedTestCase(unittest.TestCase):
    def test_settings_doc_holds_the_rendering_section(self) -> None:
        text = SETTINGS_DOC.read_text(encoding="utf-8")
        section = re.search(r"^## Delivery-mode rendering\n(.*?)(?=^## )", text, re.S | re.M)
        self.assertIsNotNone(section, "no Delivery-mode rendering section")
        self.assertIn("Value `channel`", section.group(1))

    def test_bootstrap_step_renders_per_that_section(self) -> None:
        text = UPDATE_DOC.read_text(encoding="utf-8")
        step = re.search(r"^4c\.4\. Bootstrap hooks:\n(.*?)(?=^4c\.5\. )", text, re.S | re.M)
        self.assertIsNotNone(step, "no 4c.4 step in Li+update.md")
        self.assertIn("Delivery-mode rendering", step.group(1))


if __name__ == "__main__":
    unittest.main()
