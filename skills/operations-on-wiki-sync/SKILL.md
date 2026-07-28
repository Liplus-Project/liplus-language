---
name: operations-on-wiki-sync
description: Invoke when a release has just been published and docs must be mirrored to the GitHub Wiki / a wiki sync pre-push verification or integrity assertion needs to run / a new repository wiki needs its one-shot seed setup / a case-only rename must be applied to the wiki working tree on Windows. Provides the docs-owned versus wiki-only ownership boundary, the sidebar and cross-reference integrity assertions with the code-notation stripping algorithm, the diff-targeted drift set computation, and the 8-step sync procedure. Wiki sync gates release flow completion.
layer: L4-operations
---

<post-release-wiki-sync>

# Post-release Wiki Sync

After release is published, sync docs/ to GitHub Wiki.

</post-release-wiki-sync>

<ownership-boundary>

## Ownership Boundary

Since 2026-04-26, naming refactor 2026-05-21.

- **docs/-owned files** (uppercase + numeric prefix + Home + _Footer): docs/ is source of truth, wiki is mirror; the wiki copy must match docs/ byte-for-byte after sync. `docs/Decision-Structure.md` (the Decision Structure layer index) is a regular docs/-owned uppercase file; it is read by `adapter/claude/hooks/on-session-start.sh` for cold-start synthesis on the docs/ side and visible in nav on the wiki side.
- **Wiki-only files** (lowercase kebab-case `[a-z]*.md` judgment-record entries, plus `_Sidebar.md` and any other wiki-only navigation): wiki owns them, docs/ does not have a counterpart, sync must preserve them. Decision Structure entries no longer carry a sequence prefix; ordering lives in `docs/Decision-Structure.md` and `_Sidebar.md` explicitly.

</ownership-boundary>

<pre-sync-verification>

## Pre-sync Verification

Mandatory before the step 5 / step 6 commit.

