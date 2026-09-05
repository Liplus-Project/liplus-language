"""Behavioural coverage for Li+config.md value interpretation across the ports.

Target = the six `adapter/*/hooks/on-{session-start,user-prompt}.*`
implementations (claude bash / codex bash / codex PowerShell, two hooks each).
Issue #1804.

The defect this pins: PowerShell's comparison operators and `switch` are
case-insensitive by default while `[ x != y ]` and `case` in the two bash ports
are not, so one `Li+config.md` produced two different behaviours depending on
which host adapter read it.

  `LI_PLUS_WEBHOOK_DELIVERY=Mcp_Hook` — the bash ports emitted the call half of
  the webhook re-arm and the PowerShell port suppressed it, so the same
  workspace either double-delivered or did not deliver at all.

  `LI_PLUS_CHANNEL=Latest` — the bash ports matched no `case` branch and left
  the target tag unresolved (`needed`), while the PowerShell `switch` matched
  `latest`, resolved a tag, and could emit `unnecessary`. The two ports fall
  opposite ways, and the PowerShell one falls to the unsafe side.

A second axis: key-name matching. `Select-String` in
`adapter/codex/hooks/on-user-prompt.ps1` carried no `-CaseSensitive`, so a
`li_plus_webhook_delivery=` spelling resolved on that one port alone — an
inconsistency inside the PowerShell pair as well as across the three ports.

The chosen repair is case-sensitivity plus naming (issue #1804 制約, 方向2 +
方向3): every port compares case-sensitively, and a non-empty value outside the
known set is surfaced with its key and its literal value. Normalisation was
rejected because it would pass `Mcp_Hook` while `mcp-hook` still fell silently
to the default; naming the value closes the whole silent-fallback class.

What is pinned and what is not
------------------------------
The assertions read the judgment out of the emission: which value was taken as
the mode, whether the target tag resolved, and whether an unrecognized value was
named. The banner is located by topic, and the sentence around the named value
is not matched — only that the key name and the literal value both reach the
agent. Strict cross-port equality is asserted separately, because a containment
assertion passes on any superset and would not report one port drifting from
the other two.
"""

from __future__ import annotations

import os
import re
import unittest

from test_on_session_start_observation_surface import (
    ADAPTERS,
    Workspace,
    emitted_sections,
)
from test_on_user_prompt_webhook_rearm import (
    CALL_TOKEN,
    Fixture as PromptFixture,
    webhook_section,
)


DELIVERY_KEY = "LI_PLUS_WEBHOOK_DELIVERY"
CHANNEL_KEY = "LI_PLUS_CHANNEL"

# The known value sets. Spelled here rather than derived: "which values are
# known" is the judgment under test, and `docs/B.-Configuration.md` is where it
# is specified.
DELIVERY_KNOWN = ("poll", "channel", "mcp_hook")
CHANNEL_KNOWN = ("latest", "release", "tag")

# Values outside those sets. The mixed-case spellings are the ones that split
# the ports; the last of each is the typo normalisation would not have caught,
# and it is why 方向3 is not redundant with 方向2.
DELIVERY_UNKNOWN = ("Mcp_Hook", "CHANNEL", "mcp-hook")
CHANNEL_UNKNOWN = ("Latest", "Release", "lattest")

# What the two `gh` sub-commands the channel branches call return in the stub,
# so a resolved target tag reports *which* branch resolved it.
TAG_VIEW = "TAGFROMVIEW"
TAG_LIST = "TAGFROMLIST"


def unrecognized_section(hook_output: str) -> str | None:
    """Body of the unrecognized-value section, or None when the hook was silent.

    Located by topic rather than by exact banner text, for the reason the
    session-start suite gives: the banner is an adapter choice.
    """
    for banner, body in emitted_sections(hook_output):
        if "unrecognized" in banner.lower():
            return body
    return None


def update_status_line(hook_output: str) -> str | None:
    """The `LI_PLUS_UPDATE_STATUS=...` marker line, or None when absent."""
    for _banner, body in emitted_sections(hook_output):
        for line in body.replace("\r\n", "\n").split("\n"):
            if line.strip().startswith("LI_PLUS_UPDATE_STATUS="):
                return line.strip()
    return None


