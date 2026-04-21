---
name: on-commit
description: Invoke when committing and pushing; defines git push primary and fallback procedures.
layer: L4-operations
---

# Commit And Push

Git push:
primary          = git push origin {session-branch}:{target-branch}
fallback_single  = gh api repos/{owner}/{repo}/contents/{path} (put base64 sha)
fallback_multi_1 = create blobs: gh api .../git/blobs (per file)
fallback_multi_2 = create tree:  gh api .../git/trees  (verify count after)
fallback_multi_3 = create commit: gh api .../git/commits
fallback_multi_4 = update ref:   gh api .../git/refs/heads/{branch}
