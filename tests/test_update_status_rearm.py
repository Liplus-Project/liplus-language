"""Behavioural coverage for the per-turn Li+ update status re-emit.

Target = the session-start hooks that record the update status and the
per-turn hooks that re-emit it, across the three ports (claude bash / codex
bash / codex PowerShell). Issue #1987.

The defect this pins: `LI_PLUS_UPDATE_STATUS=needed` is step 2's firing
condition, and it was delivered once, at the session boundary. Sessions read it
and carried on with other work while the adapter sentinel tag lagged the target
tag. The repair records the status at session start and has the per-turn hook
re-emit the marker while the sentinel still lags.

What is pinned
--------------
- session start: `needed` writes the one-line state file carrying the target tag
  and the sentinel tag; `unnecessary` removes it.
- per turn: re-emitted while the recorded target is non-empty, the sentinel
  differs from it, and the sentinel still equals the one recorded beside it.
  Silent when the sentinel caught up, when it moved past the recorded target,
  when the recorded target is empty, and when the state file is absent.
- the re-emitted reason is the existing `sentinel-tag(...)` axis, not a new one.
- the three ports emit the same section.
"""

from __future__ import annotations

import os
import re
import unittest
from pathlib import Path

from test_on_session_start_observation_surface import (
    ADAPTERS,
    Workspace,
    emitted_sections,
)
from test_on_user_prompt_webhook_rearm import Fixture


ADAPTER_TAG = "build-2026-09-24.12"
TARGET_TAG = "build-2026-09-25.4"
NEWER_TAG = "build-2026-09-26.1"

MARKER = "LI_PLUS_UPDATE_STATUS=needed"

STATE_RELATIVE = {
    "claude_sh": ".claude/state/update-status.txt",
    "codex_sh": ".codex/state/update-status.txt",
    "codex_ps1": ".codex/state/update-status.txt",
}

SENTINEL_RELATIVE = {
    "claude_sh": ".claude/CLAUDE.md",
    "codex_sh": "AGENTS.md",
    "codex_ps1": "AGENTS.md",
}


def sentinel_text(tag: str) -> str:
    return f"# --- Li+ BEGIN ({tag}) ---\n\nLayer = L6 Adapter Layer\n\n# --- Li+ END ---\n"


def state_line(target: str, adapter: str) -> str:
    return f"status=needed target={target} adapter={adapter}\n"


def update_status_section(hook_output: str) -> str | None:
    for banner, body in emitted_sections(hook_output):
        if "update status" in banner.lower():
            return body
    return None


def plant(workspace: Path, relative: str, text: str) -> None:
    target = workspace / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


class PromptHook(Fixture):
    """The per-turn hook runner of the webhook suite, bound to a given workspace."""

    def __init__(self, workspace: Path) -> None:  # noqa: D107 - no own root
        self.workspace = workspace

    def cleanup(self) -> None:
        pass


class ReleaseTagWorkspace(Workspace):
    """Session-start fixture whose `gh release ...` answers with TARGET_TAG."""

    def _write_gh_stub(self) -> None:
        unix_stub = self.stub_bin / "gh"
        unix_stub.write_text(
            f'#!/bin/sh\ncase "$1" in release) echo {TARGET_TAG} ;; esac\nexit 0\n',
            encoding="utf-8",
        )
        os.chmod(unix_stub, 0o755)
        (self.stub_bin / "gh.cmd").write_text(
            f'@echo off\r\nif "%1"=="release" echo {TARGET_TAG}\r\nexit /b 0\r\n',
            encoding="ascii",
        )


