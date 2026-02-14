# GitHub Rules Page (OpenAPI Automation Version)

This document defines the standard operational flow for OpenAPI based repository automation.

---

## 1. OpenAPI Automation Workflow Template

All file modifications must follow the flow no exception.

1. Create Issue
  - define purpose
  - define scope
  - reference related issue

2. Create sub branch from main
  - name: issue-{issue_number}-description
  - base sha from main
3. Get Target File Content
  - getRepoContent
  - ref = sub branch
  - extract sha
4. Regenerate Full Content
  - Generate full file as UTF-8
  - Line breaks must be LF
  - Do not perform multi-stage re-encoding

5. Base64 Encode Once
  - Encode the final UTF-8 LF string
  - No re-encoding passes
6. Update File
  - createOrUpdateRepoFile
  - message
  - content = base64
  - sha = retrieved sha
  - branch = sub branch

7. Verify Update
  - getRepoContent again
  - decode
  - compare full content
  - enforce utf-8 LF integrity

8. Create PR 
  - head = sub branch
  - base = main
  - body must reference issue

---

## 2. UTF-8 LF Safe Base64 Update Method

Japanese content must never be passed through multiple encoding transformations.

Requirements:

- All file content must be generated as UTF-8
- All newlines must be LF only
- Base64 encode only once
- Never decode and re-encode multiple times

---

## 3. Failure Prevention
- UTF-8 must be preserved from start to final
- No intermediate text manipulation
- No automatic encoding conversions
- No partial file replacement

---

## 4. Structure Requirement

 All operations must be executed in a single continuous API run.

No human confirmation steps between operations.

Result is valid only if:

- File content matches exact generated content
- SHA matches update
- PRis successfully created

---

END_OF_DOCUMENT
