---
name: operations-on-release
description: Invoke when a release is being executed after its human confirmation / a pre-create CD check is about to run / a release tag or title must be resolved against project convention / subagent capability is unavailable and the parent is executing operations directly. Provides the release create procedure.
layer: L4-operations
---

<canonical-release-creation-command-ai>

# Canonical Release Creation Command (AI)

```
gh release create {tag} \
  --target main \
  --title {version} \
  --generate-notes \
  --latest=false
```

Release body = GitHub generated release notes (`--generate-notes`). Do not pass an empty body via `--notes ""`.

`--latest=false` must be passed explicitly. Omitting the flag makes gh CLI fall back to its default `legacy` behavior (semver + date auto-pick), which promotes the new release to Latest and silently demotes the existing Latest anchor.

</canonical-release-creation-command-ai>

<version-base-rule>

# Version Base Rule

Base on most recent release = includes prereleases.
Not latest stable only.
Use: `gh release list --limit 1` (includes prereleases).

</version-base-rule>

<release-tag-and-title-rule>

# Release Tag and Title Rule

Tag format and release title follow project convention.
Default (Li+ language): cd_tag = build-YYYY-MM-DD.N, title = "{version}" (e.g. "v1.9.0")
npm package projects: tag = v{semver}, title = "v{semver}"
If project has CD workflow that creates tags: use existing CD-created tag, do not create new tag.
If project uses npm version: tag is created by npm version command.
Check project docs/ or CI/CD config for convention before creating release.

</release-tag-and-title-rule>

<release-execution-procedure>

# Release Execution Procedure

<release-checks-pre-create>

## Release checks (pre-create)

1. CD check:
  if mcp__github-webhook-mcp available:
    poll get_pending_status every 60 seconds
    on workflow_run pending: list_pending_events -> get_event -> check conclusion -> mark_processed
  else:
    Poll gh api until all CD checks complete.
  CD pass = proceed. CD fail = escalate to human (do not release).

</release-checks-pre-create>

<release-create>

## Release create

Execute the canonical `gh release create` command above with resolved {tag} and {version}.
Version type proposal and confirmation follow `rules/operations/release-version-rule.md`.

</release-create>

<post-release-wiki-sync>

## Post-release wiki sync

Run `skills/operations-on-wiki-sync/SKILL.md`. The gate literal is canonical in `rules/operations/operations.md` Operations Rules (always-on); do not restate it here.

</post-release-wiki-sync>

</release-execution-procedure>
