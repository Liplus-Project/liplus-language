---
name: operations-on-wiki-sync
description: Invoke when a release has just been published and docs must be mirrored to the GitHub Wiki / a wiki sync pre-push verification or integrity assertion needs to run / a new repository wiki needs its one-shot seed setup / a case-only rename must be applied to the wiki working tree on Windows. Provides the docs-owned versus wiki-only ownership boundary, the sidebar and cross-reference integrity assertions with the code-notation stripping algorithm, the diff-targeted drift set computation, and the 8-step sync procedure. Wiki sync gates release flow completion.
layer: L4-operations
---

<post-release-wiki-sync>

# Post-release Wiki Sync

After a release is published, mirror `docs/` into the GitHub Wiki. The sync gates release-flow completion; skipping it is prohibited.

</post-release-wiki-sync>

<ownership-boundary>

## Ownership Boundary

- **docs/-owned = uppercase + numeric-prefix `*.md`, `Home.md`, `_Footer.md`.** docs/ is source of truth and the wiki copy matches it byte-for-byte after sync. `docs/Decision-Structure.md` is one of these even though every entry it indexes is wiki-only: `adapter/claude/hooks/on-session-start.sh` reads the docs/ copy as cold-start material, so the docs/ side cannot be retired in favour of the wiki side.
- **Wiki-only = lowercase kebab-case `[a-z]*.md` Decision Structure entries, `_Sidebar.md`, and any other wiki-only navigation.** These have no docs/ counterpart, so any step that reads "absent from docs/" as "delete from wiki" erases them; sync preserves them instead. Entries carry no ordering prefix, so order is explicit in `docs/Decision-Structure.md` and `_Sidebar.md` rather than in the filenames.

</ownership-boundary>

<pre-sync-verification>

## Pre-sync Verification

The three assertions below run after step 4 and before the step 5 / step 6 commit. Each one is STOP-and-escalate on failure: name the offending file to the human and do not push. Do not repair the wiki from this layer either — sidebar drift and broken cross-references both mean an earlier PR did not maintain what it changed, and release sync is a recurring checkpoint, not the repair layer.

- **Confirm `git -C {tmpdir} status --short` shows `D` and `M` on docs/-owned paths only.** A `D` or `M` on any wiki-only file (`[a-z]*.md` or `_Sidebar.md`) means the step-4 file set diverged from the ownership boundary, which is this procedure's recurring failure mode.
- **Sidebar integrity: verify `{tmpdir}/_Sidebar.md` references every navigable entry.** Build the expected slug set from the `{tmpdir}` filesystem, not from docs/ or from an index file, so both ownership systems are counted as they will exist on the wiki:
  - `Home`
  - every `{tmpdir}/[A-Z]*.md` and every `{tmpdir}/[0-9]*.md` (docs/-owned; slug = filename without `.md`)
  - every `{tmpdir}/[a-z]*.md` (wiki-only kebab-case entries)

  Excluded from the expected set: `_Sidebar.md`, `_Footer.md` — navigation infrastructure, not target entries. Strip code notation from `{tmpdir}/_Sidebar.md` with the algorithm below. From the code-stripped body, build the referenced slug set as the union of Markdown inline link targets parsed from `](<slug>)` and GitHub Wiki native link targets parsed from `[[target]]` or `[[label|target]]`; for the labeled native form, the text to the right of `|` is the target. Strip any `#section` fragment from each extracted target before resolution. STOP if `expected - referenced` is non-empty.
