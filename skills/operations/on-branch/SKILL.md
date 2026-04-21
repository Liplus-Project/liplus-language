---
name: on-branch
description: Invoke when human intent to act now is detected; handles NOW/SOON/SOMEDAY timing tier judgment, label assignment, branch creation via gh issue develop.
layer: L4-operations
---

# Branch And Label Flow

Trigger = human intent to act now detected via dialogue.
Judgment = read atmosphere, not checklist.
If unclear = ask with feeling, not mechanically.

Timing tiers:
NOW     -> label=in-progress + branch create
SOON    -> label=backlog     + no branch
SOMEDAY -> label=deferred    + no branch

Axis separation:
Lifecycle labels = when to act.
Maturity labels  = how converged the issue body is.
Do not use lifecycle labels as substitute for memo/forming/ready.

Atmosphere reading scope:
Applies to timing tier judgment (NOW / SOON / SOMEDAY) only.
Label assignment is a deterministic mapping from tier result, not a second atmosphere read.
Once tier is judged, label follows the tiers table without re-reading atmosphere.

Branch existence check (before creation):
local:  git branch --list {branch-name}
remote: gh api repos/{owner}/{repo}/branches/{branch-name} (404=not_exists)
If remote exists = existing GitHub branch cannot be retroactively linked.
If local only   = gh issue develop still allowed (local will be overwritten).
If not exists   = proceed normally.

Branch creation:
command  = gh issue develop {issue_number} -R {owner}/{repo} --name {session-branch} --base main
assignee = gh api repos/{owner}/{repo}/issues/{issue_number}/assignees --method POST -f 'assignees[]=liplus-lin-lay'

Merge behavior:
PR merge auto-closes the parent issue via issue reference.
Parent branch is linked to parent issue via gh issue develop, so any PR from that branch
auto-closes the parent on merge. This is safe under the single parent PR flow (see Sub-issue Rules):
the single merge happens only after all sub-issues are done, so parent auto-close lands correctly.
Per-sub-issue PR on the parent branch is prohibited precisely because it triggers parent auto-close
before the remaining sub-issues complete.
If a unit needs an independent branch and PR = it is a sibling issue, not a sub-issue.
Create it as an independent issue with its own parent branch.

On local error:
gh issue develop may fail locally but succeed on GitHub side.
Check linked branches before retrying:
  gh api graphql -f query='{ repository(owner:"{owner}",name:"{repo}") { issue(number:{number}) { linkedBranches { nodes { ref { name } } } } } }'
If linked = use existing linked branch, do not create new branch.
If not linked = retry or escalate.
