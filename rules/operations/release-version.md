---
globs:
alwaysApply: true
layer: L4-operations
---

# Release Version

Authoritative release version and state rules.
`skills/operations-on-release/SKILL.md` executes against this spec.
See `rules/operations/operations.md` for the one-line release rule set.

## Release version rule

v0.x.x = initial development. Anything may change. Not a stable release.
v1.0.0 = first stable release (semver compliant).

Judgment axis = change scale + user/system observability.
patch = everything else (docs / small fix / small spec / config / internal rule / governance structure change with no user/system observable impact). This issue (#1087) is itself a patch example: release-rule redesign is structurally governance but not observable from a Li+ user's surface.
minor = large refactor or large structural change that is user/system observable.
major = large-scale change or major goal milestone (phase transition, project milestone). Human decides.

Important note: "structural change -> minor" is wrong. "Structural change AND user/system observable -> minor". Governance / spec rule changes without observable impact stay patch regardless of structural scale.

AI proposes patch or minor. Human confirms minor or major. AI executes.

## Release state rule (independent axis from version type)

default = no state flag. prerelease=false, latest=false. This is the AI `gh release create` default for any version type.
prerelease = AI option. Apply only when an explicit test period is wanted. Tag name is final-form; do not append alpha.N / rc.N / -pre suffix. Promotion = strip flag (`gh release edit {tag} --prerelease=false`), keep the same tag.
latest = human-only. Real-device verification gate. Human flips via `gh release edit {tag} --latest=true`. Independent of version type: patch / minor / major all gate on the same real-device check.

## Canonical release creation command (AI)

```
gh release create {tag} \
  --target main \
  --title {version} \
  --generate-notes \
  --latest=false
```

`--latest=false` must be passed explicitly. Omitting the flag makes gh CLI fall back to its default `legacy` behavior (semver + date auto-pick), which promotes the new release to Latest and silently demotes the existing Latest anchor.

## Latest anchor requirement

The repository must always hold at least one explicit Latest release (`make_latest=true`). This release is the Latest anchor.
When the anchor is absent, `--latest=false` on a new release is overridden by the legacy default and the new release is promoted to Latest against intent.
Treat the anchor as repo-wide persistent state, not a per-release attribute.

## Anchor flip procedure (human, after real-device verification)

```
gh release edit {new_tag} --repo {owner}/{repo} --latest=true
```

GitHub enforces a single Latest per repo, so the previous anchor automatically loses its Latest badge and transitions to the default (no-state) form. The new release becomes the Latest anchor.
Tag names remain unchanged across the flip; only the Latest state moves.

## Bootstrap / transient state

For the first non-prerelease release of a repository, or whenever the anchor is lost, GitHub temporarily promotes the newest release to Latest via the legacy auto-pick. This transient Latest state is resolved the moment a human sets an explicit Latest anchor (one-Latest-only constraint performs the natural transition).
Do not treat this transient Latest as an AI-authored state; it is a platform-side default, not a governance decision.

## Bulk state normalization

To normalize multiple existing releases to the no-state default, first pin one release as the anchor with `--latest=true`, then PATCH the remaining releases with `--latest=false`. Reversing the order leaves the repo anchorless, so `--latest=false` is silently overridden by the legacy default and one of the target releases ends up Latest again.

## Version base rule

Base on most recent release = includes prereleases.
Not latest stable only.
Use: `gh release list --limit 1` (includes prereleases).

## Release tag and title rule

Tag format and release title follow project convention.
Default (Li+ language): cd_tag = build-YYYY-MM-DD.N, title = "{version}" (e.g. "v1.9.0")
npm package projects: tag = v{semver}, title = "v{semver}"
If project has CD workflow that creates tags: use existing CD-created tag, do not create new tag.
If project uses npm version: tag is created by npm version command.
Check project docs/ or CI/CD config for convention before creating release.
