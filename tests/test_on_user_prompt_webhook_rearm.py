"""Behavioural coverage for the per-turn webhook re-arm.

Target = the three `adapter/*/hooks/on-user-prompt.*` implementations
(claude bash / codex bash / codex PowerShell). Issue #1798.

The defect this pins: the webhook block carries two separable things — a *call*
half telling the AI to run `get_pending_status` itself, and a *handling* half
saying what to do with whatever arrived. `LI_PLUS_WEBHOOK_DELIVERY=channel` and
`=mcp_hook` replace the call half only; nothing in either mode replaces the
handling half. The condition dropped the whole block, so under those two modes
events were delivered into context and no surface said what to do with them —
observed on 2026-08-24 with nine pending events injected at turn 1 and neither
inspect nor `mark_processed` running until a later step named the procedure.

The handling half cannot be left to its always-on canonical
(`rules/operations/main-agent-procedures.md` Foreground webhook notification
intake). That section fixes its own firing moment at `each user turn start`, and
always-on residency is a load guarantee, not a firing one; a per-turn hook is
the only surface that fires a turn boundary. Same reasoning, same file, as
`rules/model/trigger-check-gate.md` Trigger firing.

What is pinned and what is not
------------------------------
The assertions read the *obligations* out of the emission, not its wording. The
call half is located by the MCP tool name, which is fixed by the server; the
handling half by `mark_processed`, which `rules/operations/operations.md`
Operations Rules states as a mandatory word, and by the foreground filter's
subject. The banner text, the phrasing of each line and their order are adapter
presentation and are deliberately not matched.

The pointer is held to resolving both obligations, not merely to being present.
A re-arm that points instead of copying is only as good as what the pointer
reaches, and the two obligations it asserts have two homes — see CANONICAL_TOKENS.

The other failure direction is pinned too, and it is not symmetric noise: the
call half reaching a `channel` / `mcp_hook` workspace is the double delivery
that `LI_PLUS_WEBHOOK_DELIVERY` exists to prevent (#1632 F7), so a repair that
simply emits the block unconditionally must fail here.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from test_on_session_start_observation_surface import (
    ADAPTERS,
    BASH,
    PWSH,
    emitted_sections,
    posix_path,
    require_runtime,
    slash_path,
)


ROOT = Path(__file__).resolve().parents[1]

HOOKS = {
    "claude_sh": ROOT / "adapter" / "claude" / "hooks" / "on-user-prompt.sh",
    "codex_sh": ROOT / "adapter" / "codex" / "hooks" / "on-user-prompt.sh",
    "codex_ps1": ROOT / "adapter" / "codex" / "hooks" / "on-user-prompt.ps1",
}

HOOK_TIMEOUT = 120

DELIVERY_KEY = "LI_PLUS_WEBHOOK_DELIVERY"

# Modes that replace the call half. Both are spelled here rather than derived,
# because "which modes have a substitute" is the judgment under test.
REPLACING_MODES = ("channel", "mcp_hook")

# Config states that leave the AI as the caller. `None` = the key is absent from
# an otherwise present Li+config.md; `MISSING_CONFIG` = no config file at all.
# Both are the documented default (`docs/B.-Configuration.md`: 未設定 / poll).
MISSING_CONFIG = object()
CALLING_STATES = ("poll", None, MISSING_CONFIG)

# The MCP tool the call half names. Fixed by the server, not by the adapter.
CALL_TOKEN = "get_pending_status"

# The two handling obligations. `mark_processed` is stated as mandatory in
# `rules/operations/operations.md` Operations Rules; `foreground` is the subject
# of the report filter in `rules/operations/main-agent-procedures.md`.
CONSUME_TOKEN = "mark_processed"
FILTER_TOKEN = "foreground"

# Where each asserted obligation resolves. The re-arm points instead of copying,
# the shape the Trigger Check Gate re-arm in the same file already uses — and a
# pointer earns that shape only by reaching what the re-arm claims. The two
# claims have two homes: the intake procedure and the report filter are in
# `main-agent-procedures.md` Foreground webhook notification intake, whose only
# `mark_processed` is scoped to own-operation events (`:493`), while the general
# "every consumed event" mandate is stated in `operations.md` Operations Rules
# (`:91`). Naming the first alone left the general half unreachable by a reader
# who followed the pointer — brake 1 finding 1 on PR #1802, 3/3.
CANONICAL_TOKENS = (
    "rules/operations/main-agent-procedures.md",
    "rules/operations/operations.md",
)

# A terse re-arm, not a transplanted procedure. The budget is deliberately loose
# — it catches the canonical being copied into the hook, not a line added.
MAX_REARM_LINES = 6


def state_name(state: object) -> str:
    if state is MISSING_CONFIG:
        return "<no Li+config.md>"
    if state is None:
        return "<key absent>"
    return str(state)


class Fixture:
    """A workspace root holding one `Li+config.md` state."""

    def __init__(self, state: object) -> None:
        self.root = Path(tempfile.mkdtemp(prefix="liplus-prompt-hook-"))
        self.workspace = self.root / "ws"
        self.workspace.mkdir(parents=True)
        if state is not MISSING_CONFIG:
            (self.workspace / "Li+config.md").write_text(
                self._config_text(state), encoding="utf-8"
            )

    @staticmethod
    def _config_text(mode: str | None) -> str:
        lines = [
            "# Li+ Config",
            "",
            "LI_PLUS_REPO=https://github.com/Liplus-Project/liplus-language",
            "LI_PLUS_MODE=clone",
        ]
        if mode is not None:
            lines.append(f"{DELIVERY_KEY}={mode}")
        return "\n".join(lines) + "\n"

    def cleanup(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)

    # -- hook execution -------------------------------------------------------

    def _env_for(self, adapter: str) -> dict[str, str]:
        env = dict(os.environ)
        env.pop("CLAUDE_PROJECT_DIR", None)
        env.pop("CODEX_PROJECT_DIR", None)
        if adapter == "claude_sh":
            env["CLAUDE_PROJECT_DIR"] = posix_path(self.workspace)
        elif adapter == "codex_sh":
            # The payload `cwd` is the production path and is set below; this is
            # the hook's own documented fallback for a host without `jq`, and
            # both resolve to the same fixture. Root resolution is not the axis
            # under test here, so neither branch is allowed to decide the case.
            env["CODEX_PROJECT_DIR"] = posix_path(self.workspace)
        else:
            env["CODEX_PROJECT_DIR"] = slash_path(self.workspace)
        return env

    def _command_and_stdin(self, adapter: str) -> tuple[list[str], str]:
        hook = HOOKS[adapter]
        payload = {
            "session_id": "test-session",
            "hook_event_name": "UserPromptSubmit",
            "prompt": "test prompt",
        }
        if adapter == "codex_ps1":
            payload["cwd"] = slash_path(self.workspace)
            command = [PWSH, "-NoProfile", "-NonInteractive", "-File", str(hook)]
        else:
            payload["cwd"] = posix_path(self.workspace)
            command = [BASH, posix_path(hook)]
        return command, json.dumps(payload)

    def run(self, adapter: str) -> str:
        """Run one hook and return the context text it injects."""
        if adapter in ("claude_sh", "codex_sh") and not BASH:
            require_runtime("bash", "claude / codex shell hooks")
        if adapter == "codex_ps1" and not PWSH:
            require_runtime("pwsh", "codex PowerShell hook")

        command, stdin_payload = self._command_and_stdin(adapter)
        completed = subprocess.run(
            command,
            input=stdin_payload.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=self._env_for(adapter),
            timeout=HOOK_TIMEOUT,
        )
        stdout = completed.stdout.decode("utf-8", errors="replace")
        if adapter == "claude_sh":
            # Claude accepts plain text on UserPromptSubmit stdout.
            return stdout
        try:
            envelope = json.loads(stdout)
        except json.JSONDecodeError as error:
            raise AssertionError(
                f"{adapter} did not emit JSON: {error}\nstdout={stdout!r}\n"
                f"stderr={completed.stderr.decode('utf-8', errors='replace')!r}"
            ) from error
        return envelope["hookSpecificOutput"]["additionalContext"]


def webhook_section(hook_output: str) -> str | None:
    """Body of the webhook re-arm section, or None when it was not emitted.

    Located by topic rather than by exact banner text, for the reason the
    session-start suite gives: the banner is an adapter choice, and pinning it
    would make every assertion here depend on one string.
    """
    for banner, body in emitted_sections(hook_output):
        if "webhook" in banner.lower():
            return body
    return None


class WebhookRearmTestCase(unittest.TestCase):
    def section_for(self, adapter: str, state: object) -> str:
        fixture = Fixture(state)
        self.addCleanup(fixture.cleanup)
        output = fixture.run(adapter)
        section = webhook_section(output)
        if section is None:
            banners = [banner for banner, _body in emitted_sections(output)]
            self.fail(
                f"{adapter} emitted no webhook section for "
                f"{state_name(state)}; banners seen: {banners}"
            )
        return section


class HandlingHalfTest(WebhookRearmTestCase):
    """The half #1798 lost: it must survive every delivery mode."""

    def test_handling_half_is_emitted_in_every_delivery_mode(self) -> None:
        for adapter in ADAPTERS:
            for state in CALLING_STATES + REPLACING_MODES:
                with self.subTest(adapter=adapter, delivery=state_name(state)):
                    section = self.section_for(adapter, state)
                    self.assertIn(
                        FILTER_TOKEN,
                        section,
                        f"{adapter} dropped the report filter under "
                        f"{state_name(state)}",
                    )
                    self.assertIn(
                        CONSUME_TOKEN,
                        section,
                        f"{adapter} dropped the {CONSUME_TOKEN} re-arm under "
                        f"{state_name(state)}; omission accumulates backlog",
                    )

    def test_the_rearm_points_at_the_canonical_instead_of_copying_it(self) -> None:
        for adapter in ADAPTERS:
            for state in CALLING_STATES + REPLACING_MODES:
                with self.subTest(adapter=adapter, delivery=state_name(state)):
                    section = self.section_for(adapter, state)
                    for token in CANONICAL_TOKENS:
                        self.assertIn(
                            token,
                            section,
                            f"{adapter} carries no pointer to {token} under "
                            f"{state_name(state)}; the re-arm asserts an "
                            "obligation whose literal lives there",
                        )
                    lines = [line for line in section.split("\n") if line.strip()]
                    self.assertLessEqual(
                        len(lines),
                        MAX_REARM_LINES,
                        f"{adapter} emits {len(lines)} lines under "
                        f"{state_name(state)}; the hook carries a terse re-arm, "
                        "and the procedure body belongs to the canonical",
                    )