- Run `git -C {tmpdir} status --short` and confirm only docs/-owned paths appear in deletes (`D`) and updates (`M`).
- If `D` or `M` appears for any wiki-only file (lowercase kebab-case `[a-z]*.md` or `_Sidebar.md`), STOP and escalate to human. Selective wipe pattern divergence is the recurring failure mode; do not push to wiki on this signal.
- Sidebar integrity assertion (post-step 4, pre-step 5): verify `{tmpdir}/_Sidebar.md` references every navigable entry. Build the expected slug set from `{tmpdir}` filesystem:
  - `Home`
  - every `{tmpdir}/[A-Z]*.md` (docs/-owned uppercase + numeric prefix, slug = filename without `.md`)
  - every `{tmpdir}/[0-9]*.md`
  - every `{tmpdir}/[a-z]*.md` (wiki-only kebab-case judgment-record entries)
  Excluded from the expected set: `_Sidebar.md`, `_Footer.md` (navigation infrastructure, not target entries).
  Before extraction, remove code notation from `{tmpdir}/_Sidebar.md` body text using the same removal algorithm as the Cross-reference integrity assertion below (#1547). Extract referenced slugs by parsing `](<slug>)` link targets from the code-stripped body. If `expected - referenced` is non-empty, STOP and escalate to human naming the missing slug(s). Do not push to wiki on this signal: sidebar drift means the PR that added the entry did not maintain navigation, and release sync is the wrong layer to silently auto-fix.
  Rationale: entry create / rename commits happen between releases, separated from wiki sync timing. Sync is the natural recurring checkpoint to enforce the invariant. Dogfood (2026-05-21): build-2026-05-20.1 sync left E-J + p / r / s / t / u silently absent from `_Sidebar.md`; manual recovery via wiki commit `5e47a90`.
- Cross-reference integrity assertion (post-step 4, pre-step 5): verify every wiki-internal markdown link target in `{tmpdir}/*.md` resolves to an existing file. Before extraction, remove code notation from the body: link-like notation inside code, or inside an HTML comment, is documentation about the notation or invisible markup, not a real link. Remove notation in this order, each pass covering the whole body before the next pass starts: HTML comments, then HTML elements, then fenced code blocks, then indented code blocks, then inline code spans last.
  - HTML comment: opened by `<!--`, closed by the next `-->`. If no closing `-->` exists, the comment extends to end of file.
  - HTML element: `<pre>...</pre>` (block-level) or `<code>...</code>` (inline-level), matched to its closing tag case-insensitively. If an opening tag has no matching closing tag, the element extends to end of file.
  - Fenced code block: an opening line containing nothing but a run of 3 or more backticks or 3 or more tildes (an optional info string may follow on the same line). The block extends to the next line that likewise contains nothing but a run of the same character with length >= the opening run (the closing fence). If no such line exists, the fence extends to end of file.
  - Indented code block: a maximal run of consecutive lines each indented by 4 spaces or a tab, ending at the first line that is not so indented.
  - Inline code span: a run of N backtick characters, closed by the next run of exactly N backticks. If no closing run of exactly N backticks exists, the opening run is not a code span and is left as literal text.
  This order matters on two axes: HTML comments are removed before indentation is checked, because deleting a comment can change a line's leading whitespace and change whether that line qualifies as an indented code block; and every enclosing form is removed before inline code spans, so a fence's or tag's own backtick run is not mistaken for an inline-span delimiter and does not swallow unrelated text. Build the resolution set:
  - existing slugs = `Home` + every `{tmpdir}/[A-Z]*.md` + every `{tmpdir}/[0-9]*.md` + every `{tmpdir}/[a-z]*.md` (all slugs without `.md` extension)
  - extracted slugs = every `](<x>)` occurrence inside the code-stripped `{tmpdir}/*.md` body where `<x>` does NOT contain `://`, does NOT start with `#`, and does NOT contain `/`. Strip any `#section` fragment from `<x>` before resolution. These are wiki-internal page references.
  If any extracted slug is not in the resolution set, STOP and escalate to human naming the source file + broken target slug. Do not push to wiki on this signal: broken cross-reference means an entry was renamed without updating its referrers, and release sync is the wrong layer to silently auto-rewrite link targets.
  Rationale: with kebab-case naming (no fixed prefix), entry rename is a routine operation. Broken cross-references accumulate silently between releases. Sync is the natural recurring checkpoint to surface them. Same shape as sidebar integrity: STOP & escalate, no auto-fix.
  Code-notation exclusion (#1547): without stripping, the assertion's own spec text self-matches - this file and `docs/4.-Operations.md` describe the pattern using `](<x>)` notation inside inline code spans, and the wiki entry `wiki-sync-sidebar-integrity-check.md` does the same. That produced 3 false-positive STOPs on every release (observed 2026-07-26, v1.19.11 / build-2026-07-26.3). After stripping code notation, all 66 real links resolved with zero true broken references.

</pre-sync-verification>

<new-repo-setup>

## New-repo Setup

One-shot, before first sync.

- Seed initial docs/ with `Home.md` / `_Footer.md` / canonical uppercase + numeric prefix files (`docs/[A-Z]*.md`, `docs/[0-9]*.md`) including `docs/Decision-Structure.md` as the Decision Structure layer index.
- Push `_Sidebar.md` directly to wiki on the wiki repo (not via docs/).
- Decision Structure entries (`<topic>.md` lowercase kebab-case, no sequence prefix) are wiki-only from creation; do not place under docs/.

</new-repo-setup>

<sync-steps>

## Sync Steps

  1. Clone wiki repo (line-ending normalization disabled so the working tree matches the raw blob byte-for-byte): git -c core.autocrlf=false clone https://github.com/{owner}/{repo}.wiki.git {tmpdir}
     Rationale: on Windows hosts a default clone applies `autocrlf=true` and checks the wiki working tree out as CRLF even when the blob is LF. `cmp -s docs/X {tmpdir}/X` would then return non-zero on the line-ending difference alone, flagging every docs/-owned file as drift (false to_copy) and pushing pure line-ending churn. `core.autocrlf=false` keeps the working tree identical to the blob; combined with the LF-normalized compare in step 3 the drift set reflects real content diffs only.
  2. Configure identity (clone-and-throw-away pattern requires explicit identity):
     git -C {tmpdir} config user.name  "{commit-author-name}"
     git -C {tmpdir} config user.email "{commit-author-email}"
  3. Compute drift set (diff-targeted, bounded blast radius) — enumerate the exact files that differ between docs/ source and wiki/ working tree, then operate only on that set:
     - **to_copy** = docs/-owned filenames present in `docs/` whose content differs from `{tmpdir}/` counterpart (includes both new files and content-changed files; resolve filenames via `docs/[A-Z]*.md`, `docs/[0-9]*.md`, `docs/Home.md`, `docs/_Footer.md`).
     - **to_delete** = docs/-owned filenames present in `{tmpdir}/` but no longer present in `docs/` (rename / removal on docs/ side).
     Reference algorithm:
     ```
     shopt -s nullglob
     # Line-ending-normalized content compare: strip CR from both sides, then cmp.
     # Returns 0 when content is identical ignoring CR (LF vs CRLF), non-zero on real content diff.
     # No-op on LF-only hosts (no CR to strip → identical to a raw cmp); neutralizes a
     # CRLF working-tree checkout on Windows so line endings alone never register as drift.
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
     Line-ending normalization axis: `content_same` compares CR-stripped content, so a docs/ (LF) vs wiki (CRLF) pair with identical content is NOT flagged as drift. Real content differences still register (CR stripping does not alter non-CR bytes). This is the defensive complement to the `core.autocrlf=false` clone in step 1 — the clone keeps the working tree LF, and the normalized compare guarantees correctness even if some other path reintroduces CR. The mirror invariant (`cp docs/$name {tmpdir}/$name` on real drift) is unchanged.
     The drift set explicitly omits lowercase kebab-case files (`[a-z]*.md`, Decision Structure entries) and `_Sidebar.md`; those are wiki-only and never enter `to_copy` / `to_delete`.
  4. Apply the drift set with explicit per-file operations (bounded; no unbounded glob deletion):
     ```
     for name in "${to_delete[@]}"; do rm -f "{tmpdir}/$name"; done
     for name in "${to_copy[@]}";   do cp "docs/$name" "{tmpdir}/$name"; done
     ```
     Empty `to_copy` AND empty `to_delete` = no drift; skip the remaining commit/push steps and proceed straight to cleanup (step 8). Report no-op outcome.
  5. Stage all (covers both copies and deletes from step 4): git -C {tmpdir} add -A
  6. Commit: git -C {tmpdir} commit -m "sync: docs → wiki ({release_tag})"
  7. Push: git -C {tmpdir} push
  8. Cleanup: rm -rf {tmpdir}
If push fails (permission): escalate to human. Do not skip.

</sync-steps>

<diff-targeted-pattern-rationale>

## Diff-targeted Pattern Rationale

Replaces the prior wipe-and-copy.

- Blast radius bounded to the actually-changed files (no unbounded glob `rm` over the wiki working tree).
- End state is byte-for-byte identical to wipe-and-copy when `to_copy` covers every docs/-owned file and `to_delete` covers every removed-on-docs entry. The mirror invariant is preserved without the destructive primitive.
- Auto-mode classifier rejection of unbounded `rm [A-Z]*.md ...` patterns is structural (`rules/model/subtractive-structural-beauty.md` Artifact deletion calibration's blast-radius axis), not a transient block. Diff-targeted copy aligns with that axis by construction.
- Fallback note: if drift computation fails (e.g. `cmp` / `tr` unavailable, process substitution unsupported by the shell, filesystem encoding mismatch), STOP and escalate to human. Do not silently fall back to the wipe pattern. Process substitution (`<(...)`) requires bash/zsh; the wiki sync procedure already assumes a bash-class shell.
- Empirical anchor (build-2026-05-20.1 sync, 2026-05-21): diff-targeted pattern was first applied when the prior wipe-and-copy hit the auto-mode classifier; observed drift set was 7 files, all docs/-owned, and the resulting wiki state matched the wipe-and-copy outcome exactly.

</diff-targeted-pattern-rationale>

<windows-case-only-rename-hazard>

## Windows Case-only Rename Hazard

On Windows hosts the wiki repo filesystem is case-insensitive. A rename like `Installation.md` → `installation.md` cannot be applied via a single `git mv` and leaves the old case in the index.
Two-step pattern when sync involves case-only rename:

    git mv Installation.md __tmp_inst.md
    git mv __tmp_inst.md installation.md

Detection: `git -C {tmpdir} status --short` shows a `D` and `??` pair on the same name with case difference. Linux/Mac do not exhibit this hazard but the two-step is still applied for mirror-parity discipline.

</windows-case-only-rename-hazard>
