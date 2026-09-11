"""Contract tests for the Li+ implementation delegate's agent definition.

Scope = `adapter/claude/agents/implementer.md`, `adapter/codex/agents/implementer.toml`,
and the spawn-policy literal that routes delegations to them.

Why a test rather than reading attention: the definition exists for exactly one
field (thinking effort, which no spawn-call parameter can set), and losing that
field is silent — the spawn still succeeds, at whatever effort the host defaults
to, and nothing reports the drop. The `model` absence is the same shape in the
other direction: adding a `model` pin here would silently take over the tier
inheritance that `skills/task-subagent-spawn/SKILL.md` keeps at the spawn call.

The sentinel region's structural invariants are not re-asserted here;
`tests/test_agent_sentinel_contract.py` already runs them over every source under
`adapter/*/agents/`, this pair included.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLAUDE_AGENT = ROOT / "adapter" / "claude" / "agents" / "implementer.md"
CODEX_AGENT = ROOT / "adapter" / "codex" / "agents" / "implementer.toml"
SPAWN_SKILL = ROOT / "skills" / "task-subagent-spawn" / "SKILL.md"
DELEGATION_SKILL = ROOT / "skills" / "task-subagent-delegation" / "SKILL.md"
EVAL_SKILL = ROOT / "skills" / "evolution-parallel-agent-eval" / "SKILL.md"


def frontmatter(text: str) -> dict[str, str]:
    lines = text.split("\n")
    assert lines[0].strip() == "---"
    close = lines.index("---", 1)
    fields: dict[str, str] = {}
    for line in lines[1:close]:
        if ":" in line and not line.startswith((" ", "\t")):
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip()
    return fields


class ImplementerAgentContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.claude = CLAUDE_AGENT.read_text(encoding="utf-8")
        self.codex = CODEX_AGENT.read_text(encoding="utf-8")

    def test_both_ports_exist_and_carry_the_same_agent_name(self) -> None:
        self.assertEqual(frontmatter(self.claude)["name"], "implementer")
        self.assertIn('name = "implementer"', self.codex)

    def test_thinking_effort_is_pinned_high_on_both_ports(self) -> None:
        # The single field the definition exists for. No spawn-call parameter
        # sets it, so its loss is silent.
        self.assertEqual(frontmatter(self.claude)["effort"], "high")
        self.assertIn('model_reasoning_effort = "high"', self.codex)

    def test_neither_port_pins_a_model(self) -> None:
        # Tier inheritance stays at the spawn call by omission
        # (`skills/task-subagent-spawn/SKILL.md`). A pin here takes it over
        # silently and rots the moment the parent tier changes.
        self.assertNotIn("model", frontmatter(self.claude))
        self.assertIsNone(re.search(r"^\s*model\s*=", self.codex, re.MULTILINE))

    def test_codex_port_can_write_to_the_repository(self) -> None:
        # This role commits and pushes; the evaluator's read-only sandbox would
        # fail it at the first write with no other detector.
        self.assertIn('sandbox_mode = "workspace-write"', self.codex)

    def test_spawn_policy_names_the_agent_for_delegations(self) -> None:
        spawn = SPAWN_SKILL.read_text(encoding="utf-8")
        self.assertIn("subagent_type: implementer", spawn)
        self.assertIn("adapter/claude/agents/implementer.md", spawn)
        self.assertIn("adapter/codex/agents/implementer.toml", spawn)
        self.assertIn("skills/task-subagent-delegation/SKILL.md", spawn)

    def test_the_definition_prohibition_is_scoped_to_the_observation_target(self) -> None:
        # Narrowed from a blanket prohibition: the reason (a definition body
        # replaces the system prompt brake 1 observes) reaches the evaluators
        # and nothing else. A literal wider than its reason bars this file.
        spawn = SPAWN_SKILL.read_text(encoding="utf-8")
        self.assertIn("whose bare behavior is the observation target", spawn)
        self.assertIn("Outside the evaluators a definition file is permitted", spawn)

    def test_brake_evaluators_stay_on_the_built_in_agent(self) -> None:
        evaluation = EVAL_SKILL.read_text(encoding="utf-8")
        self.assertIn("built-in general-purpose agent", evaluation)
        self.assertIn("no Li+ agent definition file", evaluation)

    def test_delegation_skill_routes_the_agent_type_choice_to_the_spawn_skill(self) -> None:
        delegation = DELEGATION_SKILL.read_text(encoding="utf-8")
        self.assertIn(
            "the agent type these delegations name", delegation
        )

    def test_running_sessions_are_named_as_reached_by_a_definition_change(self) -> None:
        # Measured 2026-09-11: an edit takes effect on the next spawn in an
        # already-running session, with no notice emitted.
        spawn = SPAWN_SKILL.read_text(encoding="utf-8")
        self.assertIn("take effect on the next spawn, in sessions already running", spawn)


if __name__ == "__main__":
    unittest.main()