class CallHalfTest(WebhookRearmTestCase):
    """The half the delivery mode does select."""

    def test_call_half_is_emitted_where_the_ai_is_the_caller(self) -> None:
        for adapter in ADAPTERS:
            for state in CALLING_STATES:
                with self.subTest(adapter=adapter, delivery=state_name(state)):
                    self.assertIn(
                        CALL_TOKEN,
                        self.section_for(adapter, state),
                        f"{adapter} never tells the AI to call the tool under "
                        f"{state_name(state)}, and nothing else does either",
                    )

    def test_call_half_is_suppressed_where_something_replaces_it(self) -> None:
        for adapter in ADAPTERS:
            for mode in REPLACING_MODES:
                with self.subTest(adapter=adapter, delivery=mode):
                    self.assertNotIn(
                        CALL_TOKEN,
                        self.section_for(adapter, mode),
                        f"{adapter} still asks the AI to call the tool under "
                        f"{mode}; that is the double delivery the setting "
                        "exists to prevent",
                    )


class PortParityTest(WebhookRearmTestCase):
    """Strict equality across the three hand-written ports.

    Containment assertions pass on any superset, so they would not report a port
    that gained or kept a line the others do not have. This is the assertion that
    fails when one port is edited and the others are not.
    """

    def test_every_port_emits_the_same_section(self) -> None:
        for state in CALLING_STATES + REPLACING_MODES:
            sections = {
                adapter: self.section_for(adapter, state) for adapter in ADAPTERS
            }
            reference = sections["claude_sh"]
            for adapter, section in sections.items():
                with self.subTest(delivery=state_name(state), adapter=adapter):
                    self.assertEqual(
                        section,
                        reference,
                        f"{adapter} disagrees with claude_sh under "
                        f"{state_name(state)}",
                    )


if __name__ == "__main__":
    unittest.main()
