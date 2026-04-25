---
name: operations-on-release
description: Invoke for release create / branch delete / force push; handles release version rule (patch/minor/major), state rule (prerelease/latest), wiki sync, tag conventions.
layer: L4-operations
---

# Human Confirmation Required

Stop immediately when:
human says wait or stop or matte.

Always confirm before:
release create (version type and target tag) (after CD check passes)
branch delete (when linked issue may close)
force push
Mode-dependent confirm (trigger mode only): issue selection, issue execution start.

See `rules/operations/release-version.md` for the authoritative release version rule, state rule, canonical `gh release create` command, Latest anchor requirement, anchor flip procedure, bootstrap / transient state handling, bulk state normalization, version base rule, and tag / title rule.

# Release Execution Procedure

## Release checks (pre-create)

1. CD check:
  if mcp__github-webhook-mcp available:
    poll get_pending_status every 60 seconds
    on workflow_run pending: list_pending_events -> get_event -> check conclusion -> mark_processed
  else:
    Poll gh api until all CD checks complete.
  CD pass = proceed. CD fail = escalate to human (do not release).
2. Milestone check (if milestone exists for this release version):
  Verify all issues in the milestone are closed.
  Report milestone contents to human before proceeding.

## Release create

Execute the canonical `gh release create` command from `rules/operations/release-version.md` with resolved {tag} and {version}.
AI proposes patch or minor; human confirms minor or major; AI executes.

## Post-release wiki sync

After release is published, sync docs/ to GitHub Wiki.

Ownership boundary (since 2026-04-26):
- **docs/-owned files** (uppercase + numeric prefix + Home + _Footer): docs/ is source of truth, wiki is mirror; the wiki copy must match docs/ byte-for-byte after sync.
- **Wiki-only files** (lowercase prefix `[a-z].-*.md` judgment-record entries, plus `_Sidebar.md` and any other wiki-only navigation): wiki owns them, docs/ does not have a counterpart, sync must preserve them.
- The single exception is `docs/a.-Decision-Log.md` which exists in BOTH docs/ (read by `adapter/claude/hooks/on-session-start.sh` for cold-start synthesis) and wiki (visible in nav). It travels through the sync because docs/ has the source.

Steps:
  1. Clone wiki repo: git clone https://github.com/{owner}/{repo}.wiki.git {tmpdir}
  2. Configure identity (clone-and-throw-away pattern requires explicit identity):
     git -C {tmpdir} config user.name  "{commit-author-name}"
     git -C {tmpdir} config user.email "{commit-author-email}"
  3. Selective wipe — remove only docs/-owned files from wiki, preserving wiki-only entries:
     ```
     shopt -s nullglob
     for f in {tmpdir}/[A-Z]*.md {tmpdir}/[0-9]*.md {tmpdir}/Home.md {tmpdir}/_Footer.md {tmpdir}/a.-*.md; do
       [ -e "$f" ] && rm -f "$f"
     done
     ```
     The pattern explicitly omits lowercase non-`a` prefixes (`[b-z].-*.md`) and `_Sidebar.md`, leaving them in place.
  4. Copy docs/ files: cp docs/*.md {tmpdir}/
     (After migration, docs/ no longer holds `b.-` / `c.-` / ... entries, so this cp does not re-introduce them.)
  5. Stage all (including any deletes from step 3 that docs/ no longer covers): git -C {tmpdir} add -A
  6. Commit: git -C {tmpdir} commit -m "sync: docs → wiki ({release_tag})"
  7. Push: git -C {tmpdir} push
  8. Cleanup: rm -rf {tmpdir}
If push fails (permission): escalate to human. Do not skip.
Wiki sync is part of the release procedure, not a follow-up task.

## Post-release milestone delete (mandatory, gates release flow completion)

After wiki sync succeeds, delete the milestone shipped by this release:
  gh api -X DELETE repos/{owner}/{repo}/milestones/{milestone_number}
DELETE works directly on open milestones (no close step needed, empirically verified 2026-04-21).
Rationale: GitHub milestone UI retains no informational value post-release; audit lives in release notes + PR/commit history. Skipping causes stale accumulation (dogfood 2026-04-21: v1.14.1 / v1.14.2 / v1.15.0 / v1.15.1 leaked as open despite releases shipped).
Release flow is incomplete until this step runs.