class PerTurnReemitTest(unittest.TestCase):
    """The per-turn hook, driven by a planted state file and sentinel."""

    def workspace(self) -> Path:
        fixture = Fixture("poll")
        self.addCleanup(fixture.cleanup)
        return fixture.workspace

    def emission(self, adapter: str, state: str | None, sentinel: str | None) -> str | None:
        ws = self.workspace()
        if state is not None:
            plant(ws, STATE_RELATIVE[adapter], state)
        if sentinel is not None:
            plant(ws, SENTINEL_RELATIVE[adapter], sentinel_text(sentinel))
        return update_status_section(PromptHook(ws).run(adapter))

    def test_lagging_sentinel_is_reemitted(self) -> None:
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                section = self.emission(adapter, state_line(TARGET_TAG, ADAPTER_TAG), ADAPTER_TAG)
                self.assertIsNotNone(section, f"{adapter} did not re-emit while the sentinel lags")
                self.assertIn(
                    f"{MARKER} reason=sentinel-tag(adapter={ADAPTER_TAG},target={TARGET_TAG})",
                    section,
                )

    def test_reason_is_the_existing_sentinel_axis_only(self) -> None:
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                section = self.emission(adapter, state_line(TARGET_TAG, ADAPTER_TAG), ADAPTER_TAG) or ""
                reasons = re.findall(r"LI_PLUS_UPDATE_STATUS=needed reason=(\S+)", section)
                self.assertEqual(len(reasons), 1, section)
                self.assertRegex(reasons[0], r"^sentinel-tag\(adapter=[^,]*,target=[^)]*\)$")

    def test_sentinel_caught_up_is_silent(self) -> None:
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                self.assertIsNone(
                    self.emission(adapter, state_line(TARGET_TAG, ADAPTER_TAG), TARGET_TAG)
                )

    def test_sentinel_moved_past_the_recorded_target_is_silent(self) -> None:
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                self.assertIsNone(
                    self.emission(adapter, state_line(TARGET_TAG, ADAPTER_TAG), NEWER_TAG)
                )

    def test_state_absent_is_silent(self) -> None:
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                self.assertIsNone(self.emission(adapter, None, ADAPTER_TAG))

    def test_unresolved_recorded_target_is_silent(self) -> None:
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                self.assertIsNone(self.emission(adapter, state_line("", ADAPTER_TAG), ADAPTER_TAG))

    def test_every_port_emits_the_same_section(self) -> None:
        sections = {
            adapter: self.emission(adapter, state_line(TARGET_TAG, ADAPTER_TAG), ADAPTER_TAG)
            for adapter in ADAPTERS
        }
        for adapter, section in sections.items():
            with self.subTest(adapter=adapter):
                self.assertEqual(section, sections["claude_sh"])


class SessionStartRecordTest(unittest.TestCase):
    """Session start writes the state on needed and removes it on unnecessary."""

    def setUp(self) -> None:
        self.ws = ReleaseTagWorkspace()
        self.addCleanup(self.ws.cleanup)
        self.ws.write(
            self.ws.workspace,
            "Li+config.md",
            "\n".join(
                [
                    "# Li+ Config",
                    "",
                    "LI_PLUS_REPO=https://github.com/Liplus-Project/liplus-language",
                    "LI_PLUS_MODE=clone",
                    "LI_PLUS_CHANNEL=release",
                    "LI_PLUS_BASE_LANGUAGE=ja",
                    "LI_PLUS_PROJECT_LANGUAGE=ja",
                ]
            )
            + "\n",
        )

    def run_session_start(self, adapter: str, sentinel: str) -> None:
        plant(self.ws.workspace, SENTINEL_RELATIVE[adapter], sentinel_text(sentinel))
        self.ws.clear_state()
        self.ws.run(adapter)

    def state_path(self, adapter: str) -> Path:
        return self.ws.workspace / STATE_RELATIVE[adapter]

    def test_needed_records_target_and_sentinel(self) -> None:
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                self.run_session_start(adapter, ADAPTER_TAG)
                path = self.state_path(adapter)
                self.assertTrue(path.is_file(), f"{adapter} recorded no state on needed")
                self.assertEqual(
                    path.read_bytes().decode("utf-8"), state_line(TARGET_TAG, ADAPTER_TAG)
                )
                path.unlink()

    def test_unnecessary_removes_the_state(self) -> None:
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                plant(self.ws.workspace, STATE_RELATIVE[adapter], state_line(TARGET_TAG, ADAPTER_TAG))
                self.run_session_start(adapter, TARGET_TAG)
                self.assertFalse(
                    self.state_path(adapter).exists(),
                    f"{adapter} left the state in place on unnecessary",
                )

    def test_recorded_state_drives_the_per_turn_hook(self) -> None:
        """End to end: session start records, the turn re-emits, the catch-up silences."""
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                self.run_session_start(adapter, ADAPTER_TAG)
                turn = PromptHook(self.ws.workspace)
                self.assertIsNotNone(update_status_section(turn.run(adapter)))
                plant(self.ws.workspace, SENTINEL_RELATIVE[adapter], sentinel_text(TARGET_TAG))
                self.assertIsNone(update_status_section(turn.run(adapter)))
                self.state_path(adapter).unlink()


if __name__ == "__main__":
    unittest.main()
