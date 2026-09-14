from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

CONTRACT_PATTERNS = {
    "adapter": {
        "explicit_effort_context_and_no_omission": (
            r"Every subagent spawn must set `reasoning_effort` and `fork_turns` "
            r"explicitly\. Omitting either is prohibited\."
        ),
        "non_brake_model_and_context": (
            r"Normal non-brake spawn: omit `model` so the parent model is inherited, "
            r'and set `fork_turns="none"`\.'
        ),
        "brake_model_context_and_prompt": (
            r"Brake evaluator spawn: set `model` explicitly under the existing "
            r'evaluator policy, set\s+`reasoning_effort="medium"` independently of that model floor, '
            r'set `fork_turns="none"`,\s+use no agent definition file, and pass all evaluation material '
            r"in a self-contained prompt\."
        ),
        "implementation_and_dialogue_high": (
            r'Implementation-delegate and dialogue-evaluator spawns set `reasoning_effort="high"`\.'
        ),
        "bounded_read_only_selects": (
            r'A bounded read-only investigation selects `reasoning_effort="low"`, '
            r'`"medium"`, or `"high"`\s+for its purpose\. It does not omit the argument '
            r"to inherit the parent value\."
        ),
        "supported_value_only": (
            r"Pass only a `reasoning_effort` value supported by the model selected for that spawn\. "
            r"Do not\s+guess a fallback when the model does not expose the requested value\."
        ),
        "bounded_decimal_string": (
            r"The only positive form allowed is a decimal string such as "
            r'`fork_turns="3"`, and only when the\s+bounded dialogue segment itself '
            r"is required as evaluation material\."
        ),
        "all_prohibited": (
            r'Full-history inheritance via `fork_turns="all"` is normally prohibited\.'
        ),
        "per_spawn_not_toml": (
            r"Keep these bindings at the spawn call\. Do not set `model_reasoning_effort` in\s+"
            r"`adapter/codex/agents/\*\.toml`: an agent-file value overrides the resolved per-launch value\."
        ),
        "preserved_contracts": (
            r"This host-specific binding does not change the L3 context-isolation semantics, "
            r"the independent `model`\s+policy, or the evaluator model floor / N / M / P / "
            r"self-contained-prompt contracts\."
        ),
    },
    "docs": {
        "explicit_effort_context_and_no_omission": (
            r"every subagent spawn の per-call 引数に `reasoning_effort` と `fork_turns` を必ず明示し、"
            r"どちらも省略して既定値に依存することを禁止する。"
        ),
        "non_brake_model_and_context": (
            r"通常の non-brake spawn は、`model` を省略して親モデルを継承し、"
            r'`fork_turns="none"` を指定する。'
        ),
        "brake_model_context_and_prompt": (
            r"brake evaluator spawn は既存 evaluator policy に従って "
            r'`model` を明示し、その床と独立して `reasoning_effort="medium"`、'
            r'`fork_turns="none"` を指定する。定義ファイルは選ばず、'
            r"評価材料を self-contained prompt で渡す。"
        ),
        "implementation_and_dialogue_high": (
            r'implementation delegate と dialogue evaluator は `reasoning_effort="high"` を指定する。'
        ),
        "bounded_read_only_selects": (
            r'bounded read-only investigation は目的に合わせて `reasoning_effort="low"` / '
            r'`"medium"` / `"high"` を選び、親 effort への暗黙継承は使わない。'
        ),
        "supported_value_only": (
            r"`reasoning_effort` はその spawn で選択された model が公開する列挙値だけを渡す。"
            r"未対応値に対する fallback を推測しない。"
        ),
        "bounded_decimal_string": (
            r"dialogue の限定区間そのものが評価材料として必要な場合に限り、"
            r'`fork_turns="3"` のような正の10進数字文字列を使用できる。'
        ),
        "all_prohibited": (
            r'`fork_turns="all"` による full-history inheritance は通常禁止する。'
        ),
        "per_spawn_not_toml": (
            r"これらの拘束は spawn call ごとに行う。"
            r"`adapter/codex/agents/\*\.toml` に `model_reasoning_effort` を固定しない"
        ),
        "preserved_contracts": (
            r"これは L3 の context-isolation semantic を Codex の host-specific 引数へ"
            r"結び付ける規定であり、L3 semantic 自体、独立した `model` policy、"
            r"evaluator の model floor / N / M / P / self-contained-prompt 契約は変更しない。"
        ),
    },
}


