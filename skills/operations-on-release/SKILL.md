---
name: operations-on-release
description: Invoke for release create / branch delete / force push; handles release state rule (prerelease/latest), wiki sync, tag conventions, Latest anchor requirement, anchor flip procedure, bulk state normalization. Version rule criteria (patch/minor/major) live in rules/operations/release-version-rule.md (always-on).
layer: L4-operations
---

# Human Confirmation Required

Stop immediately when:
human says wait or stop or matte.

Always confirm before:
release create (version type and target tag) (after CD check passes)
branch delete (when linked issue may close)
force push
Mode-dependent confirm (trigger mode only): issue selection, issue execution start.

# Release Version Rule

Relocated to `rules/operations/release-version-rule.md` (always-on rules layer, single source, #1484). Judgment criteria (v0.x.x/v1.0.0 base, judgment axis, patch / minor / major definitions, Important note, proposal/confirmation authority split, application-moment trigger) live there. This skill does not restate them.

# Release State Rule (independent axis from version type)

default = no state flag. prerelease=false, latest=false. This is the AI `gh release create` default for any version type.
prerelease = AI option. Apply only when an explicit test period is wanted. Tag name is final-form; do not append alpha.N / rc.N / -pre suffix. Promotion = strip flag (`gh release edit {tag} --prerelease=false`), keep the same tag.
latest = human-only. Real-device verification gate. Human flips via `gh release edit {tag} --latest=true`. Independent of version type: patch / minor / major all gate on the same real-device check.

**Authority axis**: "human-only" / "human flips via ..." refers to decision authority, not execution authority — human decides, AI executes `gh release edit ... --latest=true` after explicit go-sign. See `rules/operations/execution-mode.md` human judgment gate for the full gate list and axis definition.

# Canonical Release Creation Command (AI)

```
gh release create {tag} \
  --target main \
  --title {version} \
  --generate-notes \
  --latest=false
```

`--latest=false` must be passed explicitly. Omitting the flag makes gh CLI fall back to its default `legacy` behavior (semver + date auto-pick), which promotes the new release to Latest and silently demotes the existing Latest anchor.

# Latest Anchor Requirement

The repository must always hold at least one explicit Latest release (`make_latest=true`). This release is the Latest anchor.
When the anchor is absent, `--latest=false` on a new release is overridden by the legacy default and the new release is promoted to Latest against intent.
Treat the anchor as repo-wide persistent state, not a per-release attribute.

# Anchor Flip Procedure (human, after real-device verification)

```
gh release edit {new_tag} --repo {owner}/{repo} --latest=true
```

GitHub enforces a single Latest per repo, so the previous anchor automatically loses its Latest badge and transitions to the default (no-state) form. The new release becomes the Latest anchor.
Tag names remain unchanged across the flip; only the Latest state moves.

# Bootstrap / Transient State

For the first non-prerelease release of a repository, or whenever the anchor is lost, GitHub temporarily promotes the newest release to Latest via the legacy auto-pick. This transient Latest state is resolved the moment a human sets an explicit Latest anchor (one-Latest-only constraint performs the natural transition).
Do not treat this transient Latest as an AI-authored state; it is a platform-side default, not a governance decision.

# Bulk State Normalization

To normalize multiple existing releases to the no-state default, first pin one release as the anchor with `--latest=true`, then PATCH the remaining releases with `--latest=false`. Reversing the order leaves the repo anchorless, so `--latest=false` is silently overridden by the legacy default and one of the target releases ends up Latest again.

# Version Base Rule

Base on most recent release = includes prereleases.
Not latest stable only.
Use: `gh release list --limit 1` (includes prereleases).

# Release Tag and Title Rule

Tag format and release title follow project convention.
Default (Li+ language): cd_tag = build-YYYY-MM-DD.N, title = "{version}" (e.g. "v1.9.0")
npm package projects: tag = v{semver}, title = "v{semver}"
If project has CD workflow that creates tags: use existing CD-created tag, do not create new tag.
If project uses npm version: tag is created by npm version command.
Check project docs/ or CI/CD config for convention before creating release.

# Release Execution Procedure

## Release checks (pre-create)

1. CD check:
  if mcp__github-webhook-mcp available:
    poll get_pending_status every 60 seconds
    on workflow_run pending: list_pending_events -> get_event -> check conclusion -> mark_processed
  else:
    Poll gh api until all CD checks complete.
  CD pass = proceed. CD fail = escalate to human (do not release).

## Release create

Execute the canonical `gh release create` command above with resolved {tag} and {version}.
Version type proposal and confirmation follow `rules/operations/release-version-rule.md`.

## Post-release wiki sync

After release is published, sync docs/ to GitHub Wiki.

Ownership boundary (since 2026-04-26, naming refactor 2026-05-21):
- **docs/-owned files** (uppercase + numeric prefix + Home + _Footer): docs/ is source of truth, wiki is mirror; the wiki copy must match docs/ byte-for-byte after sync. `docs/Decision-Structure.md` (the Decision Structure layer index) is a regular docs/-owned uppercase file; it is read by `adapter/claude/hooks/on-session-start.sh` for cold-start synthesis on the docs/ side and visible in nav on the wiki side.
- **Wiki-only files** (lowercase kebab-case `[a-z]*.md` judgment-record entries, plus `_Sidebar.md` and any other wiki-only navigation): wiki owns them, docs/ does not have a counterpart, sync must preserve them. Decision Structure entries no longer carry a sequence prefix; ordering lives in `docs/Decision-Structure.md` and `_Sidebar.md` explicitly.

Pre-sync verification (mandatory before step 5/6 commit):
- Run `git -C {tmpdir} status --short` and confirm only docs/-owned paths appear in deletes (`D`) and updates (`M`).
- If `D` or `M` appears for any wiki-only file (lowercase kebab-case `[a-z]*.md` or `_Sidebar.md`), STOP and escalate to human. Selective wipe pattern divergence is the recurring failure mode; do not push to wiki on this signal.
- Sidebar integrity assertion (post-step 4, pre-step 5): verify `{tmpdir}/_Sidebar.md` references every navigable entry. Build the expected slug set from `{tmpdir}` filesystem:
  - `Home`
  - every `{tmpdir}/[A-Z]*.md` (docs/-owned uppercase + numeric prefix, slug = filename without `.md`)
  - every `{tmpdir}/[0-9]*.md`
  - every `{tmpdir}/[a-z]*.md` (wiki-only kebab-case judgment-record entries)
  Excluded from the expected set: `_Sidebar.md`, `_Footer.md` (navigation infrastructure, not target entries).
  Extract referenced slugs by parsing `](<slug>)` link targets from `{tmpdir}/_Sidebar.md`. If `expected - referenced` is non-empty, STOP and escalate to human naming the missing slug(s). Do not push to wiki on this signal: sidebar drift means the PR that added the entry did not maintain navigation, and release sync is the wrong layer to silently auto-fix.
  Rationale: entry create / rename commits happen between releases, separated from wiki sync timing. Sync is the natural recurring checkpoint to enforce the invariant. Dogfood (2026-05-21): build-2026-05-20.1 sync left E-J + p / r / s / t / u silently absent from `_Sidebar.md`; manual recovery via wiki commit `5e47a90`.
- Cross-reference integrity assertion (post-step 4, pre-step 5): verify every wiki-internal markdown link target in `{tmpdir}/*.md` resolves to an existing file. Build the resolution set:
  - existing slugs = `Home` + every `{tmpdir}/[A-Z]*.md` + every `{tmpdir}/[0-9]*.md` + every `{tmpdir}/[a-z]*.md` (all slugs without `.md` extension)
  - extracted slugs = every `](<x>)` occurrence inside `{tmpdir}/*.md` body where `<x>` does NOT contain `://`, does NOT start with `#`, and does NOT contain `/`. Strip any `#section` fragment from `<x>` before resolution. These are wiki-internal page references.
  If any extracted slug is not in the resolution set, STOP and escalate to human naming the source file + broken target slug. Do not push to wiki on this signal: broken cross-reference means an entry was renamed without updating its referrers, and release sync is the wrong layer to silently auto-rewrite link targets.
  Rationale: with kebab-case naming (no fixed prefix), entry rename is a routine operation. Broken cross-references accumulate silently between releases. Sync is the natural recurring checkpoint to surface them. Same shape as sidebar integrity: STOP & escalate, no auto-fix.

New-repo setup (one-shot, before first sync):
- Seed initial docs/ with `Home.md` / `_Footer.md` / canonical uppercase + numeric prefix files (`docs/[A-Z]*.md`, `docs/[0-9]*.md`) including `docs/Decision-Structure.md` as the Decision Structure layer index.
- Push `_Sidebar.md` directly to wiki on the wiki repo (not via docs/).
- Decision Structure entries (`<topic>.md` lowercase kebab-case, no sequence prefix) are wiki-only from creation; do not place under docs/.

Steps:
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

Rationale for diff-targeted pattern (replaces prior wipe-and-copy):
- Blast radius bounded to the actually-changed files (no unbounded glob `rm` over the wiki working tree).
- End state is byte-for-byte identical to wipe-and-copy when `to_copy` covers every docs/-owned file and `to_delete` covers every removed-on-docs entry. The mirror invariant is preserved without the destructive primitive.
- Auto-mode classifier rejection of unbounded `rm [A-Z]*.md ...` patterns is structural (`rules/model/subtractive-structural-beauty.md` Artifact deletion calibration's blast-radius axis), not a transient block. Diff-targeted copy aligns with that axis by construction.
- Fallback note: if drift computation fails (e.g. `cmp` / `tr` unavailable, process substitution unsupported by the shell, filesystem encoding mismatch), STOP and escalate to human. Do not silently fall back to the wipe pattern. Process substitution (`<(...)`) requires bash/zsh; the wiki sync procedure already assumes a bash-class shell.
- Empirical anchor (build-2026-05-20.1 sync, 2026-05-21): diff-targeted pattern was first applied when the prior wipe-and-copy hit the auto-mode classifier; observed drift set was 7 files, all docs/-owned, and the resulting wiki state matched the wipe-and-copy outcome exactly.

Windows-specific (case-only rename hazard):
On Windows hosts the wiki repo filesystem is case-insensitive. A rename like `Installation.md` → `installation.md` cannot be applied via a single `git mv` and leaves the old case in the index.
Two-step pattern when sync involves case-only rename:

    git mv Installation.md __tmp_inst.md
    git mv __tmp_inst.md installation.md

Detection: `git -C {tmpdir} status --short` shows a `D` and `??` pair on the same name with case difference. Linux/Mac do not exhibit this hazard but the two-step is still applied for mirror-parity discipline.

Wiki sync is part of the release procedure, not a follow-up task. Wiki sync gates release flow completion.

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
