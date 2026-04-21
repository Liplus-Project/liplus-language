---
name: on-pr-creation
description: Invoke when creating a PR; enforces one PR per parent issue, Closes keyword format, self-assign bot, draft PR early open for parent with sub-issues.
layer: L4-operations
---

# PR Creation

One PR per parent issue (see Sub-issue Rules#Single parent PR flow).
Parent issue with sub-issues = single PR that closes all sub-issues + the parent on merge.
Per-sub-issue PR is prohibited.

Draft PR early open (optional, for per-commit CI visibility):
On parent issue with sub-issues, open the parent PR as draft immediately after the first commit is pushed.
command = gh pr create --draft -R {owner}/{repo} --base main --head {session-branch} ...
pull_request.synchronize CI fires on every subsequent push, giving per-commit CI without splitting PRs.
Mark ready for review (gh pr ready {pr}) only after all sub-issues are complete and the PR body is final.
Draft PR is not required; it is a convenience for long-running parent work.

PR body format:
  per issue block:
    line1 = "Closes #{issue_number}" (for non-parent issues, including sub-issues)
    line2_to_3 = two to three line summary of that issue
  order = non-parent issues first, then parent (if any); omit deferred and open children.
  parent issue reference under single parent PR flow = "Closes #{parent_number}" (parent closes together with sub-issues on the single final merge).
  "Part of #{parent_number}" is used only when the current PR is NOT the final parent PR — e.g. an explicitly deferred remainder PR on a different parent issue. In the canonical single parent PR flow, "Part of" does not appear.
  "Closes" triggers GitHub auto-close on merge. "Part of" does not, so parent is preserved.
  GitHub auto-close keywords (authoritative list): close / closes / closed / fix / fixes / fixed / resolve / resolves / resolved.
  "Refs" is not a close keyword and does not auto-close; do not use "Refs" for issues that should close on merge.
Detail belongs in issue, not in PR.

On PR created:
1 = self-assign AI bot to PR assignees:
    gh pr edit {pr} -R {owner}/{repo} --add-assignee liplus-lin-lay
    rationale: existing issue-side assignee does not auto-propagate to the PR entity. Self-assign makes "AI owns this PR" explicit in the Assignees field.
    mechanism note: GitHub rejects `--add-reviewer` self-assignment silently, but allows `--add-assignee` self-assign for PR author (empirically verified 2026-04-20 on PR #1099).
    scope: assignee self-assign is UI trail only; it does not replace the formal self-review record (`gh pr review --comment`, see [PR Review]).
2 = proceed to [CI Loop] immediately, no human instruction required.
Merge execution is unified to AI across all modes (see [Merge]). GitHub auto-merge handoff is no longer used.
