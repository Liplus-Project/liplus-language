---
name: operations-on-release
description: Invoke when a release is about to be created / a branch is about to be deleted / a force push is about to run / a release completion report is about to be written. Provides the human confirmation list, the pre-create CD check, the canonical gh release create command, version base and tag or title conventions, and release completion report discipline. Release state flags live in `skills/operations-on-release-state/SKILL.md`; the mandatory post-release mirror lives in `skills/operations-on-wiki-sync/SKILL.md`; version type criteria live in `rules/operations/release-version-rule.md` (always-on).
layer: L4-operations
---

<human-confirmation-required>

# Human Confirmation Required

Stop immediately when:
human says wait or stop or matte.

Always confirm before:
release create (version type and target tag) (after CD check passes)
branch delete (when linked issue may close)
force push
Mode-dependent confirm (trigger mode only): issue selection, issue execution start.

</human-confirmation-required>

<release-version-rule>

# Release Version Rule

Relocated to `rules/operations/release-version-rule.md` (always-on rules layer, single source, #1484). Judgment criteria (v0.x.x/v1.0.0 base, judgment axis, patch / minor / major definitions, Important note, proposal/confirmation authority split, application-moment trigger) live there. This skill does not restate them.

</release-version-rule>

<release-state-rule>

# Release State Rule

Relocated to `skills/operations-on-release-state/SKILL.md` (#1598). The prerelease / latest state axis, the Latest anchor requirement, the anchor flip procedure, bootstrap transient state, and bulk state normalization live there. This skill does not restate them.

The one clause that binds at release-create time is carried by the canonical command below: `--latest=false` is passed explicitly.

</release-state-rule>

<canonical-release-creation-command-ai>

# Canonical Release Creation Command (AI)

```
gh release create {tag} \
  --target main \
  --title {version} \
  --generate-notes \
  --latest=false
```

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

Relocated to `skills/operations-on-wiki-sync/SKILL.md` (#1598). Ownership boundary, pre-sync verification assertions, the diff-targeted drift set, and the 8-step procedure live there.

Wiki sync is part of the release procedure, not a follow-up task. Wiki sync gates release flow completion: the release flow is not complete until that skill's procedure has run.

</post-release-wiki-sync>

<release-completion-report-discipline>

## Release Completion Report Discipline

Release create completion report contains release URL + post-release task completion only. The report does NOT mention any of the following:
- Latest flip (`gh release edit --latest=true`) — separate human-gated step on an independent axis (`rules/operations/execution-mode.md` human judgment gate)
- Real-device verification / runtime check
- go-sign solicitation phrasing ("いただければ" / "どうぞ" / "判断で")
- Waiting / standby positioning ("Latest 未 flip = 待機状態")

Real-device verification structure:
Real-device verification is multi-session continuous observation by human, not a single-session event. Normal session operation after a release IS the verification. AI emitting "flip 待ち" on a freshly-created release misreads continuous observation as a single-event gate. Human flips Latest on its own timing when accumulated observation crosses the threshold.

Application moments (apply discipline at):
- Release create completion report (the primary trigger).
- Cold-start synthesis: when release tag list is surfaced and Latest flag is observed on a prior version, do NOT surface "Latest behind / flip pending" as unique insight. Hook surfaces raw material; AI side stays silent on the Latest position.
- Any AI-side mention of release state outside an explicit human inquiry.

Detection signs:
- Report tail trailing into "～いただければ" / "～どうぞ" / "Latest flip の go-sign" / "あとは Master の判断で".
- "次のステップ" / "あとは" surfacing in release completion report.
- "実機検証してから" being mentioned by AI (verification is human's autonomous process).
- Cold-start synthesis about to surface "v1.x.y が出ているが Latest は前版" as unique insight.

On detection: drop all Latest-related mentions; end the report at "release URL + post-release tasks done".

</release-completion-report-discipline>

</release-execution-procedure>
