"""Behavioural coverage for the update-status emission time line.

Target = `adapter/claude/hooks/on-session-start.sh`. Issue #2189.

The line and the reason it exists are fixed in `docs/6.-Adapter.md`
(on-session-start.sh, Li+ update status) and `adapter/claude/hooks-settings.md`.
The codex ports are out of this file's scope; the same docs place the line on
the claude port only.

What is pinned
--------------
- the update-status banner carries `Emitted at <UTC time> (UTC).` under the
  matchers startup / resume / clear / compact / fork, with the status both
  `needed` and `unnecessary`;
- the time is the run's own: it falls inside the wall-clock window around the
  run, so a constant or stale value fails;
- two `resume` runs a second apart, on an unchanged workspace, do not produce
  byte-identical output, and differ in the stamp line only. Byte identity is
  what the docs above name as the host's duplicate criterion.
"""

from __future__ import annotations

import re
import time
import unittest
from datetime import datetime, timezone

from test_on_session_start_observation_surface import emitted_sections
from test_update_status_rearm import (
    ADAPTER_TAG,
    SENTINEL_RELATIVE,
    TARGET_TAG,
    ReleaseTagWorkspace,
    plant,
    sentinel_text,
    update_status_section,
)


ADAPTER = "claude_sh"
MATCHERS = ("startup", "resume", "clear", "compact", "fork")
STAMP_RE = re.compile(r"^Emitted at (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z) \(UTC\)\.$", re.M)


def now_utc() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def stamp_of(hook_output: str) -> datetime | None:
    section = update_status_section(hook_output)
    if section is None:
        return None
    match = STAMP_RE.search(section)
    if match is None:
        return None
    return datetime.strptime(match.group(1), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


class EmissionTimeLineTest(unittest.TestCase):
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

    def set_sentinel(self, tag: str) -> None:
        plant(self.ws.workspace, SENTINEL_RELATIVE[ADAPTER], sentinel_text(tag))

    def test_stamp_is_the_run_time_on_every_matcher_and_status(self) -> None:
        for status, sentinel in (("needed", ADAPTER_TAG), ("unnecessary", TARGET_TAG)):
            self.set_sentinel(sentinel)
            for matcher in MATCHERS:
                with self.subTest(status=status, matcher=matcher):
                    before = now_utc()
                    output = self.ws.run(ADAPTER, matcher)
                    after = now_utc()
                    section = update_status_section(output) or ""
                    self.assertIn(f"LI_PLUS_UPDATE_STATUS={status}", section)
                    stamp = stamp_of(output)
                    self.assertIsNotNone(stamp, section)
                    self.assertLessEqual(before, stamp)
                    self.assertLessEqual(stamp, after)

    def test_repeated_resume_output_is_not_byte_identical(self) -> None:
        self.set_sentinel(TARGET_TAG)
        first = self.ws.run(ADAPTER, "resume")
        # Cross the next whole-second boundary; the stamp has one-second resolution.
        time.sleep(1.05 - (time.time() % 1.0))
        second = self.ws.run(ADAPTER, "resume")
        self.assertIn("LI_PLUS_UPDATE_STATUS=unnecessary", update_status_section(second) or "")
        self.assertNotEqual(first, second)
        # Only the stamp line separates the two: the rest of the emission is unchanged.
        self.assertEqual(STAMP_RE.sub("", first), STAMP_RE.sub("", second))
        self.assertEqual(
            [banner for banner, _ in emitted_sections(first)],
            [banner for banner, _ in emitted_sections(second)],
        )


if __name__ == "__main__":
    unittest.main()
