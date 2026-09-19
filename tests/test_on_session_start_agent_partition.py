"""Behavioural coverage for the cold-start multi-session state partition.

Target = the three `adapter/*/hooks/on-session-start.*` implementations
(claude bash / codex bash / codex PowerShell). Issue #1811.

The defect this covers is not starvation (a state file missing entirely) but
*distribution*: two sessions sharing one working directory each ran the
diff-only comparison against one shared "last emitted" pointer, so whichever
session ran first silently consumed the pending diff for a section, and the
second session's own run then read that section as already-seen — even
though the second session never itself saw it. Neither session's own context
shows the gap; it only appears when both sessions' output is compared side
by side, which is exactly what this file does with two calls to `run(...)`
against one fixture, one per `LI_PLUS_AGENT_KEY`.

The fix partitions the persisted state by `LI_PLUS_AGENT_KEY` (env var,
default `"default"`). Unset reproduces the pre-#1811 single-partition
behavior exactly — that is `test_unset_key_behaves_as_a_single_shared_default_partition`
below, the backward-compatibility guard for the overwhelmingly common
single-session workspace.

What is pinned and what is not
------------------------------
The contract (`rules/evolution/cold-start-synthesis.md` Hook Emission
Contract, Multi-session partition) fixes the partition key's env var name and
default, the fail-safe reasons a first-use-of-this-key and a legacy-schema
state file collapse to, and that a sibling partition survives a write it did
not participate in. It does not fix section banner text or ordering, so the
assertions here locate sections by topic (via `emitted_sections` /
`self_eval_section`, reused from `test_on_session_start_observation_surface`)
rather than matching presentation.

The fixture and hook runner are reused from that module for the reason it
states: a second copy of the harness would be the copy that drifts.
"""

from __future__ import annotations

import json
import unittest

from test_on_session_start_observation_surface import (
    ADAPTERS,
    FAIL_SAFE_MARK,
    NO_NEW_MATERIAL,
    Workspace,
    emitted_sections,
)


def self_eval_section(hook_output: str) -> str | None:
    """Body of the self-evaluation head section, or None when absent.

    Reimplemented rather than imported: the observation-surface module's copy
    is private to that file's own naming, and this file changes exactly one
    thing about the fixture (`self-evaluation_log.md` content) to move exactly
    one diffed section, so locating by the same topic keyword is what proves
    the move landed.
    """
    for banner, body in emitted_sections(hook_output):
        if "self-evaluation" in banner.lower():
            return body
    return None


def no_new_material_marker(hook_output: str) -> str | None:
    for _banner, body in emitted_sections(hook_output):
        lines = [line for line in body.split("\n") if line.strip()]
        if len(lines) == 1 and NO_NEW_MATERIAL in lines[0]:
            return lines[0]
    return None


