---
name: operations-on-release-state
description: Invoke when a release state flag is about to be set or changed on a GitHub release (prerelease or latest) / a Latest anchor flip is being executed after its human go-sign has already been given / a prerelease is about to be promoted to stable / several existing releases need their state normalized in bulk / subagent capability is unavailable and the parent is executing operations directly. Provides the release state rule and the Latest anchor flip procedure.
layer: L4-operations
---

<release-state-rule>

# Release State Rule

Independent axis from version type. Version type criteria (patch / minor / major) live in `rules/operations/release-version-rule.md` (always-on) and are not restated here.

default = no state flag. prerelease=false, latest=false. This is the AI `gh release create` default for any version type.
prerelease = AI option. Apply only when an explicit test period is wanted. Tag name is final-form; do not append alpha.N / rc.N / -pre suffix. Promotion = strip flag (`gh release edit {tag} --prerelease=false`), keep the same tag.
latest = human-only. Real-device verification gate. Human flips via `gh release edit {tag} --latest=true`. Independent of version type: patch / minor / major all gate on the same real-device check.

**Authority axis**: "human-only" / "human flips via ..." refers to decision authority, not execution authority — human decides, AI executes `gh release edit ... --latest=true` after explicit go-sign. See `rules/operations/execution-mode.md` human judgment gate for the full gate list and axis definition.

</release-state-rule>

<latest-anchor-requirement>

# Latest Anchor Requirement

The repository must always hold at least one explicit Latest release (`make_latest=true`). This release is the Latest anchor.
When the anchor is absent, `--latest=false` on a new release is overridden by the legacy default and the new release is promoted to Latest against intent.
Treat the anchor as repo-wide persistent state, not a per-release attribute.

This is why `skills/operations-on-release/SKILL.md` Canonical Release Creation Command passes `--latest=false` explicitly.

</latest-anchor-requirement>

<anchor-flip-procedure-human-after-real-device-verification>

# Anchor Flip Procedure (human, after real-device verification)

```
gh release edit {new_tag} --repo {owner}/{repo} --latest=true
```

GitHub enforces a single Latest per repo, so the previous anchor automatically loses its Latest badge and transitions to the default (no-state) form. The new release becomes the Latest anchor.
Tag names remain unchanged across the flip; only the Latest state moves.

</anchor-flip-procedure-human-after-real-device-verification>

<bootstrap-transient-state>

# Bootstrap / Transient State

For the first non-prerelease release of a repository, or whenever the anchor is lost, GitHub temporarily promotes the newest release to Latest via the legacy auto-pick. This transient Latest state is resolved the moment a human sets an explicit Latest anchor (one-Latest-only constraint performs the natural transition).
Do not treat this transient Latest as an AI-authored state; it is a platform-side default, not a governance decision.

</bootstrap-transient-state>

<bulk-state-normalization>

# Bulk State Normalization

To normalize multiple existing releases to the no-state default, first pin one release as the anchor with `--latest=true`, then PATCH the remaining releases with `--latest=false`. Reversing the order leaves the repo anchorless, so `--latest=false` is silently overridden by the legacy default and one of the target releases ends up Latest again.

</bulk-state-normalization>