def resolved_target_tag(hook_output: str) -> str | None:
    """The target tag the sentinel axis resolved, read off the marker.

    The fixture plants no adapter file, so axis 1 always contributes a reason
    and the marker is always `needed` — which is what makes `target=`
    observable at all. `unknown` is the hooks' own rendering of an unresolved
    tag and is returned as None, so a test can say "nothing resolved" directly.
    """
    line = update_status_line(hook_output)
    if line is None:
        return None
    match = re.search(r"target=([^,)]*)", line)
    if not match:
        return None
    value = match.group(1).strip()
    return None if value == "unknown" else value


class ChannelWorkspace(Workspace):
    """A session-start fixture whose `gh` stub reports which branch called it.

    The inherited stub exits silently, which leaves the target tag unresolved
    under every channel value and so cannot tell a matched branch from an
    unmatched one — the whole judgment under test here.
    """

    def _write_gh_stub(self) -> None:
        unix_stub = self.stub_bin / "gh"
        unix_stub.write_text(
            "#!/bin/sh\n"
            'case "$2" in\n'
            f"  view) echo {TAG_VIEW} ;;\n"
            f"  list) echo {TAG_LIST} ;;\n"
            "esac\n"
            "exit 0\n",
            encoding="utf-8",
        )
        os.chmod(unix_stub, 0o755)
        (self.stub_bin / "gh.cmd").write_text(
            "@echo off\r\n"
            f'if "%2"=="view" echo {TAG_VIEW}\r\n'
            f'if "%2"=="list" echo {TAG_LIST}\r\n'
            "exit /b 0\r\n",
            encoding="ascii",
        )


def channel_config(value: str | None, key: str = CHANNEL_KEY) -> str:
    lines = [
        "# Li+ Config",
        "",
        "LI_PLUS_REPO=https://github.com/Liplus-Project/liplus-language",
        "LI_PLUS_MODE=clone",
        "LI_PLUS_BASE_LANGUAGE=ja",
        "LI_PLUS_PROJECT_LANGUAGE=ja",
    ]
    if value is not None:
        lines.append(f"{key}={value}")
    return "\n".join(lines) + "\n"


class ChannelTestCase(unittest.TestCase):
    """`LI_PLUS_CHANNEL` — the value the `case` / `switch` branches on."""

    def run_with(self, adapter: str, value: str | None, key: str = CHANNEL_KEY) -> str:
        ws = ChannelWorkspace()
        self.addCleanup(ws.cleanup)
        ws.write(ws.workspace, "Li+config.md", channel_config(value, key))
        return ws.run(adapter)

    def test_known_values_route_to_their_own_branch_on_every_port(self) -> None:
        """The baseline the case-sensitivity cases are read against.

        Without it, a port that resolved nothing under any value would pass
        every assertion below by accident.
        """
        expected = {"latest": TAG_VIEW, "release": TAG_LIST}
        for adapter in ADAPTERS:
            for value, tag in expected.items():
                with self.subTest(adapter=adapter, channel=value):
                    output = self.run_with(adapter, value)
                    self.assertEqual(resolved_target_tag(output), tag)
                    self.assertIsNone(
                        unrecognized_section(output),
                        f"{adapter} flagged the documented value {value!r}",
                    )

    def test_mixed_case_value_resolves_nothing_on_every_port(self) -> None:
        """The #1804 split: `switch` matched `Latest`, `case` did not.

        Both directions of the split are failures, but they are not symmetric:
        the PowerShell port resolved a tag and could emit `unnecessary`, which
        skips the update walkthrough on a config no other host accepts.
        """
        for adapter in ADAPTERS:
            for value in CHANNEL_UNKNOWN:
                with self.subTest(adapter=adapter, channel=value):
                    self.assertIsNone(
                        resolved_target_tag(self.run_with(adapter, value)),
                        f"{adapter} matched {value!r} to a channel branch; the "
                        "value set is case-sensitive on every port",
                    )

    def test_unknown_value_is_named_on_every_port(self) -> None:
        """方向3: the fallback stays, the silence does not."""
        for adapter in ADAPTERS:
            for value in CHANNEL_UNKNOWN:
                with self.subTest(adapter=adapter, channel=value):
                    section = unrecognized_section(self.run_with(adapter, value))
                    self.assertIsNotNone(
                        section,
                        f"{adapter} fell to the default silently under {value!r}",
                    )
                    self.assertIn(CHANNEL_KEY, section)
                    self.assertIn(
                        value,
                        section,
                        "the literal value is what tells the human which "
                        "spelling to correct",
                    )

    def test_documented_and_absent_values_stay_silent(self) -> None:
        """An unset key is the documented default, not a mistake to report."""
        for adapter in ADAPTERS:
            for value in CHANNEL_KNOWN + (None,):
                with self.subTest(adapter=adapter, channel=value):
                    self.assertIsNone(
                        unrecognized_section(self.run_with(adapter, value)),
                        f"{adapter} raised a warning for {value!r}",
                    )

    def test_key_spelling_is_case_sensitive_on_every_port(self) -> None:
        """A lowercase key name resolves on no port, so it defaults to release.

        Reported through the branch that ran rather than through silence: the
        `release` default is what a key nothing matched falls to.
        """
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                output = self.run_with(adapter, "latest", key=CHANNEL_KEY.lower())
                self.assertEqual(resolved_target_tag(output), TAG_LIST)
                self.assertIsNone(unrecognized_section(output))

    def test_every_port_names_it_the_same_way(self) -> None:
        """Strict equality; a containment assertion passes on any superset."""
        for value in CHANNEL_UNKNOWN:
            sections = {
                adapter: unrecognized_section(self.run_with(adapter, value))
                for adapter in ADAPTERS
            }
            reference = sections["claude_sh"]
            for adapter, section in sections.items():
                with self.subTest(channel=value, adapter=adapter):
                    self.assertEqual(section, reference)


