"""Contract tests for the Li+ implementation delegate's agent definition.

Scope = `adapter/claude/agents/high.md`, `adapter/codex/agents/implementer.toml`,
the role literal that carries the Claude Code role, and the spawn-policy
literal that routes delegations to both.

Reorganized at #1972: `adapter/claude/agents/` was split by role
(`implementer.md` / `brake-evaluator.md` / `dialogue-evaluator.md`) up to that
issue; from it on the Claude Code source is three files named by effort
(`low.md` / `medium.md` / `high.md`), none of which carries a role. The
implementation delegate now spawns as `subagent_type: high` with its role
literal injected into the prompt by `skills/task-subagent-prompt/SKILL.md`
instead of arriving through a role-named definition file's body. The Codex
port is out of scope for that split (Master agreement, 2026-09-14): its role
definition remains, while #1973 moves its effort resolution to the spawn call.

Why a test rather than reading attention: Claude pins thinking effort in the
definition while Codex resolves it per launch. Either losing the Claude field or
reintroducing the Codex override is silent — the spawn still succeeds at a
different effort. The `model` absence is the same shape in the other direction:
adding a `model` pin here would silently take over the tier inheritance that
`skills/task-subagent-spawn/SKILL.md` keeps at the spawn call. On the Claude
side, a role fragment written into `high.md` would silently
duplicate the role literal now canonical in `skills/task-subagent-prompt/SKILL.md`
— the two-copies failure `rules/model/subtractive-structural-beauty.md` Core
principle (A) refuses a place for.

The sentinel region's structural invariants are not re-asserted here;
`tests/test_agent_sentinel_contract.py` already runs them over every source under
`adapter/*/agents/`, this pair included.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLAUDE_AGENT = ROOT / "adapter" / "claude" / "agents" / "high.md"
CODEX_AGENT = ROOT / "adapter" / "codex" / "agents" / "implementer.toml"
SPAWN_SKILL = ROOT / "skills" / "task-subagent-spawn" / "SKILL.md"
DELEGATION_SKILL = ROOT / "skills" / "task-subagent-delegation" / "SKILL.md"
PROMPT_SKILL = ROOT / "skills" / "task-subagent-prompt" / "SKILL.md"
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


def body(text: str) -> str:
    """The owned region's prose, sentinel lines excluded."""
    start = text.index("\n", text.index("Li+ BEGIN")) + 1
    return text[start : text.rindex("\n", 0, text.index("Li+ END"))]


class ImplementerAgentContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.claude = CLAUDE_AGENT.read_text(encoding="utf-8")
        self.codex = CODEX_AGENT.read_text(encoding="utf-8")

    def test_claude_agent_is_named_by_effort_not_role(self) -> None:
        # Deliberately not "implementer" any more: #1972 dropped per-role
        # Claude Code definitions. The Codex port keeps its own role name.
        self.assertEqual(frontmatter(self.claude)["name"], "high")
        self.assertIn('name = "implementer"', self.codex)

    def test_thinking_effort_uses_each_hosts_supported_surface(self) -> None:
        # Claude has no per-call effort argument; Codex does, and an agent-file
        # value would override the resolved per-launch value.
        self.assertEqual(frontmatter(self.claude)["effort"], "high")
        self.assertIsNone(
            re.search(r"^\s*model_reasoning_effort\s*=", self.codex, re.MULTILINE)
        )
        spawn = SPAWN_SKILL.read_text(encoding="utf-8")
        self.assertIn(
            'An implementation-delegate or dialogue-evaluator spawn passes `reasoning_effort="high"`',
            spawn,
        )

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

    def test_claude_definition_carries_no_role_fragment(self) -> None:
        # high.md is shared by every high-effort Claude Code spawn, not just
        # the implementation delegate. A role fragment here would duplicate
        # the role literal (Role literal: implementation delegate, below) on a
        # surface every other high-effort role also reads.
        prose = body(self.claude)
        self.assertIn("no role, no procedure", prose)
        self.assertIn("arrive in the prompt", prose)
        for role_word in ("implementation delegate", "issue's change", "stop condition"):
            with self.subTest(literal=role_word):
                self.assertNotIn(role_word, prose)

    def test_the_role_literal_lives_in_the_prompt_skill(self) -> None:
        # The one place the role now lives on Claude Code, per #1972 decision
        # point 4 (role conveyed by prompt, held in exactly one skill).
        prompt = PROMPT_SKILL.read_text(encoding="utf-8")
        self.assertIn("Role literal: implementation delegate", prompt)
        self.assertIn("You are the Li+ implementation delegate.", prompt)
        self.assertIn("Do not create, move, or remove worktrees.", prompt)
        self.assertIn("subagent_type: high", prompt)

    def test_spawn_policy_names_the_agent_for_delegations(self) -> None:
        spawn = SPAWN_SKILL.read_text(encoding="utf-8")
        self.assertIn("subagent_type: high", spawn)
        self.assertIn("adapter/claude/agents/high.md", spawn)
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

    def test_stale_installed_role_files_are_named_as_left_behind(self) -> None:
        # #1972 deleted implementer.md / brake-evaluator.md / dialogue-evaluator.md
        # from this repository. Li+update.md Phase 4c performs no stale removal,
        # so a workspace that installed them before this change keeps them on
        # disk; this asymmetry is named on the spawn-policy surface rather than
        # silently left for a reader to rediscover.
        spawn = SPAWN_SKILL.read_text(encoding="utf-8")
        self.assertIn("no stale removal", spawn)
        self.assertIn("implementer.md", spawn)


if __name__ == "__main__":
    unittest.main()
