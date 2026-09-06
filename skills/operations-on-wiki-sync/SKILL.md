---
name: operations-on-wiki-sync
description: Invoke when a release has just been published and docs must be mirrored to the GitHub Wiki / a wiki sync pre-push verification or integrity assertion needs to run / a new repository wiki needs its one-shot seed setup / a case-only rename must be applied to the wiki working tree on Windows. Provides the ownership boundary, the integrity assertions, and the sync procedure. Wiki sync gates release flow completion.
layer: L4-operations
---

<post-release-wiki-sync>

# Post-release Wiki Sync

After a release is published, mirror `docs/` into the GitHub Wiki. The sync gates release-flow completion; skipping it is prohibited.

</post-release-wiki-sync>

<ownership-boundary>

## Ownership Boundary

- **docs/-owned = every `*.md` at the top level of `docs/`.** Location decides; the filename is not consulted. docs/ is source of truth and the wiki copy matches it byte-for-byte after sync. `docs/D.-Installation.md` is docs/-owned exactly as `docs/4.-Operations.md` is. `docs/Decision-Structure.md` is docs/-owned even though every entry it indexes is wiki-only: `adapter/claude/hooks/on-session-start.sh` reads the docs/ copy as cold-start material, so the docs/ side cannot be retired in favour of the wiki side. Top level only — the wiki namespace is flat, so a nested `docs/**/x.md` has no wiki counterpart and is out of scope for sync.
- **Wiki-only = an explicit list, closed here.** These have no docs/ counterpart. Sync never copies them and never deletes them.
  - `_Sidebar.md`. No sync step creates it from docs/. It is the only navigation page on the list: `Home.md` and `_Footer.md` live in `docs/`, so location already makes them docs/-owned. A wiki navigation page that is on neither side reaches the human as unclassified, and that escalation is how this list grows — by a change to this file, not by a per-repository convention.
  - Every Decision Structure entry indexed by `docs/Decision-Structure.md`. Their bodies are authored directly in the wiki under `Decision_Structure_Write_Autonomy`, so for these the wiki is source (`rules/operations/operations.md` states that exception to docs-is-source-of-truth). Entries carry no ordering prefix, so order is explicit in that index and in `_Sidebar.md` rather than in the filenames.
- **Anything else on the wiki is unclassified: present in the wiki, absent from `docs/`, absent from the list above.** It is not a deletion candidate. STOP and escalate, naming the page (step 4). Ownership is not observable from the wiki side — an unclassified page is either a leftover from a docs/ rename, where deleting is correct, or a wiki-source page the list has not caught up with, where deleting destroys the source. The recurring instance of the second is a Decision Structure entry pushed to the wiki before the index row for it has merged: `skills/evolution-decision-structure-write/SKILL.md` pushes the entry straight to the wiki at its step 5 and updates `docs/Decision-Structure.md` through the main-repo PR flow at its step 6, so that window is normal operation, not an error state. One of the two mistakes is unrecoverable from this side, so the widening of ownership above does not get to decide deletion; the human names which.

The two axes are separate and this section moves only the first: **which side is source** is decided by location plus the explicit list, while **whether an orphan is deleted** stays a human judgment gate (`rules/operations/execution-mode.md` human judgment gate — human decides, AI executes). Reading a widened ownership rule as a widened deletion rule is what erases the wiki-source entries.

</ownership-boundary>

<pre-sync-verification>

## Pre-sync Verification

The three assertions below run after step 5 and before the step 6 / step 7 commit. Each one is STOP-and-escalate on failure: name the offending file to the human and do not push. Do not repair the wiki from this layer either — sidebar drift and broken cross-references both mean an earlier PR did not maintain what it changed, and release sync is a recurring checkpoint, not the repair layer.

- **Confirm `git -C {tmpdir} status --short` shows `D` and `M` on names present in `docs/` only.** A `D` or `M` on any other name means the step-5 file set diverged from the ownership boundary, which is this procedure's recurring failure mode. One exception: a page the human confirmed for deletion at step 4 shows a `D` and is expected.
- **Sidebar integrity: verify `{tmpdir}/_Sidebar.md` references every navigable entry.** Build the expected slug set from the `{tmpdir}` filesystem, not from docs/ or from an index file, so both ownership systems are counted as they will exist on the wiki: every `{tmpdir}/*.md` (slug = filename without `.md`), which reaches docs/-owned files and wiki-only entries alike without asking which is which.

  Excluded from the expected set: `_Sidebar.md`, `_Footer.md` — navigation infrastructure, not target entries. Strip code notation from `{tmpdir}/_Sidebar.md` with the algorithm below. From the code-stripped body, build the referenced slug set as the union of Markdown inline link targets parsed from `](<slug>)` and GitHub Wiki native link targets parsed from `[[target]]` or `[[label|target]]`; for the labeled native form, the text to the right of `|` is the target. Strip any `#section` fragment from each extracted target before resolution. STOP if `expected - referenced` is non-empty.
