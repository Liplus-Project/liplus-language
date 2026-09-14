"""Contract tests for the brake 1 judge-type evaluator's agent definition.

Scope = `adapter/claude/agents/medium.md`, `adapter/codex/agents/brake-evaluator.toml`,
and the skill literals that route judge-type rounds to them, carry the
judge-type role on the Claude side, and keep probe-type rounds off them.

Reorganized at #1972: `adapter/claude/agents/` no longer carries a
`brake-evaluator.md`. The judge-type role literal that used to live in that
file's body now lives in `skills/evolution-parallel-agent-eval/SKILL.md`
Constraint: Effort floor, and the Claude Code spawn selects the effort-named
`medium.md` (or a higher effort-named agent) instead of a role-named
definition. The Codex port is out of scope for this split (Master agreement,
2026-09-14): its role definition remains as a compatibility source, while
#1973 moves brake 1 effort and role delivery to the spawn call and prompt.

Why a test rather than reading attention: Claude resolves thinking effort in
the definition while Codex resolves it per launch. Losing the Claude pin or
reintroducing the Codex override is silent — the spawn still succeeds at a
different effort. The `model` and `tools` absences are the same shape in the other direction: a
`model` key here would take over the per-call sonnet floor, and a `tools` key
would express the no-write requirement as a permission, which
`skills/evolution-parallel-agent-eval/SKILL.md` Non-scope rejects. On the
Claude side, a role fragment written into `medium.md` would silently duplicate
the role literal now canonical in the eval skill, and would also steer every
other medium-effort spawn that is not a brake evaluator at all.

The sentinel region's structural invariants are not re-asserted here;
`tests/test_agent_sentinel_contract.py` already runs them over every source
under `adapter/*/agents/`, this pair included.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLAUDE_AGENT = ROOT / "adapter" / "claude" / "agents" / "medium.md"
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

    def test_claude_agent_is_named_by_effort_not_role(self) -> None:
        # Deliberately not "brake-evaluator" any more: #1972 dropped per-role
        # Claude Code definitions. The Codex port keeps its own role name.
        self.assertEqual(frontmatter(self.claude)["name"], "medium")
        self.assertEqual(frontmatter(self.claude)["effort"], "medium")
        self.assertIn('name = "brake-evaluator"', self.codex)

    def test_thinking_effort_uses_each_hosts_supported_surface(self) -> None:
        # Master fixed the floor on 2026-09-13 at one step above the observed
        # Claude `low`; Codex can carry the same value per launch.
        self.assertEqual(frontmatter(self.claude)["effort"], "medium")
        self.assertIsNone(
            re.search(r"^\s*model_reasoning_effort\s*=", self.codex, re.MULTILINE)
        )
        evaluation = EVAL_SKILL.read_text(encoding="utf-8")
        self.assertIn('explicitly pass `reasoning_effort="medium"`', evaluation)

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

    def test_claude_definition_carries_no_role_fragment(self) -> None:
        # medium.md is shared by every medium-effort Claude Code spawn, not
        # just the judge-type evaluator. Evaluation content placed here would
        # steer every round any medium-effort agent is spawned for, not only
        # brake 1 rounds.
        prose = body(self.claude)
        self.assertIn("no role, no procedure", prose)
        for steering in ("axis", "Axis", "finding is one", "Verdict terms", "Basis", "evaluator"):
            with self.subTest(literal=steering):
                self.assertNotIn(steering, prose)

    def test_the_role_literal_lives_in_the_eval_skill(self) -> None:
        # The one place the judge-type role now lives on Claude Code, per
        # #1972 decision point 4 (role conveyed by prompt, held in exactly one
        # skill — the eval skill for judge-type, the prompt skill for the
        # implementation delegate).
        evaluation = EVAL_SKILL.read_text(encoding="utf-8")
        self.assertIn("You are a Li+ brake 1 evaluator.", evaluation)
        self.assertIn("arrives in that prompt", evaluation)
        self.assertIn("Do not write a role fragment into", evaluation)

    def test_the_eval_skill_routes_each_host_to_its_effort_surface(self) -> None:
        evaluation = EVAL_SKILL.read_text(encoding="utf-8")
        self.assertIn("subagent_type: medium", evaluation)
        self.assertNotIn("adapter/codex/agents/brake-evaluator.toml", evaluation)
        self.assertIn("On Codex, both kinds spawn with no agent definition file", evaluation)
        self.assertIn("Effort floor = `medium`", evaluation)

    def test_the_probe_type_round_reaches_the_floor_through_the_parent(self) -> None:
        # Claude has no per-call effort argument, so its probe reaches the floor
        # through the parent. Codex passes the floor at the call instead.
        evaluation = EVAL_SKILL.read_text(encoding="utf-8")
        self.assertIn(
            "raise the parent session's effort to the floor before spawning one",
            evaluation,
        )
        self.assertIn(
            'On Codex, both kinds spawn with no agent definition file and explicitly pass `reasoning_effort="medium"`',
            evaluation,
        )

    def test_the_spawn_policy_scopes_its_prohibition_to_probe_type(self) -> None:
        # A literal wider than its reason bars this file: the reason is the
        # observation target, which a judge-type evaluator does not carry.
        spawn = SPAWN_SKILL.read_text(encoding="utf-8")
        self.assertIn("the probe-type brake 1 evaluators", spawn)
        self.assertIn("judge-type brake 1 evaluator", spawn)

    def test_the_spawn_policy_names_the_effort_floor_agent(self) -> None:
        spawn = SPAWN_SKILL.read_text(encoding="utf-8")
        self.assertIn("adapter/claude/agents/medium.md", spawn)


if __name__ == "__main__":
    unittest.main()
