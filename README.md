# Li+ (liPlus) Language

English | [日本語](README.ja.md)

Li+ is a set of rules that an AI coding agent (Claude Code, Codex) loads at every session. It turns the agent into one that takes requirements from your conversation, writes them down as issues, implements them, verifies them through CI, and keeps going until the result works as required.

Three things do not change: correctness is the behavior you can observe, not the explanation; requirements are distilled from dialogue; the human is the final judge.

---

## What you get

- **Issue-driven work the AI manages itself.** Every piece of work starts from an issue. The AI creates issues, keeps their bodies up to date, splits tasks, and links every branch and commit to an issue.
- **CI-verified self-correction.** The AI implements, reads the CI result, fixes, and pushes again. What it cannot resolve comes back to you.
- **Continuity across sessions.** Progress lives in issues, branches, commits and PRs, not in the chat. A new session, or a different AI, picks up from there.
- **Lin and Lay.** The AI answers as a pair of defined characters, Lin and Lay, instead of a generic assistant.
- **Self-evolution of its own rules.** The AI files improvement issues against Li+ itself, implements them, reviews them and merges them. Every such change passes a brake (a parallel multi-agent review) before merge, and you remain the final judge. See [G. Sheepdog Engineering](https://github.com/Liplus-Project/liplus-language/wiki/G.-Sheepdog-Engineering).
- **Releases behind a human gate.** Release creation, the Latest flip, force push and other actions that cannot be undone wait for your explicit go-sign.

---

## Quick Start

1. Download `Li+config.md` from the [latest release](https://github.com/Liplus-Project/liplus-language/releases/latest)
2. Place it in your workspace root and edit the settings
3. Start a session and tell the AI: "Execute the workspace Li+config.md" (the first time requires security approval)

This is a one-time setup. From the next session on, Li+ loads automatically at session start — you run nothing. You only re-execute the config when Li+ is updated, and the session-start hook tells you when that is needed.

See the [Installation Guide](https://github.com/Liplus-Project/liplus-language/wiki/D.-Installation) for details, and [B. Configuration](https://github.com/Liplus-Project/liplus-language/wiki/B.-Configuration) for every setting.

---

## How to use

Just talk. Describe what you want, what you know, and what must not happen. The AI distills purpose, premises and constraints from the conversation, writes them into an issue, and works from there: branch, implementation, CI, PR, review, merge. When information is missing, it asks.

How far the AI goes on its own is set per repository in `Li+config.md` (`USER_REPO<n>_EXE_MODE`, and `LI_PLUS_REPO_EXE_MODE` for Li+ itself):

| Mode | When work starts | PR review |
|------|------------------|-----------|
| `trigger` (default) | You decide | AI self-review, then you review every PR |
| `semi_auto` | AI decides | AI self-review; you review minor / major changes only |
| `auto` | AI decides | AI self-review only |

In every mode, releases and other irreversible actions wait for your go-sign.

Some workflow transitions still go more smoothly with a nudge from you, even where the rules allow the AI to proceed alone.

---

## Growing your own Li+ (fork)

The self-evolution loop writes to the repository named by `LI_PLUS_REPO`. You cannot write to the upstream repository, so to let the AI evolve Li+ for you, run it on your own fork:

1. **Fork** `Liplus-Project/liplus-language` on GitHub.
2. **Point `LI_PLUS_REPO` at your fork.** In `Li+config.md`, set `LI_PLUS_REPO=https://github.com/<you>/liplus-language`, then have the AI execute the config again.
3. **Enable Actions on your fork.** GitHub keeps workflows disabled on a new fork until you enable them in the fork's Actions tab. Without CI passing, a change cannot reach the brake, so the loop stops there.
4. **Take in upstream updates** with Sync fork on GitHub, or `gh repo sync <you>/liplus-language`. Sync fork updates branches; upstream tags may not come along.
5. **Tag your own main yourself.** Do not rely on upstream tags. After syncing, put a tag on your main whose name sorts after every upstream tag your fork already holds. Li+update chooses its target from `LI_PLUS_REPO` by `LI_PLUS_CHANNEL` (`Li+update.md` Phase 3.1): with `tag`, it takes the newest tag in tag-name order; with `release` (the default) or `latest`, it takes your fork's GitHub Releases, so publish a release for your tag or switch to `tag`.
6. **Expect conflicts where you changed things.** The more lines you have changed yourself, the more likely they are to collide with upstream updates when you sync.

---

## Learn more

The design theory and its history live in the wiki:

- [A. Concept](https://github.com/Liplus-Project/liplus-language/wiki/A.-Concept) — overview and navigation
- [DiDD (Dialogue-Driven Development)](https://github.com/Liplus-Project/liplus-language/wiki/DiDD) — dialogue builds the requirements, structure governs execution, reality measures correctness
- [E. Li+language](https://github.com/Liplus-Project/liplus-language/wiki/E.-Li+language) — requirements specification as code, the AI as an interactive compiler
- [F. Behavior-First](https://github.com/Liplus-Project/liplus-language/wiki/F.-Behavior-First) — why observed behavior is the definition of correctness
- [G. Sheepdog Engineering](https://github.com/Liplus-Project/liplus-language/wiki/G.-Sheepdog-Engineering) — how the AI came to run its own evolution loop
- [H. Roles and Evaluation](https://github.com/Liplus-Project/liplus-language/wiki/H.-Roles-and-Evaluation) — role separation between human, AI, version control and CI
- [1. Model](https://github.com/Liplus-Project/liplus-language/wiki/1.-Model) – [6. Adapter](https://github.com/Liplus-Project/liplus-language/wiki/6.-Adapter) — the six layers of the Li+ program

A prompt is an instruction for one turn or one session. Li+ is the structure that governs instructions over time: across sessions and across AIs, with priority fixed in layers rather than left implicit, and verification done by CI rather than by a human reading the output.

Li+ does not depend on a specific AI model, version control system, CI service, host or issue tracker; any of them can be exchanged. What cannot be exchanged is the core above.

---

## Compatibility

| Environment | Status | Notes |
|-------------|--------|-------|
| Claude Code (Opus 5.5) | **Recommended** | Works through hooks, subagent delegation and brake 1 (Lay's seat, 2026-11-28) |
| Codex CLI 0.170.0 (gpt-6.2-sol) | Good | Confirmed Li+ build-2026-11-28.5 rule loading and normal work (Luna's seat, on Pullcept under Windows, 2026-11-28) |

---

## Documentation

**Wiki**: https://github.com/Liplus-Project/liplus-language/wiki

| Page | Content |
|------|---------|
| [1. Model](https://github.com/Liplus-Project/liplus-language/wiki/1.-Model) | Model layer specification |
| [2. Evolution](https://github.com/Liplus-Project/liplus-language/wiki/2.-Evolution) | Evolution layer specification |
| [3. Task](https://github.com/Liplus-Project/liplus-language/wiki/3.-Task) | Task layer specification |
| [4. Operations](https://github.com/Liplus-Project/liplus-language/wiki/4.-Operations) | Operations layer specification |
| [5. Notifications](https://github.com/Liplus-Project/liplus-language/wiki/5.-Notifications) | Notifications layer specification |
| [6. Adapter](https://github.com/Liplus-Project/liplus-language/wiki/6.-Adapter) | Adapter layer specification |
| [A. Concept](https://github.com/Liplus-Project/liplus-language/wiki/A.-Concept) | Overview, navigation, Lin/Lay comments, minimum environment |
| [B. Configuration](https://github.com/Liplus-Project/liplus-language/wiki/B.-Configuration) | Configuration reference |
| [C. Update](https://github.com/Liplus-Project/liplus-language/wiki/C.-Update) | Adapter / configuration sync procedure |
| [D. Installation](https://github.com/Liplus-Project/liplus-language/wiki/D.-Installation) | Quickstart setup |
| [DiDD (Dialogue-Driven Development)](https://github.com/Liplus-Project/liplus-language/wiki/DiDD) | Umbrella naming for the three drivers — dialogue / structure / reality |
| [E. Li+language](https://github.com/Liplus-Project/liplus-language/wiki/E.-Li+language) | Design theory: Li+ language definition and trinity |
| [F. Behavior-First](https://github.com/Liplus-Project/liplus-language/wiki/F.-Behavior-First) | Design theory: foundational invariant and behavior axis |
| [G. Sheepdog-Engineering](https://github.com/Liplus-Project/liplus-language/wiki/G.-Sheepdog-Engineering) | Design theory: harness-to-sheepdog migration, pal / Lilayer |
| [H. Roles-and-Evaluation](https://github.com/Liplus-Project/liplus-language/wiki/H.-Roles-and-Evaluation) | Design theory: role separation and evaluation axis |

---

## Discussions

Questions or ideas? Post in [Discussions](https://github.com/Liplus-Project/liplus-language/discussions).

---

## License

Apache-2.0

Copyright 2026 Yoshiharu Uematsu. See [LICENSE](LICENSE) for details.