- **Cross-reference integrity: verify every wiki-internal markdown link target in `{tmpdir}/*.md` resolves to an existing file.** Build the resolution set:
  - existing targets = for every existing `{tmpdir}/*.md` file, both its extensionless slug and its exact filename including `.md` (`Home` and `Home.md` included). A `.md` target enters the set only when this enumeration found the corresponding Markdown file. The enumeration is one glob rather than a per-ownership set because the assertion asks only whether a target resolves to a file that exists, which does not depend on who owns it.
  - extracted targets = every `](<x>)` occurrence in the code-stripped body where `<x>` does NOT contain `://`, does NOT start with `#`, and does NOT contain `/`. Strip any `#section` fragment before resolution. Do not strip `.md`; compare the extracted notation as written against the resolution set.

  STOP if any extracted target is absent from the resolution set. Both notations are live because these bodies mirror into repository `docs/` as well, where only the `.md` form resolves.

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

- Seed `docs/` with `Home.md`, `_Footer.md`, and the repository's requirements and reference docs including `docs/Decision-Structure.md`. Filename shape is free; sitting at the top level of `docs/` is what makes a file docs/-owned.
- Push `_Sidebar.md` directly to the wiki repo. It is wiki-only, so no sync step will ever create it from docs/.
- Create Decision Structure entries (`<topic>.md`, lowercase kebab-case, no ordering prefix) in the wiki from the start; placing one under docs/ makes it a mirrored docs/-owned file instead.

</new-repo-setup>

<sync-steps>

## Sync Steps