def contract_violations(text: str, surface: str) -> list[str]:
    return [
        name
        for name, pattern in CONTRACT_PATTERNS[surface].items()
        if re.search(pattern, text) is None
    ]


class CodexSubagentContextContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.adapter = (ROOT / "adapter" / "codex" / "AGENTS.md").read_text(encoding="utf-8")
        self.docs = (ROOT / "docs" / "6.-Adapter.md").read_text(encoding="utf-8")

    def test_adapter_and_docs_encode_the_complete_contract(self) -> None:
        for surface, text in (("adapter", self.adapter), ("docs", self.docs)):
            with self.subTest(surface=surface):
                self.assertEqual(contract_violations(text, surface), [])

    def test_agent_toml_files_do_not_fix_fork_turns(self) -> None:
        agents = sorted((ROOT / "adapter" / "codex" / "agents").glob("*.toml"))
        self.assertNotEqual(agents, [])
        for agent in agents:
            with self.subTest(agent=agent.name):
                self.assertNotIn("fork_turns", agent.read_text(encoding="utf-8"))

    def test_agent_toml_files_do_not_override_per_launch_effort(self) -> None:
        agents = sorted((ROOT / "adapter" / "codex" / "agents").glob("*.toml"))
        self.assertNotEqual(agents, [])
        for agent in agents:
            with self.subTest(agent=agent.name):
                self.assertIsNone(
                    re.search(
                        r"^\s*model_reasoning_effort\s*=",
                        agent.read_text(encoding="utf-8"),
                        re.MULTILINE,
                    )
                )

    def test_reversed_adapter_semantics_are_rejected(self) -> None:
        mutations = {
            "omission_allowed": ("Omitting either is prohibited.", "Omitting either is allowed."),
            "all_allowed": (
                'Full-history inheritance via `fork_turns="all"` is normally prohibited.',
                'Full-history inheritance via `fork_turns="all"` is normally allowed.',
            ),
            "non_brake_model_pinned": (
                "omit `model` so the parent model is inherited",
                "set `model` explicitly instead of inheriting the parent model",
            ),
            "non_brake_full_history": ('set `fork_turns="none"`', 'set `fork_turns="all"`'),
            "brake_model_omitted": (
                "set `model` explicitly under the existing evaluator policy",
                "omit `model` under the existing evaluator policy",
            ),
            "brake_effort_omitted": (
                'set\n    `reasoning_effort="medium"` independently of that model floor',
                "omit reasoning effort and inherit the parent",
            ),
            "brake_prompt_not_self_contained": (
                "pass all evaluation material in a self-contained prompt",
                "inherit evaluation material from the parent history",
            ),
            "bounded_value_not_a_decimal_string": (
                'a decimal string such as `fork_turns="3"`',
                "a numeric value such as `fork_turns=3`",
            ),
            "binding_moved_to_toml": (
                "Do not set `model_reasoning_effort` in\n    `adapter/codex/agents/*.toml`",
                "Set `model_reasoning_effort` in\n    `adapter/codex/agents/*.toml`",
            ),
            "context_isolation_changed": (
                "does not change the L3 context-isolation semantics",
                "changes the L3 context-isolation semantics",
            ),
            "model_policy_changed": (
                "the independent `model`\n  policy",
                "a replacement `model`\n  policy",
            ),
            "evaluator_floor_changed": (
                "the evaluator model floor / N / M / P / self-contained-prompt contracts",
                "the evaluator model ceiling / N / M / P / self-contained-prompt contracts",
            ),
            "evaluator_dimensions_changed": (
                "the evaluator model floor / N / M / P / self-contained-prompt contracts",
                "the evaluator model floor / self-contained-prompt contracts",
            ),
        }
        for name, (original, replacement) in mutations.items():
            with self.subTest(name=name):
                mutated = self.adapter.replace(original, replacement, 1)
                self.assertNotEqual(mutated, self.adapter)
                self.assertNotEqual(contract_violations(mutated, "adapter"), [])


if __name__ == "__main__":
    unittest.main()