class AgentPartitionTest(unittest.TestCase):
    def fixture(self) -> Workspace:
        ws = Workspace()
        self.addCleanup(ws.cleanup)
        ws.seed_coldstart_rule("anchor-token")
        ws.write(ws.shared_memory, "self-evaluation_log.md", "# log\n\n## first entry\n")
        return ws

    def move_the_diffed_section(self, ws: Workspace) -> None:
        """Change the one section every case here tracks across two runs."""
        ws.write(ws.shared_memory, "self-evaluation_log.md", "# log\n\n## second entry\n")

    # -- backward compatibility: the common, single-session workspace --------

    def test_unset_key_behaves_as_a_single_shared_default_partition(self) -> None:
        # No LI_PLUS_AGENT_KEY anywhere in this test: reproduces the exact
        # pre-#1811 two-run shape (seed = full emit, repeat = no-new-material).
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                ws = self.fixture()
                seed = ws.run(adapter)
                self.assertIn(FAIL_SAFE_MARK, seed)
                repeat = ws.run(adapter)  # nothing changed
                self.assertNotIn(FAIL_SAFE_MARK, repeat)
                self.assertIsNotNone(
                    no_new_material_marker(repeat),
                    f"{adapter}: unset LI_PLUS_AGENT_KEY regressed the "
                    "single-session no-new-material path",
                )

    # -- the #1811 defect, fixed --------------------------------------------

    def test_two_agent_keys_each_get_their_own_first_full_emit(self) -> None:
        # Neither key has ever been recorded, so both are a first use — not
        # one full emit followed by the other reading the first one's write
        # as its own prior state.
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                ws = self.fixture()
                lay = ws.run(adapter, extra_env={"LI_PLUS_AGENT_KEY": "lay"})
                lin = ws.run(adapter, extra_env={"LI_PLUS_AGENT_KEY": "lin"})
                self.assertIn(FAIL_SAFE_MARK, lay)
                self.assertIn(FAIL_SAFE_MARK, lin)

    def test_second_key_still_observes_a_change_the_first_key_already_read(self) -> None:
        # The worked distribution example from issue #1811: both sessions
        # establish a baseline, one section changes once, and BOTH sessions'
        # own next run must show it — not "whichever session happens to run
        # the diff first consumes it for the other."
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                ws = self.fixture()
                ws.run(adapter, extra_env={"LI_PLUS_AGENT_KEY": "lay"})
                ws.run(adapter, extra_env={"LI_PLUS_AGENT_KEY": "lin"})
                self.move_the_diffed_section(ws)

                lay_after = ws.run(adapter, extra_env={"LI_PLUS_AGENT_KEY": "lay"})
                self.assertIsNotNone(
                    self_eval_section(lay_after),
                    f"{adapter}: lay's own baseline did not show a change lay "
                    "never previously saw",
                )

                lin_after = ws.run(adapter, extra_env={"LI_PLUS_AGENT_KEY": "lin"})
                self.assertIsNotNone(
                    self_eval_section(lin_after),
                    f"{adapter}: lin was starved of a change lay already read — "
                    "this is the #1811 distribution defect reappearing",
                )

    def test_sibling_partition_survives_a_write_it_did_not_participate_in(self) -> None:
        # The read-merge-write in the fix: writing "lin"'s partition must not
        # erase "lay"'s already-recorded entry.
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                ws = self.fixture()
                ws.run(adapter, extra_env={"LI_PLUS_AGENT_KEY": "lay"})
                ws.run(adapter, extra_env={"LI_PLUS_AGENT_KEY": "lin"})
                state = json.loads(ws.state_file(adapter).read_text(encoding="utf-8"))
                self.assertEqual(set(state.get("agents", {})), {"lay", "lin"})

    # -- migration from the pre-#1811 shape -----------------------------------

    def test_legacy_single_partition_shape_migrates_without_losing_a_run(self) -> None:
        for adapter in ADAPTERS:
            with self.subTest(adapter=adapter):
                ws = self.fixture()
                state_path = ws.state_file(adapter)
                state_path.parent.mkdir(parents=True, exist_ok=True)
                state_path.write_text(
                    json.dumps(
                        {
                            "sections": {"rules_tree": "deadbeef"},
                            "last_emit_at": "2026-09-01T00:00:00Z",
                        }
                    ),
                    encoding="utf-8",
                )
                migrated = ws.run(adapter)
                self.assertIn(
                    FAIL_SAFE_MARK,
                    migrated,
                    f"{adapter}: a legacy-shape state file did not fail-safe "
                    "into a full emit",
                )
                state = json.loads(state_path.read_text(encoding="utf-8"))
                self.assertIn("agents", state)
                self.assertNotIn("sections", state)
                # And the migration is a one-time cost, not a permanent one:
                # the very next run against the now-migrated file is diff-only.
                repeat = ws.run(adapter)
                self.assertNotIn(FAIL_SAFE_MARK, repeat)


if __name__ == "__main__":
    unittest.main()
