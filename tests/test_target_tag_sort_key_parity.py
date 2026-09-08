"""Cross-surface parity for the `LI_PLUS_CHANNEL=tag` target tag sort key.

Issue #1918.

The defect this pins: `--sort=-creatordate` does not order ref names. It reads
the object each tag points at, so `git ls-remote` fails outright in two states
the update path actually reaches -- run from outside a git repository (Phase 3.1
before the first clone exists), and run inside a shallow clone whose newest tag
points past the truncation. Both failures are swallowed (`2>/dev/null`), leaving
the target tag empty, which pins the workspace at
`sentinel-tag(adapter=...,target=unknown)` permanently.

The replacement is `-v:refname`: it reads ref names only, so it resolves in both
states, and it compares numeric components numerically, so the two-digit `N` in
`build-YYYY-MM-DD.N` orders correctly where plain `-refname` does not.

What is pinned
--------------
The sort key is one decision spread across four surfaces plus their two doc
mirrors. One surface left behind makes the same workspace resolve a different
target tag depending on which host adapter ran, which is the shape issue #1804
already produced once on a different value. So the assertions are: every
`ls-remote --tags --sort=` occurrence across the six surfaces carries a key that
orders on ref names alone, every surface carries at least one occurrence (a port
that lost its call is not silently a pass), and all six agree on one key.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

# Surfaces carrying the tag-channel target resolution: the three hook ports, the
# Phase 3.1 spec they implement, and the two docs that mirror it.
SURFACES = (
    "adapter/claude/hooks/on-session-start.sh",
    "adapter/codex/hooks/on-session-start.sh",
    "adapter/codex/hooks/on-session-start.ps1",
    "Li+update.md",
    "docs/B.-Configuration.md",
    "docs/C.-Update.md",
)

SORT_CALL = re.compile(r"ls-remote\s+--tags\s+--sort=(-?[A-Za-z0-9:_-]+)")

# Keys `git for-each-ref` orders without reading object data. Anything else
# (creatordate, taggerdate, committerdate, objectsize, subject, ...) makes the
# command fail in the two states above.
REF_NAME_ONLY_KEYS = frozenset({"refname", "-refname", "v:refname", "-v:refname"})


def sort_keys(surface: str) -> list[str]:
    text = (ROOT / surface).read_text(encoding="utf-8")
    return SORT_CALL.findall(text)


class TargetTagSortKeyParityTest(unittest.TestCase):
    def test_every_surface_carries_the_resolution_call(self) -> None:
        for surface in SURFACES:
            with self.subTest(surface=surface):
                self.assertTrue(
                    sort_keys(surface),
                    f"{surface} carries no `ls-remote --tags --sort=` call; a port that "
                    f"lost the call must fail here rather than pass vacuously",
                )

    def test_no_surface_sorts_on_object_data(self) -> None:
        for surface in SURFACES:
            for key in sort_keys(surface):
                with self.subTest(surface=surface, key=key):
                    self.assertIn(
                        key,
                        REF_NAME_ONLY_KEYS,
                        f"{surface} sorts on `{key}`, which requires object data and "
                        f"fails outside a repository and in a shallow clone",
                    )

    def test_all_surfaces_agree_on_one_key(self) -> None:
        observed = {key for surface in SURFACES for key in sort_keys(surface)}
        self.assertEqual(
            observed,
            {"-v:refname"},
            "the sort key must be identical across every surface; a split makes one "
            "workspace resolve two target tags depending on which port ran",
        )


if __name__ == "__main__":
    unittest.main()
