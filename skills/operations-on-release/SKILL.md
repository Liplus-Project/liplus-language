---
name: operations-on-release
description: Invoke for release create / branch delete / force push; handles release version rule (patch/minor/major), state rule (prerelease/latest), wiki sync, tag conventions, Latest anchor requirement, anchor flip procedure, bulk state normalization.
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

# Release Version Rule

v0.x.x = initial development. Anything may change. Not a stable release.
v1.0.0 = first stable release (semver compliant).

Judgment axis = change scale + user/system observability.
patch = everything else (docs / small fix / small spec / config / internal rule / governance structure change with no user/system observable impact). This issue (#1087) is itself a patch example: release-rule redesign is structurally governance but not observable from a Li+ user's surface.
minor = large refactor or large structural change that is user/system observable.
major = large-scale change or major goal milestone (phase transition, project milestone). Human decides.

Important note: "structural change -> minor" is wrong. "Structural change AND user/system observable -> minor". Governance / spec rule changes without observable impact stay patch regardless of structural scale.

AI proposes patch or minor. Human confirms minor or major. AI executes.

**Application-moment trigger:** Before writing a classification (patch / minor / major) in any artifact, Read this section literally. The recurring miss is omitting the "large" modifier on minor — observable change misclassified as minor when it is incremental scope (patch). See `skills/model-trigger-check-gate-actions/SKILL.md` Trigger moments.

# Release State Rule (independent axis from version type)

default = no state flag. prerelease=false, latest=false. This is the AI `gh release create` default for any version type.
prerelease = AI option. Apply only when an explicit test period is wanted. Tag name is final-form; do not append alpha.N / rc.N / -pre suffix. Promotion = strip flag (`gh release edit {tag} --prerelease=false`), keep the same tag.
latest = human-only. Real-device verification gate. Human flips via `gh release edit {tag} --latest=true`. Independent of version type: patch / minor / major all gate on the same real-device check.

**Authority axis**: "human-only" / "human flips via ..." refers to decision authority, not execution authority — human decides, AI executes `gh release edit ... --latest=true` after explicit go-sign. See `rules/operations/execution-mode.md` human judgment gate for the full gate list and axis definition.

# Canonical Release Creation Command (AI)

```
gh release create {tag} \
  --target main \
  --title {version} \
  --generate-notes \
  --latest=false
```

`--latest=false` must be passed explicitly. Omitting the flag makes gh CLI fall back to its default `legacy` behavior (semver + date auto-pick), which promotes the new release to Latest and silently demotes the existing Latest anchor.

# Latest Anchor Requirement

The repository must always hold at least one explicit Latest release (`make_latest=true`). This release is the Latest anchor.
When the anchor is absent, `--latest=false` on a new release is overridden by the legacy default and the new release is promoted to Latest against intent.
Treat the anchor as repo-wide persistent state, not a per-release attribute.

# Anchor Flip Procedure (human, after real-device verification)

```
gh release edit {new_tag} --repo {owner}/{repo} --latest=true
```

GitHub enforces a single Latest per repo, so the previous anchor automatically loses its Latest badge and transitions to the default (no-state) form. The new release becomes the Latest anchor.
Tag names remain unchanged across the flip; only the Latest state moves.

# Bootstrap / Transient State

For the first non-prerelease release of a repository, or whenever the anchor is lost, GitHub temporarily promotes the newest release to Latest via the legacy auto-pick. This transient Latest state is resolved the moment a human sets an explicit Latest anchor (one-Latest-only constraint performs the natural transition).
Do not treat this transient Latest as an AI-authored state; it is a platform-side default, not a governance decision.

# Bulk State Normalization

To normalize multiple existing releases to the no-state default, first pin one release as the anchor with `--latest=true`, then PATCH the remaining releases with `--latest=false`. Reversing the order leaves the repo anchorless, so `--latest=false` is silently overridden by the legacy default and one of the target releases ends up Latest again.

# Version Base Rule

Base on most recent release = includes prereleases.
Not latest stable only.
Use: `gh release list --limit 1` (includes prereleases).

# Release Tag and Title Rule

Tag format and release title follow project convention.
Default (Li+ language): cd_tag = build-YYYY-MM-DD.N, title = "{version}" (e.g. "v1.9.0")
npm package projects: tag = v{semver}, title = "v{semver}"
If project has CD workflow that creates tags: use existing CD-created tag, do not create new tag.
If project uses npm version: tag is created by npm version command.
Check project docs/ or CI/CD config for convention before creating release.

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

Execute the canonical `gh release create` command above with resolved {tag} and {version}.
AI proposes patch or minor; human confirms minor or major; AI executes.

## Post-release wiki sync

After release is published, sync docs/ to GitHub Wiki.

Ownership boundary (since 2026-04-26, naming refactor 2026-05-21):
- **docs/-owned files** (uppercase + numeric prefix + Home + _Footer): docs/ is source of truth, wiki is mirror; the wiki copy must match docs/ byte-for-byte after sync. `docs/Decision-Log.md` (the Decision Log layer index) is a regular docs/-owned uppercase file; it is read by `adapter/claude/hooks/on-session-start.sh` for cold-start synthesis on the docs/ side and visible in nav on the wiki side.
- **Wiki-only files** (lowercase kebab-case `[a-z]*.md` judgment-record entries, plus `_Sidebar.md` and any other wiki-only navigation): wiki owns them, docs/ does not have a counterpart, sync must preserve them. Decision Log entries no longer carry a sequence prefix; ordering lives in `docs/Decision-Log.md` and `_Sidebar.md` explicitly.

Pre-sync verification (mandatory before step 5/6 commit):
- Run `git -C {tmpdir} status --short` and confirm only docs/-owned paths appear in deletes (`D`) and updates (`M`).
- If `D` or `M` appears for any wiki-only file (lowercase kebab-case `[a-z]*.md` or `_Sidebar.md`), STOP and escalate to human. Selective wipe pattern divergence is the recurring failure mode; do not push to wiki on this signal.
- Sidebar integrity assertion (post-step 4, pre-step 5): verify `{tmpdir}/_Sidebar.md` references every navigable entry. Build the expected slug set from `{tmpdir}` filesystem:
  - `Home`
  - every `{tmpdir}/[A-Z]*.md` (docs/-owned uppercase + numeric prefix, slug = filename without `.md`)
  - every `{tmpdir}/[0-9]*.md`
  - every `{tmpdir}/[a-z]*.md` (wiki-only kebab-case judgment-record entries)
  Excluded from the expected set: `_Sidebar.md`, `_Footer.md` (navigation infrastructure, not target entries).
  Extract referenced slugs by parsing `](<slug>)` link targets from `{tmpdir}/_Sidebar.md`. If `expected - referenced` is non-empty, STOP and escalate to human naming the missing slug(s). Do not push to wiki on this signal: sidebar drift means the PR that added the entry did not maintain navigation, and release sync is the wrong layer to silently auto-fix.
  Rationale: entry create / rename commits happen between releases, separated from wiki sync timing. Sync is the natural recurring checkpoint to enforce the invariant. Dogfood (2026-05-21): build-2026-05-20.1 sync left E-J + p / r / s / t / u silently absent from `_Sidebar.md`; manual recovery via wiki commit `5e47a90`.
- Cross-reference integrity assertion (post-step 4, pre-step 5): verify every wiki-internal markdown link target in `{tmpdir}/*.md` resolves to an existing file. Build the resolution set:
  - existing slugs = `Home` + every `{tmpdir}/[A-Z]*.md` + every `{tmpdir}/[0-9]*.md` + every `{tmpdir}/[a-z]*.md` (all slugs without `.md` extension)
  - extracted slugs = every `](<x>)` occurrence inside `{tmpdir}/*.md` body where `<x>` does NOT contain `://`, does NOT start with `#`, and does NOT contain `/`. Strip any `#section` fragment from `<x>` before resolution. These are wiki-internal page references.
  If any extracted slug is not in the resolution set, STOP and escalate to human naming the source file + broken target slug. Do not push to wiki on this signal: broken cross-reference means an entry was renamed without updating its referrers, and release sync is the wrong layer to silently auto-rewrite link targets.
  Rationale: with kebab-case naming (no fixed prefix), entry rename is a routine operation. Broken cross-references accumulate silently between releases. Sync is the natural recurring checkpoint to surface them. Same shape as sidebar integrity: STOP & escalate, no auto-fix.

New-repo setup (one-shot, before first sync):
- Seed initial docs/ with `Home.md` / `_Footer.md` / canonical uppercase + numeric prefix files (`docs/[A-Z]*.md`, `docs/[0-9]*.md`) including `docs/Decision-Log.md` as the Decision Log layer index.
- Push `_Sidebar.md` directly to wiki on the wiki repo (not via docs/).
- Decision log entries (`<topic>.md` lowercase kebab-case, no sequence prefix) are wiki-only from creation; do not place under docs/.

Steps:
  1. Clone wiki repo: git clone https://github.com/{owner}/{repo}.wiki.git {tmpdir}
  2. Configure identity (clone-and-throw-away pattern requires explicit identity):
     git -C {tmpdir} config user.name  "{commit-author-name}"
     git -C {tmpdir} config user.email "{commit-author-email}"
  3. Selective wipe — remove only docs/-owned files from wiki, preserving wiki-only entries:
     ```
     shopt -s nullglob
     for f in {tmpdir}/[A-Z]*.md {tmpdir}/[0-9]*.md {tmpdir}/Home.md {tmpdir}/_Footer.md; do
       [ -e "$f" ] && rm -f "$f"
     done
     ```
     The pattern explicitly omits lowercase kebab-case files (`[a-z]*.md`, Decision Log entries) and `_Sidebar.md`, leaving them in place. `Decision-Log.md` (uppercase `D`) is caught by `[A-Z]*.md` as a regular docs/-owned file.
  4. Copy docs/ files: cp docs/*.md {tmpdir}/
     (docs/ holds only uppercase + numeric prefix files + `Home.md` + `_Footer.md` + `Decision-Log.md`; Decision Log entries live in wiki only, so this cp does not re-introduce them.)
  5. Stage all (including any deletes from step 3 that docs/ no longer covers): git -C {tmpdir} add -A
  6. Commit: git -C {tmpdir} commit -m "sync: docs → wiki ({release_tag})"
  7. Push: git -C {tmpdir} push
  8. Cleanup: rm -rf {tmpdir}
If push fails (permission): escalate to human. Do not skip.

Windows-specific (case-only rename hazard):
On Windows hosts the wiki repo filesystem is case-insensitive. A rename like `Installation.md` → `installation.md` cannot be applied via a single `git mv` and leaves the old case in the index.
Two-step pattern when sync involves case-only rename:

    git mv Installation.md __tmp_inst.md
    git mv __tmp_inst.md installation.md

Detection: `git -C {tmpdir} status --short` shows a `D` and `??` pair on the same name with case difference. Linux/Mac do not exhibit this hazard but the two-step is still applied for mirror-parity discipline.

Wiki sync is part of the release procedure, not a follow-up task.

## Post-release milestone delete (mandatory, gates release flow completion)

After wiki sync succeeds, delete the milestone shipped by this release:
  gh api -X DELETE repos/{owner}/{repo}/milestones/{milestone_number}
DELETE works directly on open milestones (no close step needed, empirically verified 2026-04-21).
Rationale: GitHub milestone UI retains no informational value post-release; audit lives in release notes + PR/commit history. Skipping causes stale accumulation (dogfood 2026-04-21: v1.14.1 / v1.14.2 / v1.15.0 / v1.15.1 leaked as open despite releases shipped).
Release flow is incomplete until this step runs.
