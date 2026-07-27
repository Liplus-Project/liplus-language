"""Behavioural coverage for the session-start language contract emission.

Target = the three `adapter/*/hooks/on-session-start.*` implementations
(claude bash / codex bash / codex PowerShell). Issue #1575.

The defect this pins: `Workspace_Language_Contract` is always in context, but
resolving its *values* was written as a procedure ("read the workspace-root
Li+config.md"), and that file is auto-loaded into no agent context. The
contract text was present while its values were not, so human-readable output
with no other language literal fell back to the model default — observed as
English self-review bodies on PR #1531 / #1533 in a `base=ja` workspace.

Each hook already extracts both values from the live config to run the
update-status axis-3 check, then discarded them. The fix emits what it holds.

What is pinned and what is not
------------------------------
The assertions read the two `KEY=value` lines out of the emission and the fact
that the block is present. The banner wording, the surrounding prose line and
the ordering against the other startup markers are adapter presentation and are
deliberately not matched — except that the block is located by the two key
names, which are the `Li+config.md` schema keys and therefore fixed elsewhere.

`unset` is matched literally: `docs/6.-Adapter.md` specifies that spelling for
an unresolved value, and the AI-side contract in `adapter/*/CLAUDE.md` keys its
"ask human" branch off it.
"""

from __future__ import annotations

import re
import unittest

from test_on_session_start_observation_surface import (
    ADAPTERS,
    Workspace,
    emitted_sections,
)


BASE_KEY = "LI_PLUS_BASE_LANGUAGE"
PROJ_KEY = "LI_PLUS_PROJECT_LANGUAGE"

# The value the adapters render for a key the config does not resolve.
UNSET = "unset"


def config_text(base: str | None, project: str | None) -> str:
    """A Li+config.md carrying only what a case needs to set."""
    lines = [
        "# Li+ Config",
        "",
        "LI_PLUS_REPO=https://github.com/Liplus-Project/liplus-language",
        "LI_PLUS_MODE=clone",
        "LI_PLUS_CHANNEL=tag",
    ]
    if base is not None:
        lines.append(f"{BASE_KEY}={base}")
    if project is not None:
        lines.append(f"{PROJ_KEY}={project}")
    return "\n".join(lines) + "\n"


def language_values(hook_output: str) -> dict[str, str]:
    """The language contract values carried by the emission.

    Located by key name rather than by banner: the banner is an adapter choice,
    the keys are the config schema. Both keys must appear as standalone
    `KEY=value` lines in one section, which is what separates this block from
    the update-status marker — that marker reports the same axis, but as an
    abbreviated `language-contract-unresolved(base=...,project=...)` fragment
    inside one reason line, so it cannot satisfy the match.
    """
    for _banner, body in emitted_sections(hook_output):
        found: dict[str, str] = {}
        for line in body.replace("\r\n", "\n").split("\n"):
            match = re.fullmatch(rf"({BASE_KEY}|{PROJ_KEY})=(.*)", line.strip())
            if match:
                found[match.group(1)] = match.group(2).strip()
        if BASE_KEY in found and PROJ_KEY in found:
            return found
    return {}


class LanguageContractEmissionTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.ws = Workspace()
        self.addCleanup(self.ws.cleanup)

    def write_config(self, base: str | None, project: str | None) -> None:
        self.ws.write(self.ws.workspace, "Li+config.md", config_text(base, project))

    def run_hook(self, adapter: str, matcher: str = "startup") -> str:
        # codex_sh and codex_ps1 share one diff-only state path, so a previous
        # adapter's run would otherwise make this one look like a second run.
        self.ws.clear_state()
        return self.ws.run(adapter, matcher=matcher)

    def test_resolved_values_reach_the_session_context(self) -> None:
        """The two keys are carried independently, not collapsed into one."""
        # Deliberately different so a port that emits one value twice fails.
        self.write_config("ja", "en")
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                values = language_values(self.run_hook(adapter))
                self.assertEqual(
                    values,
                    {BASE_KEY: "ja", PROJ_KEY: "en"},
                    "the contract cannot fire on values the agent never receives",
                )

    def test_unresolved_values_still_emit_the_block(self) -> None:
        """Absence of a value must not become absence of the block.

        Otherwise the agent has to tell "the hook did not run" apart from "the
        config does not set it", and the ask-human branch loses its trigger.
        """
        self.write_config(None, None)
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                values = language_values(self.run_hook(adapter))
                self.assertEqual(values, {BASE_KEY: UNSET, PROJ_KEY: UNSET})

    def test_partially_resolved_config_keeps_the_resolved_half(self) -> None:
        self.write_config("ja", None)
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                values = language_values(self.run_hook(adapter))
                self.assertEqual(values, {BASE_KEY: "ja", PROJ_KEY: UNSET})

    def test_key_spelling_is_case_sensitive_on_every_adapter(self) -> None:
        """One config must not resolve differently per host adapter.

        `Select-String` defaults to case-insensitive while the bash ports' `sed`
        is case-sensitive, so a lowercase key spelling used to resolve on the
        PowerShell port alone.
        """
        self.ws.write(
            self.ws.workspace,
            "Li+config.md",
            config_text("ja", "en").replace(BASE_KEY, BASE_KEY.lower()),
        )
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                values = language_values(self.run_hook(adapter))
                self.assertEqual(values, {BASE_KEY: UNSET, PROJ_KEY: "en"})

    def test_pre_bootstrap_session_emits_no_block(self) -> None:
        """Before the clone is resolved the hooks exit ahead of the emission.

        Pinned because the adapter contract text carries a branch for exactly
        this state (banner absent -> ask human, same as `unset`); if a later
        change started emitting here, that branch would become unreachable
        prose while the values it promises are still not resolvable.
        """
        self.write_config("ja", "en")
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                workspace = Workspace()
                self.addCleanup(workspace.cleanup)
                workspace.write(workspace.workspace, "Li+config.md", config_text("ja", "en"))
                workspace.liplus.rmdir()  # unresolved Li+ source
                self.assertEqual(language_values(workspace.run(adapter)), {})

    def test_every_session_entry_point_carries_the_values(self) -> None:
        """resume / clear / compact need the values as much as startup does.

        The codex ports gate the update-status verification on the startup
        matcher; the language values are resolved outside that gate precisely
        so this case does not split the three adapters.
        """
        self.write_config("ja", "en")
        for adapter in ADAPTERS:
            for matcher in ("resume", "clear", "compact"):
                with self.subTest(adapter=adapter, matcher=matcher):
                    values = language_values(self.run_hook(adapter, matcher))
                    self.assertEqual(values, {BASE_KEY: "ja", PROJ_KEY: "en"})


if __name__ == "__main__":
    unittest.main()
