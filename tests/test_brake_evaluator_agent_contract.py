"""Contract tests for the brake 1 judge-type evaluator's agent definition.

Scope = `adapter/claude/agents/low.md` and the skill literals that route
judge-type rounds to it, carry the judge-type role, and keep probe-type rounds
off it.

Reorganized at #1972: `adapter/claude/agents/` no longer carries a
`brake-evaluator.md`. The judge-type role literal that used to live in that
file's body now lives in `skills/evolution-parallel-agent-eval/SKILL.md`
Constraint: Effort floor, and the Claude Code spawn selects the effort-named
`low.md` (or a higher effort-named agent) instead of a role-named
definition. The floor value these tests assert is held at
`skills/evolution-parallel-agent-eval/SKILL.md` Constraint: Effort floor. The Codex port was out of scope for that split
(Master agreement, 2026-09-14); #1973 moved brake 1 effort and role delivery
to the spawn call and prompt, and #2176 deleted its `brake-evaluator.toml`.

Why a test rather than reading attention: Claude resolves thinking effort in
the definition while Codex resolves it per launch. Losing the Claude pin or
reintroducing a Codex definition file is silent — the spawn still succeeds at
a different effort. The `model` and `tools` absences are the same shape in the other direction: a
`model` key here would take over the per-call sonnet floor, and a `tools` key
would express the no-write requirement as a permission, which
`skills/evolution-parallel-agent-eval/SKILL.md` Non-scope rejects. On the
Claude side, a role fragment written into `low.md` would silently duplicate
the role literal now canonical in the eval skill, and would also steer every
other low-effort spawn that is not a brake evaluator at all.

The sentinel region's structural invariants are not re-asserted here;
`tests/test_agent_sentinel_contract.py` already runs them over every source
under `adapter/claude/agents/`, this file included.
"""

from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLAUDE_AGENT = ROOT / "adapter" / "claude" / "agents" / "low.md"
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

    def test_claude_agent_is_named_by_effort_not_role(self) -> None:
        # Deliberately not "brake-evaluator" any more: #1972 dropped per-role
        # Claude Code definitions; #2176 deleted the Codex role file.
        self.assertEqual(frontmatter(self.claude)["name"], "low")
        self.assertEqual(frontmatter(self.claude)["effort"], "low")
        self.assertFalse(CODEX_AGENT.exists())

    def test_thinking_effort_uses_each_hosts_supported_surface(self) -> None:
        # Asserted against the floor value held at
        # `skills/evolution-parallel-agent-eval/SKILL.md` Constraint: Effort
        # floor, which the Codex spawn passes per launch.
        self.assertEqual(frontmatter(self.claude)["effort"], "low")
        evaluation = EVAL_SKILL.read_text(encoding="utf-8")
        self.assertIn('explicitly pass `reasoning_effort="low"`', evaluation)

    def test_claude_definition_pins_no_model(self) -> None:
        # The sonnet-class floor stays an explicit spawn-call parameter
        # (`skills/evolution-parallel-agent-eval/SKILL.md` Constraint: Model
        # floor). A pin here takes that axis over silently.
        self.assertNotIn("model", frontmatter(self.claude))

    def test_claude_definition_restricts_no_tools(self) -> None:
        # The no-write requirement rests on a prompt literal, and the `tools:`
        # route is rejected outright (same skill, Non-scope).
        self.assertNotIn("tools", frontmatter(self.claude))

    def test_claude_definition_carries_no_role_fragment(self) -> None:
        # low.md is shared by every low-effort Claude Code spawn, not just the
        # judge-type evaluator. Evaluation content placed here would steer
        # every round any low-effort agent is spawned for, not only brake 1
        # rounds.
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
        self.assertIn("subagent_type: low", evaluation)
        self.assertNotIn("adapter/codex/agents/brake-evaluator.toml", evaluation)
        self.assertIn("On Codex, both kinds spawn with no agent definition file", evaluation)
        self.assertIn("Effort floor = `low`", evaluation)

    def test_the_probe_type_round_reaches_the_floor_through_the_parent(self) -> None:
        # Claude has no per-call effort argument, so its probe reaches the floor
        # through the parent. Codex passes the floor at the call instead.
        evaluation = EVAL_SKILL.read_text(encoding="utf-8")
        self.assertIn(
            "raise the parent session's effort to the floor before spawning one",
            evaluation,
        )
        self.assertIn(
            'On Codex, both kinds spawn with no agent definition file and explicitly pass `reasoning_effort="low"`',
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
        self.assertIn("adapter/claude/agents/low.md", spawn)
        self.assertIn("A judge-type brake 1 evaluator selects at or above `low`", spawn)
        self.assertIn("A brake evaluator's effort is at or above `low`", spawn)


if __name__ == "__main__":
    unittest.main()