The source side is named by ref, not by the caller's working tree: every read of `docs/` below goes through `origin/main` (`git show origin/main:docs/<name>` / `git ls-tree origin/main docs/`), and no step reads `docs/` off the checkout. The ref is `origin/main` and not the release tag — release is the sync's trigger, not the selector of its content — so the wiki may stand ahead of the latest release tag. A stale checkout is not detected downstream either: the Pre-sync Verification assertions below measure ownership and reference resolution, and an old body is owned exactly as a current one is.

  1. Fetch the source ref, so the `origin/main` reads below resolve to the current upstream tree: git fetch origin
     Failure = STOP and escalate. Do not continue from the caller's working tree; with the ref unresolved there is no source to mirror, and this is the only freshness-side check in the procedure.
  2. Clone the wiki repo with line-ending normalization disabled, so the working tree matches the raw blob byte-for-byte: git -c core.autocrlf=false clone https://github.com/{owner}/{repo}.wiki.git {tmpdir}
     A default clone on a Windows host applies `autocrlf=true`, checks the tree out as CRLF even when the blob is LF, and makes every docs/-owned file compare as drift — pushing pure line-ending churn. The docs/ side needs no counterpart setting: `git show` returns the blob's raw bytes and never passes through a working-tree filter.
  3. Configure identity; the clone-and-throw-away pattern inherits none, and the step 7 commit fails without it:
     git -C {tmpdir} config user.name  "{commit-author-name}"
     git -C {tmpdir} config user.email "{commit-author-email}"
  4. Compute the drift set — enumerate the exact files that differ between the `origin/main` docs/ tree and the wiki working tree, and operate only on that set. An unbounded destructive glob over the wiki working tree is not an acceptable substitute: its blast radius is the whole wiki, which `rules/evolution/memory-entry-format.md` Artifact deletion calibration puts on the wrong side of the axis, and the auto-mode classifier rejects it by construction rather than transiently.
     - **to_copy** = docs/-owned filenames whose `origin/main` content differs from the `{tmpdir}/` counterpart (covers both new and content-changed files; resolve via `git ls-tree origin/main docs/`).
     - **unclassified** = names present in `{tmpdir}/` that are neither docs/-owned nor on the wiki-only list. Non-empty = STOP and escalate, naming each: the reference algorithm below exits non-zero at that point, so the stop is executed rather than left to a sentence a later reader has to remember. What the guard blocks is the silent pass-through, not a deletion — step 5 copies and never removes, so an unobserved STOP takes nothing off the wiki and instead leaves the page standing while the mirror is reported as synced. Do not delete and do not proceed to step 5; a docs/-side rename or removal surfaces here, and so does a wiki-source page the list has not caught up with. The escalation classifies each name by whether it has history under `docs/` on the source ref (`git log --diff-filter=AD -- docs/<name>`): history present = likely a leftover from a docs/-side rename or removal; history absent = likely a wiki-source page, where deleting destroys the source. That classification is a reading, not a decision — neither branch deletes, and which of the two a page is stays the human's to name (`rules/operations/operations.md` published-wiki deletion gate). On an explicit human go-sign for a named page, `rm -f` that page and continue; without one, the page stays.
     Reference algorithm:
     ```
     shopt -s nullglob
     SRC_REF=origin/main
     # Line-ending-normalized content compare: strip CR from both sides, then cmp.
     # Returns 0 when content is identical ignoring CR (LF vs CRLF), non-zero on real content diff.
     # No-op on LF-only hosts; neutralizes a CRLF working-tree checkout on Windows so line
     # endings alone never register as drift, even if some path reintroduces CR past step 2.
     content_same() {  # args: docs_path_in_ref wiki_file
       cmp -s <(git show "$SRC_REF:$1" | tr -d '\r') <(tr -d '\r' < "$2")
     }
     # docs/-owned = every top-level docs/*.md in the ref. Location decides; the filename is not
     # consulted. ls-tree without -r lists direct children only, so a nested docs/**/x.md never enters.
     docs_owned=()
     while read -r name; do docs_owned+=("$name"); done < <(
       git ls-tree --name-only "$SRC_REF" docs/ | sed -n 's#^docs/\(.*\.md\)$#\1#p'
     )
     # wiki-only = the explicit list: _Sidebar.md plus every entry the Decision Structure index names.
     # The index is read from the ref as well; leaving it on the working tree reopens the same
     # rollback on the index-versus-body axis.
     # Slugs come from the index's own wiki link targets, so the list tracks the index rather than a
     # filename pattern. Over-extraction only spares a page from deletion and under-extraction only
     # routes one to the human, so precision here is not load-bearing in either direction.
     wiki_only=("_Sidebar.md")
     if git cat-file -e "$SRC_REF:docs/Decision-Structure.md" 2>/dev/null; then
       while read -r slug; do wiki_only+=("$slug.md"); done < <(
         git show "$SRC_REF:docs/Decision-Structure.md" |
           grep -oE '/wiki/[A-Za-z0-9._-]+' | sed 's#.*/wiki/##' | sort -u
       )
     fi
     # to_copy = docs/ entries whose content differs (wiki side absent, or content_same returns non-zero).
     to_copy=()
     for name in "${docs_owned[@]}"; do
       if [ ! -e "{tmpdir}/$name" ] || ! content_same "docs/$name" "{tmpdir}/$name"; then
         to_copy+=("$name")
       fi
     done
     # unclassified = wiki pages owned by neither side. Escalation set, not a deletion set.
     unclassified=()
     for f in {tmpdir}/*.md; do
       name="$(basename "$f")"
       case " ${docs_owned[*]} " in *" $name "*) continue ;; esac
       case " ${wiki_only[*]} "  in *" $name "*) continue ;; esac
       unclassified+=("$name")
     done
     # Guard. Non-empty = stop here, non-zero, naming each page with its docs/-history
     # reading. Nothing is deleted on either branch; the reading only shortens the human's
     # move from investigation to confirmation.
     if [ ${#unclassified[@]} -ne 0 ]; then
       for name in "${unclassified[@]}"; do
         if [ -n "$(git log --diff-filter=AD --format=%H -1 "$SRC_REF" -- "docs/$name")" ]; then
           echo "unclassified: $name (docs/ history present; likely a rename or removal leftover)"
         else
           echo "unclassified: $name (no docs/ history; likely wiki-source, deleting destroys the source)"
         fi
       done
       exit 1
     fi
     ```
     If drift computation itself fails (`cmp` / `tr` unavailable, process substitution unsupported — it requires a bash-class shell, filesystem encoding mismatch), STOP and escalate. Do not fall back to a wipe pattern.
  5. Apply the drift set with explicit per-file operations, reading each blob from the same ref:
     ```
     for name in "${to_copy[@]}"; do git show "$SRC_REF:docs/$name" > "{tmpdir}/$name"; done
     ```
     Empty `to_copy` = no drift; skip the commit and push steps, go straight to cleanup (step 9), and report the no-op outcome. The condition carries no `unclassified` term: a non-empty set exits at step 4, so this line is only ever read with it empty.
  6. Stage both copies and deletes: git -C {tmpdir} add -A
  7. Commit: git -C {tmpdir} commit -m "sync: docs -> wiki ({release_tag})"
  8. Push: git -C {tmpdir} push
  9. Cleanup: rm -rf {tmpdir}
If push fails on permission, escalate to human. Do not skip.

</sync-steps>

<windows-case-only-rename-hazard>

## Windows Case-only Rename Hazard

On Windows hosts the wiki repo filesystem is case-insensitive, so a rename like `Installation.md` → `installation.md` cannot be applied by a single `git mv` and leaves the old case in the index. Use the two-step pattern:

    git mv Installation.md __tmp_inst.md
    git mv __tmp_inst.md installation.md

Detection: `git -C {tmpdir} status --short` shows a `D` and `??` pair on the same name with a case difference. Linux and Mac do not exhibit the hazard, but apply the two-step there as well so the procedure stays identical across hosts.

</windows-case-only-rename-hazard>