- **Cross-reference integrity: verify every wiki-internal markdown link target in `{tmpdir}/*.md` resolves to an existing file.** Build the resolution set:
  - existing targets = for every existing `{tmpdir}/[A-Z]*.md`, `{tmpdir}/[0-9]*.md`, and `{tmpdir}/[a-z]*.md` file, both its extensionless slug and its exact filename including `.md` (`Home` and `Home.md` included). A `.md` target enters the set only when this enumeration found the corresponding Markdown file.
  - extracted targets = every `](<x>)` occurrence in the code-stripped body where `<x>` does NOT contain `://`, does NOT start with `#`, and does NOT contain `/`. Strip any `#section` fragment before resolution. Do not strip `.md`; compare the extracted notation as written against the resolution set.

  STOP if any extracted target is absent from the resolution set. Both notations are live because these bodies mirror into repository `docs/` as well, where only the `.md` form resolves (#1608).

**Code-notation stripping (both assertions).** Link-like notation inside code, or inside an HTML comment, documents the notation or is invisible markup — it is not a real link. Skipping this step is not a rare-edge risk but a guaranteed false-positive STOP on every release, because the assertion specs themselves (this file, `docs/4.-Operations.md`, and the wiki entry `wiki-sync-sidebar-integrity-check`) describe the pattern using that very notation. Remove notation in this order, each pass covering the whole body before the next pass starts: HTML comments, then HTML elements, then fenced code blocks, then indented code blocks, then inline code spans last.

- HTML comment: opened by `<!--`, closed by the next `-->`. If no closing `-->` exists, the comment extends to end of file.
- HTML element: `<pre>...</pre>` (block-level) or `<code>...</code>` (inline-level), matched to its closing tag case-insensitively. If an opening tag has no matching closing tag, the element extends to end of file.
- Fenced code block: an opening line containing nothing but a run of 3 or more backticks or 3 or more tildes (an optional info string may follow on the same line). The block extends to the next line that likewise contains nothing but a run of the same character with length >= the opening run. If no such line exists, the fence extends to end of file.
- Indented code block: a maximal run of consecutive lines each indented by 4 spaces or a tab, ending at the first line that is not so indented.
- Inline code span: a run of N backtick characters, closed by the next run of exactly N backticks. If no closing run of exactly N backticks exists, the opening run is not a code span and is left as literal text.

The order is load-bearing on two axes. HTML comments come before the indentation check because deleting a comment can change a line's leading whitespace and thus whether it qualifies as an indented code block. Every enclosing form comes before inline code spans so that a fence's or tag's own backtick run is not mistaken for an inline-span delimiter and does not swallow unrelated text.

</pre-sync-verification>

<new-repo-setup>

## New-repo Setup

One-shot, before the first sync.

- Seed `docs/` with `Home.md`, `_Footer.md`, and the canonical uppercase + numeric-prefix files (`docs/[A-Z]*.md`, `docs/[0-9]*.md`) including `docs/Decision-Structure.md`.
- Push `_Sidebar.md` directly to the wiki repo. It is wiki-only, so no sync step will ever create it from docs/.
- Create Decision Structure entries (`<topic>.md`, lowercase kebab-case, no ordering prefix) in the wiki from the start; placing one under docs/ makes it a mirrored docs/-owned file instead.

</new-repo-setup>

<sync-steps>

## Sync Steps

  1. Clone the wiki repo with line-ending normalization disabled, so the working tree matches the raw blob byte-for-byte: git -c core.autocrlf=false clone https://github.com/{owner}/{repo}.wiki.git {tmpdir}
     A default clone on a Windows host applies `autocrlf=true`, checks the tree out as CRLF even when the blob is LF, and makes every docs/-owned file compare as drift — pushing pure line-ending churn.
  2. Configure identity; the clone-and-throw-away pattern inherits none, and the step 6 commit fails without it:
     git -C {tmpdir} config user.name  "{commit-author-name}"
     git -C {tmpdir} config user.email "{commit-author-email}"
  3. Compute the drift set — enumerate the exact files that differ between the docs/ source and the wiki working tree, and operate only on that set. An unbounded destructive glob over the wiki working tree is not an acceptable substitute: its blast radius is the whole wiki, which `rules/model/subtractive-structural-beauty.md` Artifact deletion calibration puts on the wrong side of the axis, and the auto-mode classifier rejects it by construction rather than transiently.
     - **to_copy** = docs/-owned filenames present in `docs/` whose content differs from the `{tmpdir}/` counterpart (covers both new and content-changed files; resolve via `docs/[A-Z]*.md`, `docs/[0-9]*.md`, `docs/Home.md`, `docs/_Footer.md`).
     - **to_delete** = docs/-owned filenames present in `{tmpdir}/` but no longer present in `docs/` (rename or removal on the docs/ side).
     Reference algorithm:
     ```
     shopt -s nullglob
     # Line-ending-normalized content compare: strip CR from both sides, then cmp.
     # Returns 0 when content is identical ignoring CR (LF vs CRLF), non-zero on real content diff.
     # No-op on LF-only hosts; neutralizes a CRLF working-tree checkout on Windows so line
     # endings alone never register as drift, even if some path reintroduces CR past step 1.
     content_same() {  # args: docs_file wiki_file
       cmp -s <(tr -d '\r' < "$1") <(tr -d '\r' < "$2")
     }
     # Build docs/-owned filename set on docs/ side.
     docs_owned=()
     for f in docs/[A-Z]*.md docs/[0-9]*.md docs/Home.md docs/_Footer.md; do
       [ -e "$f" ] && docs_owned+=("$(basename "$f")")
     done
     # Build docs/-owned filename set on wiki side (same glob applied to tmpdir).
     wiki_docs_owned=()
     for f in {tmpdir}/[A-Z]*.md {tmpdir}/[0-9]*.md {tmpdir}/Home.md {tmpdir}/_Footer.md; do
       [ -e "$f" ] && wiki_docs_owned+=("$(basename "$f")")
     done
     # to_copy = docs/ entries whose content differs (wiki side absent, or content_same returns non-zero).
     to_copy=()
     for name in "${docs_owned[@]}"; do
       if [ ! -e "{tmpdir}/$name" ] || ! content_same "docs/$name" "{tmpdir}/$name"; then
         to_copy+=("$name")
       fi
     done
     # to_delete = wiki-side docs/-owned entries absent on docs/ side.
     to_delete=()
     for name in "${wiki_docs_owned[@]}"; do
       case " ${docs_owned[*]} " in
         *" $name "*) ;;
         *) to_delete+=("$name") ;;
       esac
     done
     ```
     The globs above never reach lowercase kebab-case files or `_Sidebar.md`; those are wiki-only and must not enter `to_copy` / `to_delete`.
     If drift computation itself fails (`cmp` / `tr` unavailable, process substitution unsupported — it requires a bash-class shell, filesystem encoding mismatch), STOP and escalate. Do not fall back to a wipe pattern.
  4. Apply the drift set with explicit per-file operations:
     ```
     for name in "${to_delete[@]}"; do rm -f "{tmpdir}/$name"; done
     for name in "${to_copy[@]}";   do cp "docs/$name" "{tmpdir}/$name"; done
     ```
     Empty `to_copy` AND empty `to_delete` = no drift; skip the commit and push steps, go straight to cleanup (step 8), and report the no-op outcome.
  5. Stage both copies and deletes: git -C {tmpdir} add -A
  6. Commit: git -C {tmpdir} commit -m "sync: docs → wiki ({release_tag})"
  7. Push: git -C {tmpdir} push
  8. Cleanup: rm -rf {tmpdir}
If push fails on permission, escalate to human. Do not skip.

</sync-steps>

<windows-case-only-rename-hazard>

## Windows Case-only Rename Hazard

On Windows hosts the wiki repo filesystem is case-insensitive, so a rename like `Installation.md` → `installation.md` cannot be applied by a single `git mv` and leaves the old case in the index. Use the two-step pattern:

    git mv Installation.md __tmp_inst.md
    git mv __tmp_inst.md installation.md

Detection: `git -C {tmpdir} status --short` shows a `D` and `??` pair on the same name with a case difference. Linux and Mac do not exhibit the hazard, but apply the two-step there as well so the procedure stays identical across hosts.

</windows-case-only-rename-hazard>
