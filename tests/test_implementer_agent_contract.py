"""Contract tests for the Li+ implementation delegate's agent definition.

Scope = `adapter/claude/agents/implementer.md`, `adapter/codex/agents/implementer.toml`,
and the spawn-policy literal that routes delegations to them.

Why a test rather than reading attention: Claude pins thinking effort in the
definition while Codex resolves it per launch. Either losing the Claude field or
reintroducing the Codex override is silent — the spawn still succeeds at a
different effort. The `model` absence is the same shape in the other direction:
adding a `model` pin here would silently take over the tier inheritance that
`skills/task-subagent-spawn/SKILL.md` keeps at the spawn call.

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

    def test_thinking_effort_uses_each_hosts_supported_surface(self) -> None:
        # Claude has no per-call effort argument; Codex does, and an agent-file
        # value would override the resolved per-launch value.
        self.assertEqual(frontmatter(self.claude)["effort"], "high")
        self.assertIsNone(
            re.search(r"^\s*model_reasoning_effort\s*=", self.codex, re.MULTILINE)
        )
        spawn = SPAWN_SKILL.read_text(encoding="utf-8")
        self.assertIn('Codex spawn passes `reasoning_effort="high"`', spawn)

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
        self.assertIn("It reaches no other Claude spawn", spawn)

    def test_probe_type_evaluators_stay_on_the_built_in_agent(self) -> None:
        # Narrowed 2026-09-14 (#1968): the judge-type evaluator now carries its
        # own definition. What keeps no definition is the probe-type round,
        # whose bare behavior is the thing being read.
        evaluation = EVAL_SKILL.read_text(encoding="utf-8")
        self.assertIn("A probe-type evaluator spawns as the host's", evaluation)
        self.assertIn("built-in general-purpose agent", evaluation)
        self.assertIn("no Li+ agent definition file", evaluation)

    def test_delegation_skill_routes_the_agent_type_choice_to_the_spawn_skill(self) -> None:
        # Observed: the delegation skill's spawn-parameter bullet points at the
        # spawn skill, where the agent type choice is fixed
        # (`skills/task-subagent-spawn/SKILL.md`). The pointer is what is
        # asserted; an enumeration of the spawn skill's sections restated in the
        # delegation skill would be a second copy of them.
        delegation = DELEGATION_SKILL.read_text(encoding="utf-8")
        routing = [
            line
            for line in delegation.split("\n")
            if "Setting the Agent tool spawn parameters" in line
        ]
        self.assertEqual(len(routing), 1)
        self.assertIn("skills/task-subagent-spawn/SKILL.md", routing[0])

    def test_running_sessions_are_named_as_reached_by_a_definition_change(self) -> None:
        # Measured 2026-09-11: an edit takes effect on the next spawn in an
        # already-running session, with no notice emitted.
        spawn = SPAWN_SKILL.read_text(encoding="utf-8")
        self.assertIn("take effect on the next spawn, in sessions already running", spawn)


if __name__ == "__main__":
    unittest.main()
