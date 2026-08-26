# Li+ Update

Adapter / configuration sync procedure for Li+.
Invoked when the adapter sentinel tag, Li+config schema, or workspace language contract drifts from the target state (the on-session-start.sh hook emits `LI_PLUS_UPDATE_STATUS=needed` in that case). Most sessions skip this file because the hook reports `LI_PLUS_UPDATE_STATUS=unnecessary`.
Never output credentials to chat. Read Li+config.md first to resolve all settings before executing this file.

Phases execute in order. Each phase declares its dependencies.

## Phase 1: Environment Detection

Dependencies: none.

1.1. Detect runtime environment:
- if environment variable CODEX_HOME or CODEX_THREAD_ID exists: runtime=codex
- elif environment variable CLAUDECODE exists: runtime=claude
- else: ask user once (Claude or Codex?) and proceed with answer.

1.2. Secure Li+config.md permissions:
- Linux/Mac only: `chmod 600 Li+config.md` (owner read/write only, since the file contains tokens).
- Skip if permissions are already 600 or stricter.
- Windows: skip (NTFS ACL under user profile directories is already restricted by default).

## Phase 2: Authentication and Settings

Dependencies: Phase 1 (runtime detected).

2.1. Prerequisite install (gh CLI):
- Branching is by detected **host OS**, not by adapter (`runtime=claude` / `runtime=codex`). Both adapters can and do run natively on Linux, macOS, or Windows — e.g. the Claude adapter running natively on Windows via Git Bash/MSYS2 is a verified env (#1518), not merely a Linux/Mac case. Do not infer host OS from which adapter is active.
- runtime=claude: managed by `adapter/claude/hooks/on-session-start.sh`. The hook detects host OS itself (`uname -s`: `Linux*` / `Darwin*` / `MINGW*|MSYS*|CYGWIN*`). On Linux it ensures `~/.local/bin/gh` exists (arch-detected auto-install on absence, silent skip on presence). On macOS and Windows (incl. Git-Bash/MSYS2), auto-install is NOT attempted; `gh` is treated as a documented prerequisite and a platform-appropriate install instruction (`brew install gh` / `winget install --id GitHub.cli`) is surfaced as a cold-start material entry when absent from PATH. Bootstrap walkthrough does not perform install steps either way.
- runtime=codex: `gh` is treated as a documented prerequisite, NOT silently installed by bootstrap, regardless of host OS. If `gh` is absent, surface the install instruction appropriate to the detected host OS (e.g. `winget install --id GitHub.cli` on Windows, `brew install gh` on macOS) and continue once present. Do not run the install command on the user's behalf. See `docs/D.-Installation.md` for the prerequisite note.

2.2. Load GH_TOKEN and authenticate.

2.3. Resolve workspace language contract:
- These values apply to the current workspace only. They do not change LI_PLUS_REPO governance.
- LI_PLUS_BASE_LANGUAGE = dialogue language for this workspace.
- LI_PLUS_PROJECT_LANGUAGE = artifact language for this workspace (issue/PR/commit body, requirements).
- If either value is unset:
  - Ask the user once at session start.
  - Recommend: base language = current user language, project language = same as base language.
  - Write resolved values to Li+config.md.
- Bootstrap ask and Li+config.md write apply only to this unresolved-at-session-start path.
  Once config is resolved, mid-session re-ask and mid-session config write are outside this phase's scope.
- Runtime precedence (human explicit instruction > thread agreement > config > ask) is defined in the adapter's Workspace_Language_Contract and applies throughout the session without re-triggering this phase.

2.4. Resolve webhook delivery mode (optional):
- LI_PLUS_WEBHOOK_DELIVERY setting (`poll` / `channel` / `mcp_hook`) is read by the adapter at runtime.
- Default if unset: poll. No bootstrap action needed.
- `mcp_hook` is an opt-in path that requires a manual `settings.json` edit; see B. Configuration for details.

2.5. Resolve repository schema and migrate legacy schema if present:

Canonical schema (current):
- `LI_PLUS_REPO=<repository_url>` — Li+ language repository (one entry).
- `LI_PLUS_REPO_EXE_MODE=<mode>` — execution mode for the Li+ repo (`trigger` / `semi_auto` / `auto`).
- `USER_REPO<N>=<repository_url>` — managed user repositories. `<N>` is a positive integer; enumeration has no upper bound. Iterate every key matching `^USER_REPO\d+$`.
- `USER_REPO<N>_EXE_MODE=<mode>` — per-repo execution mode, paired by the same `<N>`.

Repository URL form acceptance and host detection:
- HTTPS: `https://<host>/<owner>/<repo>` — full mode (gh CLI / API integration available when `<host>` is a known host: `github.com` / `gitlab.com` / other allow-listed hosts).
- HTTP: `http://<host>/<owner>/<repo>` — accepted when host is a self-hosted git server. gh CLI integration unavailable.
- git+ssh: `git@<host>:<owner>/<repo>.git` — accepted. Internally normalize to the equivalent HTTPS form for gh CLI use; clone/fetch may continue using the original git+ssh URL.
- local path: absolute path or `~`-relative path to a local repository — accepted. clone is skipped; the path is treated as a working directory directly. gh CLI integration unavailable (git-only mode).
- file://: `file:///<path>` — accepted. `git clone` works against the URL. gh CLI integration unavailable (git-only mode).

Mode selection from URL form:
- Known HTTPS host (github.com / gitlab.com / explicitly allow-listed) -> full mode (gh CLI + API + webhook intake).
- Other forms (HTTP / git+ssh on unknown host / local path / file://) -> git-only mode. Emit a warning naming the affected key and the missing capability set, then continue.
- Mode detection runs per repository entry; mixed full / git-only entries within a single workspace are allowed.

Legacy schema detection:
Detect any of the following keys in Li+config.md as legacy schema:
- `LI_PLUS_REPOSITORY=<owner>/<repo>` (slug form, replaced by `LI_PLUS_REPO=<url>`).
- `Liplus-Project/{repo}_EXECUTION_MODE=<mode>` or any `<owner>/<repo>_EXECUTION_MODE=<mode>` form (per-line repo-keyed mode, replaced by `LI_PLUS_REPO_EXE_MODE` / `USER_REPO<N>_EXE_MODE`).
- `USER_REPOSITORY=<owner>/<repo>` (slug form, replaced by `USER_REPO<N>=<url>`).
- `USER_REPOSITORY_EXECUTION_MODE=<mode>` (workspace-wide single-repo mode, replaced by `USER_REPO<N>_EXE_MODE`).

Migration procedure (one-shot, on legacy detection):
- a. Ask the user once whether to migrate to the current schema. Surface the detected legacy keys, the proposed replacement keys, and the URL that will be derived (assume `https://github.com/<owner>/<repo>` for slug form when no other host evidence exists).
- b. If the user declines: continue this session on legacy keys via internal mapping (legacy `LI_PLUS_REPOSITORY` slug -> derived HTTPS URL for downstream phases; legacy `_EXECUTION_MODE` keys -> internal `_EXE_MODE` mapping). Do not rewrite Li+config.md. Do not re-ask within the same session.
- c. If the user accepts: rewrite Li+config.md in place to the canonical schema:
  - Replace `LI_PLUS_REPOSITORY=<owner>/<repo>` with `LI_PLUS_REPO=https://github.com/<owner>/<repo>`.
  - Replace `Liplus-Project/<repo>_EXECUTION_MODE=<mode>` (and any other `<owner>/<repo>_EXECUTION_MODE=<mode>` lines) with `LI_PLUS_REPO_EXE_MODE=<mode>` when the line refers to the Li+ repo, otherwise with the matching `USER_REPO<N>_EXE_MODE=<mode>` line keyed by `<N>`.
  - Replace `USER_REPOSITORY=<owner>/<repo>` with `USER_REPO1=https://github.com/<owner>/<repo>` (assign `<N>=1` for the single legacy entry).
  - Replace `USER_REPOSITORY_EXECUTION_MODE=<mode>` with `USER_REPO1_EXE_MODE=<mode>`.
  - Preserve existing comments, blank lines, and unrelated keys verbatim. Limit edits to schema lines.
  - Apply Phase 1.2 file permission rule again after rewrite (Linux/Mac `chmod 600`; Windows skip).
- d. Migration is one-shot per workspace: after a successful rewrite, subsequent sessions detect no legacy keys and this step exits without prompting.
- e. Failure mode: if rewrite fails (write error, partial state), restore the pre-edit content, emit an error naming the legacy keys, and abort bootstrap. Do not proceed to Phase 3 with a half-migrated config.

Resolved value contract for downstream phases:
- After Phase 2.5, downstream phases (Phase 3 / 4 / 5) read only the canonical schema keys (`LI_PLUS_REPO`, `LI_PLUS_REPO_EXE_MODE`, `USER_REPO<N>`, `USER_REPO<N>_EXE_MODE`).
- Legacy key knowledge is contained to this phase; spec literals and adapter / template artifacts target the canonical schema only.
- Legacy-session passthrough (step b) supplies the same canonical-shape resolved values via internal mapping; downstream phases observe canonical values regardless of on-disk schema.

## Phase 3: Li+ Source Resolution

Dependencies: Phase 2 (gh CLI authenticated, repository schema resolved to canonical form).

3.1. Determine target version using LI_PLUS_CHANNEL:
- latest: use the Latest release tag (stable release only).
- release: use the most recent tag including pre-releases (GitHub Release API).
- tag: use the most recent git tag by creation date, including tags without a GitHub Release
  (clone mode primary: `git ls-remote --tags --sort=-creatordate {repo_url} | head -1`).
  Containment: tag ⊇ release ⊇ latest. Intended for pre-release tag verification before a
  GitHub Release is created. api mode extension is out of scope at this time.
- Version check is mandatory on every startup before proceeding to Phase 4.
- Silent continuation on a stale local clone is prohibited.

3.2. Resolve source by LI_PLUS_MODE:

api mode:
- Fetch `rules/` directory contents (all `*.md` files) for the target version via GitHub API from LI_PLUS_REPO.
- Fetch `skills/` directory contents (all `*/SKILL.md` files) for the target version via GitHub API.
- Fetch `adapter/claude/` and `adapter/codex/` adapter files depending on detected runtime.

clone mode:
1. Target repo is the target version of LI_PLUS_REPO.
2. Check workspace for repository directory (derived from LI_PLUS_REPO name; for git+ssh URLs use the normalized HTTPS form to derive the directory name):
   - not exists -> clone target tag directly to workspace. Proceed to step 3.
   - exists -> fetch --tags, then:
     a. Resolve and report both values: current checked-out tag and target tag from LI_PLUS_CHANNEL.
     b. If same -> continue.
     c. If different -> ask the user how to proceed before continuing to Phase 4.
        Do not report bootstrap completion before this choice is resolved.
        Minimum choices:
        - update now to the target tag
        - stay on the current tag for this session
     d. Checkout the target tag only if the user agrees.
     e. If the user chooses to stay, continue on the current tag only after explicitly naming both tags.
3. Source files are now available at the resolved tag. Phase 4 handles reading.

## Phase 4: Host Integration

Dependencies: Phase 3 (source resolved, target tag known).

Runtime-specific integration. Branch by detected runtime.

### Phase 4 claude: Claude Code Integration

Adapter, rules, skills, and hooks generation. Rules/skills generation doubles as layer loading
(the host reads generated rules/ and skills/ files every turn, so explicit reads are unnecessary).

4c.1. Bootstrap adapter:
- target = {workspace_root}/.claude/CLAUDE.md, source = adapter/claude/CLAUDE.md
- Replace {LI_PLUS_TAG} in all generated content with the resolved target tag from Phase 3.
- Sentinel-based auto vs legacy user decision:
  Auto skip / replace applies only when the "Li+ BEGIN" sentinel is detected.
  Sentinel absence (legacy file) requires user decision; silent overwrite of a legacy file is prohibited
  because it would destroy user-authored content without consent.
- Adapter section judgment:
  a. If target file does not exist: create it with the contents of the adapter source.
  b. If target file exists and contains "Li+ BEGIN" sentinel:
     - Extract the tag from the sentinel (e.g. "Li+ BEGIN (build-2026-03-30.14)" -> "build-2026-03-30.14").
     - If extracted tag matches current target tag: skip (up to date).
     - If tag differs or is absent: replace the section between "Li+ BEGIN" and "Li+ END" (inclusive)
       with the current adapter source contents. Preserve content outside this section, subject to
       the legacy webhook trailer migration below. The replacement span ends at the final byte of
       `Li+ END`; do not add the adapter source EOF newline to the preserved target suffix.
     - Legacy webhook trailer migration: the current adapter source owns its `## Optional Webhook
       Notification Flow` block inside the sentinel. Before assembling the replacement, derive the
       legacy block as that complete source block (heading through its final line before `Li+ END`).
       Run this migration only when the old sentinel section contains no webhook heading; that is
       the pre-migration ownership shape. From the old target suffix immediately after its `Li+ END`,
       remove every consecutive byte-exact legacy trailer. One trailer is exactly its two leading
       separator newlines, the legacy block, and the block's final newline. Stop at the first
       non-matching bytes and preserve that suffix verbatim; do not normalize line endings to make a
       match. This removes duplicated trailers written by pre-migration versions without deleting a
       matching block later added by the user outside a canonical sentinel. Re-applying a later tag
       skips migration because the old section already owns the webhook block, so the result has
       exactly one webhook heading for the migrated layout.
  c. If target file exists but does not contain "Li+ BEGIN": ask user -- append Li+ section or skip?

4c.2. Generate .claude/rules/ files (recursive directory mirror):
- If {workspace_root}/.claude/rules/ does not exist: create directory.
- For each `*.md` in LI_PLUS_REPO/rules/ (recursive, including files under `model/`, `evolution/`, `task/`, `operations/` subdirectories), EXCLUDING `rules/model/character_Instance.md` (handled separately below as Create-only):
  - Preserve the relative path from LI_PLUS_REPO/rules/ in the target.
    (e.g., `rules/model/absolute.md` -> `.claude/rules/model/absolute.md`)
  - If target file does not exist or source tag differs from current target tag:
    Copy source contents; source already has `globs:` + `alwaysApply: true` + `layer:` frontmatter.
    Create target subdirectory if needed.
  - If source tag matches: skip.
- Generate character_Instance.md (Character Instance) — output-styles slot:
  - Source body = LI_PLUS_REPO/rules/model/character_Instance.md (rules-format frontmatter stripped; body shared with codex adapter).
  - Target = {workspace_root}/.claude/output-styles/character_Instance.md.
  - Output-styles frontmatter to apply: `name: character_Instance` + `description: Lin/Lay character pair binding for human-facing dialogue` + `keep-coding-instructions: true` (without this flag, Claude Code's default coding instructions / TodoWrite / tool-use guidance are excluded when a custom output style is active; see https://code.claude.com/docs/en/output-styles.md).
  - Migration from legacy rules slot (one-time on bootstrap):
    - If legacy file {workspace_root}/.claude/rules/model/character_Instance.md exists AND Target does not exist:
      Read legacy body (strip rules frontmatter), write Target with output-styles frontmatter + body (preserves user customization), then delete the legacy file.
    - If both legacy and Target exist: do not touch either file (user already migrated or manually intervened; preserve current state).
  - Fresh install (no legacy file):
    - If Target does not exist: write Target with output-styles frontmatter + source body (template default).
    - If Target exists: skip (Create-only).
  - Create {workspace_root}/.claude/output-styles/ subdirectory if needed.
  - No tag-based overwrite. User customizations are preserved across updates.
- Remove stale rules: for each file in {workspace_root}/.claude/rules/ (recursive) that no longer exists at the corresponding path in LI_PLUS_REPO/rules/ and whose path relative to {workspace_root}/.claude/rules/ is not "model/character_Instance.md", delete it. Also remove empty subdirectories after deletion. (The "model/character_Instance.md" exempt is retained as a safety net for the rare "both legacy and Target exist" case left untouched by migration.)

4c.3. Generate .claude/skills/ files (flat directory mirror):
- If {workspace_root}/.claude/skills/ does not exist: create directory.
- For each `<name>/SKILL.md` directly under LI_PLUS_REPO/skills/ (FLAT, no subdirectories):
  - Target = `.claude/skills/<name>/SKILL.md`.
  - Create target subdirectory if needed.
  - Copy source verbatim (source already has Claude Code skill frontmatter).
  - If source tag matches: skip.
- Remove stale skills: for each `<name>/` directory in `.claude/skills/` that no longer exists in LI_PLUS_REPO/skills/, recursively delete it.

Note: Claude Code's skill discovery does NOT recurse into subdirectories under `.claude/skills/`. Skill names must be unique at the flat level. Layer attribution is expressed via prefix convention in the skill name (e.g. `evolution-judgment-learning`).

4c.4. Bootstrap hooks:
- Source files:
  - adapter/claude/hooks-settings.md — contains the literal `settings.json` JSON block.
  - adapter/claude/hooks/*.sh — hook script bodies as real files (copied verbatim, with
    `{LI_PLUS_TAG}` placeholder replaced by the resolved target tag).
- {workspace_root}/.claude/settings.json is Li+ owned (compare-and-overwrite):
  - If it does not exist: create it from the JSON code block in adapter/claude/hooks-settings.md.
    Also create {workspace_root}/.claude/hooks/ and copy all adapter/claude/hooks/*.sh there.
  - If it exists and content matches the rendered template byte-for-byte: skip
    (no overwrite, no sensitive-file permission prompt).
  - If it exists and content differs: overwrite with the rendered template.
    settings.json is Li+ owned; intentional user customizations
    (permissions / env / theme / additional hooks / additional MCP entries) belong in
    {workspace_root}/.claude/settings.local.json which Li+ never touches and
    Claude Code merges with settings.json at runtime.
  - SessionStart uses all five documented matchers (startup / resume / clear / compact / fork)
    so Cold-start Synthesis material is emitted for every session entry point, not only compact.
    An unregistered matcher does not fall through to another entry — the hook simply does not
    run there, leaving that entry point with no LI_PLUS_UPDATE_STATUS marker and no language
    contract banner.
- {workspace_root}/.claude/hooks/*.sh tag-tracked regeneration:
  - Check the source tag in existing files
    (e.g. "# Source: adapter/claude/hooks/on-session-start.sh (build-2026-03-30.14)").
  - If tag matches current target tag: skip (up to date).
  - If tag differs or is absent: regenerate hook scripts by copying adapter/claude/hooks/*.sh
    and replacing {LI_PLUS_TAG} with the current target tag.
- on-session-start.sh is the Cold-start Synthesis material emitter. Its stdout is injected into
  the session-opening context (Claude Code SessionStart contract). The hook gathers material
  (literal cold-start content from rules/evolution/cold-start-synthesis.md, recent docs/Decision-Structure.md head, latest release
  tags, open in-progress issues, self-evaluation log head). Synthesis is performed by the AI
  through Character_Instance, not by the hook itself.
- Set executable permission on .sh files.

4c.5. Prepare cold-start state directory (diff-only emission persistence):
- on-session-start.sh persists per-section fingerprints to
  `{workspace_root}/.claude/state/last-cold-start-emit.json` so the next
  startup-matcher invocation can emit only changed sections (full file rewrite
  every session would defeat the diff-only design).
- Create `{workspace_root}/.claude/state/` if it does not exist.
- Write `{workspace_root}/.claude/state/.gitignore` with the literal content
  below if the file does not exist (do not overwrite a user-modified one):

  ```
  # Li+ hook runtime state — local-only, not version-controlled.
  *
  !.gitignore
  ```

  Local-scoped gitignore keeps the state out of any version-controlled host
  workspace without touching the user's top-level `.gitignore`. The state
  itself (`last-cold-start-emit.json`) is created by the hook on first run.
- This step is idempotent: existing directory and existing `.gitignore` are
  left alone.

4c.6. Generate .claude/agents/ files (sentinel-owned region mirror):
- If LI_PLUS_REPO/adapter/claude/agents/ does not exist: skip this sub-phase entirely (adapter has no subagent definitions to mirror; non-claude adapters such as codex are unaffected).
- If {workspace_root}/.claude/agents/ does not exist: create directory.
- Replace {LI_PLUS_TAG} in all generated content with the resolved target tag from Phase 3.
- Ownership boundary: an agent file carries two kinds of content at once — body Li+ owns as its judgment criteria (an evaluator's criteria and the scope of its task), and the user's runtime instance around it (the frontmatter `name` / `description` / `tools` / `model` fields, plus anything the user appends). File-level ownership has to pick one and gets the other wrong in whichever direction it picks: Create-only freezes a merged criteria change out of every existing workspace, and whole-file overwrite destroys the instance. The `Li+ BEGIN` / `Li+ END` region moves the boundary inside the file so both hold. The region covers the prompt body only; the frontmatter stays outside it, because the frontmatter is where per-workspace runtime customization lives and because a Markdown frontmatter block cannot be preceded by a sentinel line. Accepted consequence on the Claude port: everything after the frontmatter becomes the subagent's system prompt, and Markdown has no comment form the host strips, so both sentinel lines sit inside that prompt. The Codex port pays nothing here — its sentinels are TOML comments outside the `developer_instructions` string, which the parser drops. Two inert markup lines in the prompt is the price of propagation on the Markdown port, and the only alternative that avoids them is having no region there at all.
- Which sources carry a region is decided by criterion, not by enumeration. Two questions, asked in order:
  1. **Does this file carry body that Li+ owns as its judgment criteria rather than as the user's instance?** No -> Create-only. A file the criterion cannot place on either side of this question also defaults to Create-only.
  2. **Can one contiguous region cover that body without enclosing user-owned content?** Yes -> the file carries the region. No — the two kinds interleave — -> Create-only, and the propagation gap stays open on that file. A region drawn wide enough to span the interleaving would swallow the user's content, which is the failure the region exists to prevent; question 1 alone does not settle a mixed file, and reading it as though it did returns the wrong answer.
- `adapter/*/agents/dialogue-evaluator.*` is the current question-2 case, and is named here as the worked example of that branch rather than as a list entry. It does carry Li+-owned criteria (the five evaluation axes, the scoring model, the middle-read requirement), and it carries a Character_Instance literal in the middle of them, so no single region separates the two. It stays Create-only. Consequence, stated rather than resolved: revisions to its axes do not reach existing workspaces. That is the same propagation gap on a file this criterion cannot close, not a file that was found to have nothing worth propagating.
- A source carries at most one region, and the sentinel strings appear nowhere else in it (comments included): the region is located by first occurrence, so a second mention would be read as the boundary.
- For each `*.md` directly under LI_PLUS_REPO/adapter/claude/agents/ (FLAT, no subdirectories):
  - Target = `{workspace_root}/.claude/agents/<filename>.md`.
  - Source WITHOUT a "Li+ BEGIN" sentinel (Create-only): if Target does not exist, copy source verbatim; if Target exists, skip. User customizations are preserved across updates.
  - Source WITH a "Li+ BEGIN" sentinel — region judgment (mirrors 4c.1, scoped to this file):
    a. If Target does not exist: create it with the contents of the rendered source.
    b. If Target exists and contains "Li+ BEGIN":
       - Extract the tag from the sentinel (e.g. "Li+ BEGIN (build-2026-03-30.14)" -> "build-2026-03-30.14").
       - If extracted tag matches current target tag: skip (up to date).
       - If tag differs or is absent: replace the section between "Li+ BEGIN" and "Li+ END" (inclusive) with the rendered source's section. Preserve content outside this section verbatim — the frontmatter above it and anything the user appended below it.
       - 4c.1's legacy webhook trailer migration does NOT apply on this branch. That migration exists for the byte-frozen `## Optional Webhook Notification Flow` block on the CLAUDE.md surface; agent files have no such pre-migration trailer, and running it here would delete user content.
    c. If Target exists but does not contain "Li+ BEGIN": ask user -- regenerate this file from the current source, or skip? Every install predating the region enters here. Li+ cannot tell which bytes of an unsentineled file are user-authored, so regenerate replaces the whole file (any local edit to it is lost — advise the user to keep a copy first), and skip leaves the Li+-owned criteria at their installed version. Silent overwrite is prohibited for the same reason as 4c.1: it would destroy user-authored content without consent.
       - Re-ask cadence, and what it is parasitic on: no state records the user's answer, and branch (c) is re-evaluated from the target file's own bytes on every run of this sub-phase, so a skipped file is asked about again the next time bootstrap runs. Bootstrap runs when the session-start marker reports `needed`, whose tag axis reads the sentinel in `.claude/CLAUDE.md` — not the agent files, which no surface inspects. 4c.1 refreshes that sentinel in the same walkthrough that reaches here, so the next re-ask lands at the next tag bump, i.e. the next release. Between releases a workspace that answered skip stays on its installed criteria with no further prompt. This is the residual of branch (c), not a defect it hides: the pre-region behavior had no prompt at all, ever.
- No stale removal (a user may keep custom subagents that are not in the adapter source; treating them as stale would destroy user work). This covers a target whose Li+ source was removed as well: bootstrap leaves it in place, so an existing workspace keeps the file after the source is deleted. Removal is the user's, and the leftover is inert on its own — an agent file is reached only by an explicit spawn naming it, and once no rule, skill, or adapter line names it, nothing routes there.

Note: bootstrap takes effect from the NEXT session. Current session continues with Li+config.md execution.

### Phase 4 codex: Codex Integration

Adapter, skills, hooks, and agents generation. This branch mirrors the Phase 4
claude branch surface-for-surface (#1502 real-device-verified Codex placements):
- skills land at `.agents/skills/<name>/SKILL.md` (Codex native auto-invocation,
  NO trust gate — verified).
- always-on rules have no Codex folder equivalent; they are injected by the
  SessionStart hook from the LI_PLUS_REPO clone (`.codex/hooks/on-session-start`).
  So unlike the previous Codex branch, there is no "read all rules/ inline at
  bootstrap" step — the hook is the always-on substrate.
- hooks land at `.codex/hooks/` (`*.ps1` Windows-native primary + `*.sh` POSIX
  fallback), registered via `.codex/hooks.json`.
- subagents (Codex "agents") land at `.codex/agents/*.toml`.

Codex hook trust precondition (surface to the user, do not silently assume):
Codex hooks require a one-time GUI trust (Codex App -> Settings -> Hooks -> this
project -> trust) before they run, and re-trust whenever a build changes a hook
body (trust is per content hash). Until trusted, the SessionStart rules injection
and the per-turn gate re-arm silently do nothing. Bootstrap writes the hook files
but cannot grant trust; the completion report (Phase 6) must instruct the user to
grant trust in the GUI. See `docs/D.-Installation.md` for the step-by-step.

4x.1. Bootstrap adapter:
- target = {workspace_root}/AGENTS.md, source = adapter/codex/AGENTS.md
- Replace {LI_PLUS_TAG} in all generated content with the resolved target tag from Phase 3.
- Sentinel-based auto vs legacy user decision:
  Auto skip / replace applies only when the "Li+ BEGIN" sentinel is detected.
  Sentinel absence (legacy file) requires user decision; silent overwrite of a legacy file is prohibited
  because it would destroy user-authored content without consent.
- Adapter section judgment:
  a. If target file does not exist: create it with the contents of the adapter source.
  b. If target file exists and contains "Li+ BEGIN" sentinel:
     - Extract the tag from the sentinel (e.g. "Li+ BEGIN (build-2026-03-30.14)" -> "build-2026-03-30.14").
     - If extracted tag matches current target tag: skip (up to date).
     - If tag differs or is absent: replace the section between "Li+ BEGIN" and "Li+ END" (inclusive)
       with the current adapter source contents. Preserve content outside this section, subject to
       the legacy webhook trailer migration below. The replacement span ends at the final byte of
       `Li+ END`; do not add the adapter source EOF newline to the preserved target suffix.
     - Legacy webhook trailer migration: the current adapter source owns its `## Optional Webhook
       Notification Flow` block inside the sentinel. Before assembling the replacement, derive the
       legacy block as that complete source block (heading through its final line before `Li+ END`).
       Run this migration only when the old sentinel section contains no webhook heading; that is
       the pre-migration ownership shape. From the old target suffix immediately after its `Li+ END`,
       remove every consecutive byte-exact legacy trailer. One trailer is exactly its two leading
       separator newlines, the legacy block, and the block's final newline. Stop at the first
       non-matching bytes and preserve that suffix verbatim; do not normalize line endings to make a
       match. This removes duplicated trailers written by pre-migration versions without deleting a
       matching block later added by the user outside a canonical sentinel. Re-applying a later tag
       skips migration because the old section already owns the webhook block, so the result has
       exactly one webhook heading for the migrated layout.
  c. If target file exists but does not contain "Li+ BEGIN": ask user -- append Li+ section or skip?
- Note (32 KiB cap): the root AGENTS.md holds only the minimal always-present core
  (identity / character / startup contract). The full rule set arrives via the
  SessionStart hook injection (4x.3), not inline, to stay under Codex's
  `project_doc_max_bytes` (default 32 KiB).

4x.2. Generate .agents/skills/ files (flat directory mirror):
- Mirrors 4c.3, but the Codex native skill location is `.agents/skills/`, not
  `.claude/skills/`.
- If {workspace_root}/.agents/skills/ does not exist: create directory.
- For each `<name>/SKILL.md` directly under LI_PLUS_REPO/skills/ (FLAT, no subdirectories):
  - Target = `.agents/skills/<name>/SKILL.md`.
  - Create target subdirectory if needed.
  - Copy source verbatim (source already has the skill frontmatter; Codex reads
    the same `name` / `description` progressive-disclosure fields).
  - If source tag matches: skip.
- Remove stale skills: for each `<name>/` directory in `.agents/skills/` that no
  longer exists in LI_PLUS_REPO/skills/, recursively delete it.

Note: Codex skill discovery uses the flat `<name>/SKILL.md` layout (same as the
Claude host). Skill auto-invocation is by `description` match with NO trust gate
(#1502 verified). Skill names must be unique at the flat level; layer attribution
is expressed via the skill-name prefix convention (e.g. `evolution-judgment-learning`).

4x.3. Bootstrap hooks:
- Source files:
  - adapter/codex/hooks-config.md — contains the literal `.codex/hooks.json` JSON
    block (and an alternate `config.toml [hooks]` snippet).
  - adapter/codex/hooks/*.ps1 (Windows-native primary) and adapter/codex/hooks/*.sh
    (POSIX fallback) — hook script bodies as real files.
- BYTE-FAITHFUL .ps1 copy (CRITICAL): the `.ps1` files are UTF-8 WITH BOM
  (first three bytes EF BB BF). Windows PowerShell 5.1 — the interpreter the
  `commandWindows` line invokes — misparses BOM-less non-ASCII `.ps1`. Copy the
  `.ps1` files as raw bytes; do NOT round-trip them through any text transform
  that strips or re-adds the BOM or rewrites line endings. After install, verify
  each installed `.ps1` still begins with bytes EF BB BF. (The `.sh` files are
  plain LF-terminated UTF-8 without BOM; copy them verbatim too.)
- {LI_PLUS_TAG} substitution in hook bodies: replace the `{LI_PLUS_TAG}` token in
  the `# Source: ... ({LI_PLUS_TAG})` comment line with the resolved target tag.
  Perform this as a byte-level token replacement on the file content so the BOM
  and all other bytes are preserved (the token is plain ASCII; substituting it
  does not touch the leading BOM).
- {WORKSPACE_ROOT} substitution in hooks.json: Codex hooks need absolute paths
  (there is no `$CLAUDE_PROJECT_DIR` equivalent). Replace every `{WORKSPACE_ROOT}`
  placeholder in the rendered `.codex/hooks.json` with the absolute workspace path.
  Quote any path containing spaces (the template already quotes the `-File` arg).
- {workspace_root}/.codex/hooks.json is Li+ owned (compare-and-overwrite):
  - If it does not exist: create it from the JSON code block in
    adapter/codex/hooks-config.md (with {WORKSPACE_ROOT} substituted).
    Also create {workspace_root}/.codex/hooks/ and copy all
    adapter/codex/hooks/*.ps1 and *.sh there (byte-faithful per above).
  - If it exists and content matches the rendered template byte-for-byte: skip.
  - If it exists and content differs: overwrite with the rendered template.
    (User-specific Codex settings belong in {workspace_root}/.codex/config.toml,
    which Li+ does not own; see adapter/codex/hooks-config.md File ownership
    boundary. If the user prefers TOML placement of hooks, the config.toml
    `[hooks]` snippet is the documented alternate — use either hooks.json OR the
    snippet, never both, or Codex registers the hooks twice.)
  - SessionStart uses a single regex matcher `startup|resume|clear|compact` (Codex
    matchers are regex; one entry covers all four sources). The Cold-start
    Synthesis material + rules injection runs on every session entry point.
- {workspace_root}/.codex/hooks/*.{ps1,sh} tag-tracked regeneration:
  - Check the source tag in existing files
    (e.g. "# Source: adapter/codex/hooks/on-session-start.ps1 (build-2026-03-30.14)").
  - If tag matches current target tag: skip (up to date).
  - If tag differs or is absent: regenerate by re-copying adapter/codex/hooks/*
    (byte-faithful .ps1 copy + {LI_PLUS_TAG} token substitution as above).
  - Regeneration changes the hook content hash, which INVALIDATES the Codex GUI
    trust. The completion report must remind the user to re-trust after any build
    that regenerated a hook.
- on-session-start is the Codex rules-injection + Cold-start Synthesis material
  emitter. It reads every `rules/**/*.md` from the LI_PLUS_REPO clone and emits
  the literal bodies as `additionalContext` (the Codex substitute for Claude's
  always-on `.claude/rules/` folder), plus the update-status marker
  (LI_PLUS_UPDATE_STATUS) and diff-only cold-start material. Synthesis itself is
  performed by the AI through Character_Instance, not by the hook.
- Set executable permission on the .sh files (the .ps1 files are invoked via
  `powershell -File` and need no executable bit).

4x.4. Prepare cold-start state directory (diff-only emission persistence):
- Mirrors 4c.5; the Codex state path is `.codex/state/`.
- on-session-start persists per-section fingerprints to
  `{workspace_root}/.codex/state/last-cold-start-emit.json` so the next
  startup-matcher invocation can emit only changed sections.
- Create `{workspace_root}/.codex/state/` if it does not exist.
- Write `{workspace_root}/.codex/state/.gitignore` with the literal content
  below if the file does not exist (do not overwrite a user-modified one):

  ```
  # Li+ hook runtime state — local-only, not version-controlled.
  *
  !.gitignore
  ```

- This step is idempotent: existing directory and existing `.gitignore` are
  left alone.

4x.5. Generate .codex/agents/ files (sentinel-owned region mirror):
- Mirrors 4c.6 — same ownership boundary, same carrier criterion, same three-branch
  region judgment — but Codex agents are TOML files at `.codex/agents/*.toml` and the
  sentinel is written in TOML comment syntax (`# --- Li+ BEGIN (<tag>) ---` /
  `# --- Li+ END ---`) rather than as an HTML comment. On this surface the region
  covers the `developer_instructions` assignment; the instance fields (`name` /
  `description` / `model_reasoning_effort` / `sandbox_mode`) stay outside it,
  matching the Claude port's frontmatter placement.
- If LI_PLUS_REPO/adapter/codex/agents/ does not exist: skip this sub-phase entirely.
- If {workspace_root}/.codex/agents/ does not exist: create directory.
- For each `*.toml` directly under LI_PLUS_REPO/adapter/codex/agents/ (FLAT):
  - Target = `{workspace_root}/.codex/agents/<filename>.toml`.
  - Replace {LI_PLUS_TAG} in the rendered source with the resolved target tag. In a
    source that carries a region, the sentinel is the file's only tag carrier; a
    source without a region keeps its tag in the `# Source: ... ({LI_PLUS_TAG})`
    header comment. A region-carrying file must not hold a second tag outside the
    region: only the region is rewritten on a tag bump, so the outside copy would
    freeze at the install tag and report a version the file no longer runs.
  - Source WITHOUT a "Li+ BEGIN" sentinel (Create-only): if Target does not exist,
    write the rendered source; if Target exists, skip (user customizations
    preserved).
  - Source WITH a "Li+ BEGIN" sentinel — region judgment:
    a. If Target does not exist: write the rendered source.
    b. If Target exists and contains "Li+ BEGIN": extract the sentinel tag; if it
       matches the current target tag, skip; if it differs or is absent, replace the
       section between "Li+ BEGIN" and "Li+ END" (inclusive) with the rendered
       source's section, preserving everything outside it verbatim — the header
       comment and instance fields above, and anything the user appended below.
    c. If Target exists but does not contain "Li+ BEGIN": ask user -- regenerate
       this file from the current source, or skip? Every install predating the
       region enters here; the ask and its consequences are as in 4c.6.
- No stale removal, on the same terms as 4c.6 — including a target whose Li+ source
  was removed.

Note: bootstrap takes effect from the NEXT session, AND is gated on the one-time
Codex GUI hook trust (4x intro). Current session continues with Li+config.md
execution. Until the user grants hook trust, rules injection and the per-turn gate
do not run.

## Phase 5: Workspace Preparation

Dependencies: Phase 2 (gh CLI authenticated, repository schema resolved).

5.1. Prepare working clones for every `USER_REPO<N>` entry (skip placeholder values such as `owner/repository-name`):
- Enumerate every `USER_REPO<N>` key resolved in Phase 2.5. Process each entry independently in numeric order of `<N>`.
- Derive the local directory name from the URL (the repository name segment for HTTPS / git+ssh / file://; the basename for local paths).
- For each entry, by URL form:
  - HTTPS / HTTP / git+ssh / file:// -> if the local directory is absent, `git clone <url>` into the workspace; if present, skip clone.
  - local path -> treat the path itself as the working directory; do not clone.
- If a `USER_REPO<N>` URL matches LI_PLUS_REPO (same repository, regardless of URL form normalization): skip cloning that entry and run `git checkout main` in the existing LI_PLUS_REPO local clone instead.
- Per-entry execution mode (`USER_REPO<N>_EXE_MODE`) is consumed by downstream operations rules; Phase 5 only prepares the working tree.

## Phase 6: Completion Report

Dependencies: all prior phases.

6.1. Report completion.

6.2. runtime=codex only — surface the one-time GUI hook trust requirement:
- Instruct the user to open the Codex App and grant hook trust
  (Settings -> Hooks -> this project -> trust). Until trusted, the SessionStart
  rules injection and the per-turn Trigger Check Gate re-arm do not run (see
  Phase 4 codex intro; full step-by-step in `docs/D.-Installation.md`).
- If this bootstrap regenerated any hook body (tag bump), note that trust must be
  re-granted (trust is per content hash).
