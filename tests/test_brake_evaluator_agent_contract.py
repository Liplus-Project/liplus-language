"""Contract tests for the brake 1 judge-type evaluator's agent definition.

Scope = `adapter/claude/agents/brake-evaluator.md`,
`adapter/codex/agents/brake-evaluator.toml`, and the two skill literals that
route judge-type rounds to them and keep probe-type rounds off them.

Why a test rather than reading attention: the definition exists for one field
(thinking effort, for which the spawn call carried no parameter on either host
as of 2026-09-13), and losing it is silent — the
spawn still succeeds at whatever effort the session carries, which is the state
measured on 2026-09-13, and nothing reports the drop. The `model` and `tools`
absences are the same shape in the other direction: a `model` key here would
take over the per-call sonnet floor, and a `tools` key would express the
no-write requirement as a permission, which
`skills/evolution-parallel-agent-eval/SKILL.md` Non-scope rejects.

The sentinel region's structural invariants are not re-asserted here;
`tests/test_agent_sentinel_contract.py` already runs them over every source
under `adapter/*/agents/`, this pair included.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLAUDE_AGENT = ROOT / "adapter" / "claude" / "agents" / "brake-evaluator.md"
CODEX_AGENT = ROOT / "adapter" / "codex" / "agents" / "brake-evaluator.toml"
EVAL_SKILL = ROOT / "skills" / "evolution-parallel-agent-eval" / "SKILL.md"
SPAWN_SKILL = ROOT / "skills" / "task-subagent-spawn" / "SKILL.md"


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


def body(text: str) -> str:
    """The owned region's prose, sentinel lines excluded."""
    start = text.index("\n", text.index("Li+ BEGIN")) + 1
    return text[start : text.rindex("\n", 0, text.index("Li+ END"))]


class BrakeEvaluatorAgentContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.claude = CLAUDE_AGENT.read_text(encoding="utf-8")
        self.codex = CODEX_AGENT.read_text(encoding="utf-8")

    def test_both_ports_exist_and_carry_the_same_agent_name(self) -> None:
        self.assertEqual(frontmatter(self.claude)["name"], "brake-evaluator")
        self.assertIn('name = "brake-evaluator"', self.codex)

    def test_thinking_effort_is_pinned_medium_on_both_ports(self) -> None:
        # The single field the definition exists for. Master fixed the value on
        # 2026-09-13 at one step above the `low` the evaluators were measured
        # running at; `medium` against `high` is untested (#1968).
        self.assertEqual(frontmatter(self.claude)["effort"], "medium")
        self.assertIn('model_reasoning_effort = "medium"', self.codex)

    def test_neither_port_pins_a_model(self) -> None:
        # The sonnet-class floor stays an explicit spawn-call parameter
        # (`skills/evolution-parallel-agent-eval/SKILL.md` Constraint: Model
        # floor). A pin here takes that axis over silently.
        self.assertNotIn("model", frontmatter(self.claude))
        self.assertIsNone(re.search(r"^\s*model\s*=", self.codex, re.MULTILINE))

    def test_neither_port_restricts_tools(self) -> None:
        # The no-write requirement rests on a prompt literal, and the `tools:`
        # route is rejected outright (same skill, Non-scope). A read-only Codex
        # sandbox is that route in the other spelling, and it would also refuse
        # the clone a repository-wide axis is allowed to make.
        self.assertNotIn("tools", frontmatter(self.claude))
        self.assertIn('sandbox_mode = "workspace-write"', self.codex)

    def test_the_definition_body_carries_role_only(self) -> None:
        # The body replaces the subagent's system prompt, so evaluation content
        # placed here would steer every round it is spawned for. What may stand
        # in it is the role; the axes and the criteria arrive in the prompt.
        prose = body(self.claude)
        for steering in ("axis", "Axis", "finding is one", "Verdict terms", "Basis"):
            with self.subTest(literal=steering):
                self.assertNotIn(steering, prose)
        self.assertIn("arrives in that prompt", prose)

    def test_the_eval_skill_routes_judge_type_rounds_to_the_definition(self) -> None:
        evaluation = EVAL_SKILL.read_text(encoding="utf-8")
        self.assertIn("subagent_type: brake-evaluator", evaluation)
        self.assertIn("adapter/claude/agents/brake-evaluator.md", evaluation)
        self.assertIn("adapter/codex/agents/brake-evaluator.toml", evaluation)
        self.assertIn("Effort floor = `medium`", evaluation)

    def test_the_probe_type_round_reaches_the_floor_through_the_parent(self) -> None:
        # Effort is not a spawn-call parameter and the probe-type round takes
        # no definition, so the only surface left is the parent session itself.
        evaluation = EVAL_SKILL.read_text(encoding="utf-8")
        self.assertIn(
            "raise the parent session's effort to the floor before spawning one",
            evaluation,
        )

    def test_the_spawn_policy_scopes_its_prohibition_to_probe_type(self) -> None:
        # A literal wider than its reason bars this file: the reason is the
        # observation target, which a judge-type evaluator does not carry.
        spawn = SPAWN_SKILL.read_text(encoding="utf-8")
        self.assertIn("the probe-type brake 1 evaluators", spawn)
        self.assertIn("judge-type brake 1 evaluator", spawn)


if __name__ == "__main__":
    unittest.main()
