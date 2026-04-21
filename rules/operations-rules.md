---
globs:
alwaysApply: true
layer: L4-operations
---

# Operations Rules

Issue link via gh issue develop is always required.
gh issue develop must precede first push to GitHub.
Parent issue = one branch.
Sub-issues commit on the parent branch. No individual branches for sub-issues.
Parent issue with sub-issues = single parent PR. Per-sub-issue PR is prohibited.
Per-commit CI visibility uses draft PR opened early on the parent branch, not split PRs.
Commit title = ASCII English only, single line.
Japanese commit title is prohibited.
Commit body is not optional.
Commit body must contain: change summary + intent or background + issue number.
Minimum one Japanese sentence required in commit body.
English-only commit body is prohibited.
PR title = ASCII English only, single line.
PR body = Japanese.
Docs update must be in same PR as implementation. Split docs PR is prohibited.
docs/ is source of truth. Wiki is mirror, not source.
Wiki sync is mandatory after every release. Skipping wiki sync is prohibited.
Requirements spec is not post-implementation follow-up.
Before implementation starts = create or update corresponding requirements spec first.
PR title must include impact scope.
AI `gh release create` default = no state flag (prerelease=false, latest=false).
prerelease flag = AI option. Use only when an explicit test period is desired. Tag name stays final-form; no alpha/rc/-pre suffix. Promotion strips the flag, not the tag.
latest flag = human-only. Set via `gh release edit {tag} --latest=true` after real-device verification.
Release body = GitHub generated release notes. Pass --generate-notes. Do not pass empty body via --notes "".
mark_processed is mandatory for every consumed webhook event. Omission causes backlog accumulation.