class DeliveryTestCase(unittest.TestCase):
    """`LI_PLUS_WEBHOOK_DELIVERY` — the value the per-turn hooks compare."""

    def run_with(self, adapter: str, value: str) -> str:
        fixture = PromptFixture(value)
        self.addCleanup(fixture.cleanup)
        return fixture.run(adapter)

    def test_mixed_case_value_does_not_suppress_the_call_half(self) -> None:
        """`Mcp_Hook` is not a mode; every port must fall back to poll.

        The PowerShell port used to read it as `mcp_hook` and suppress the call
        half while the bash ports emitted it — one config, two behaviours.
        """
        for adapter in ADAPTERS:
            for value in DELIVERY_UNKNOWN:
                with self.subTest(adapter=adapter, delivery=value):
                    self.assertIn(
                        CALL_TOKEN,
                        webhook_section(self.run_with(adapter, value)),
                        f"{adapter} treated {value!r} as a delivery mode and "
                        "suppressed the call half; nothing replaces it",
                    )

    def test_unknown_value_is_named_on_every_port(self) -> None:
        for adapter in ADAPTERS:
            for value in DELIVERY_UNKNOWN:
                with self.subTest(adapter=adapter, delivery=value):
                    section = unrecognized_section(self.run_with(adapter, value))
                    self.assertIsNotNone(
                        section,
                        f"{adapter} fell back to poll silently under {value!r}",
                    )
                    self.assertIn(DELIVERY_KEY, section)
                    self.assertIn(value, section)

    def test_documented_values_stay_silent(self) -> None:
        for adapter in ADAPTERS:
            for value in DELIVERY_KNOWN:
                with self.subTest(adapter=adapter, delivery=value):
                    self.assertIsNone(
                        unrecognized_section(self.run_with(adapter, value)),
                        f"{adapter} raised a warning for {value!r}",
                    )

    def test_key_spelling_is_case_sensitive_on_every_port(self) -> None:
        """`Select-String` without `-CaseSensitive` split the PowerShell pair.

        A lowercase key name must resolve nowhere: the value is then unset, the
        call half is emitted, and no warning is raised (unset is the documented
        default, not an unknown value).
        """
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                fixture = PromptFixture("mcp_hook")
                self.addCleanup(fixture.cleanup)
                config = fixture.workspace / "Li+config.md"
                config.write_text(
                    config.read_text(encoding="utf-8").replace(
                        DELIVERY_KEY, DELIVERY_KEY.lower()
                    ),
                    encoding="utf-8",
                )
                output = fixture.run(adapter)
                self.assertIn(CALL_TOKEN, webhook_section(output))
                self.assertIsNone(unrecognized_section(output))

    def test_every_port_names_it_the_same_way(self) -> None:
        for value in DELIVERY_UNKNOWN:
            sections = {
                adapter: unrecognized_section(self.run_with(adapter, value))
                for adapter in ADAPTERS
            }
            reference = sections["claude_sh"]
            for adapter, section in sections.items():
                with self.subTest(delivery=value, adapter=adapter):
                    self.assertEqual(section, reference)


if __name__ == "__main__":
    unittest.main()
