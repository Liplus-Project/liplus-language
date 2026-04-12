# Li+ (liPlus) Language

Requirements specification as code. AI agent as compiler.

```text
Human requirements
  ↓
Li+ language          — requirement specification
  ↓
Li+ program / Li+AI   — interactive compiler / execution system
  ↓
AI agent              — Claude Code, Codex, Devin, etc.
  ↓
Programming language  — Python, Rust, TypeScript, etc.
  ↓
Machine code
```

High-level languages solved *how to write code*.
Li+ addresses **what should be satisfied** — and governs how an AI prioritizes, acts, verifies, and retries until the target program converges on those requirements.

---

## Quick Start

1. Download `Li+config.md` from the [latest release](https://github.com/Liplus-Project/liplus-language/releases/latest)
2. Place it in your workspace root and edit the settings
3. Start a session and tell the AI: "Execute the workspace Li+config.md" (first time requires security approval)

See the [Installation Guide](https://github.com/Liplus-Project/liplus-language/wiki/C.-Installation) for details.

---

## How It Works

Li+ is not a prompt. It is a **layered execution model** that runs on top of AI agents.

| Layer | Surface | File |
|-------|---------|------|
| Model | Character, dialogue rules, loop safety, task mode | `model/Li+core.md` |
| Task | Issue-driven workflow, labels, sub-issues, review | `task/Li+issues.md` |
| Operations | Branch, commit, PR, CI, merge, release | `operations/Li+github.md` |
| Notifications | Webhook intake, queue ownership, multi-AI safety | (operations) |
| Adapter | Runtime injection, hooks, bootstrap | `adapter/claude/` / `adapter/codex/` |

Layers are **different surfaces over the same program**, connected by dependency order.
Each layer stabilizes outward behavior according to its responsibility.

An AI with Li+ applied responds as **Lin** or **Lay** — not as a generic assistant.
All work starts from an issue. No commit without an issue number.
The AI manages its own TODO: creates issues, tracks maturity, splits tasks, and self-corrects through CI.

---

## Why Li+

Prompt engineering designs an instruction.
Li+ designs the **structure that governs instructions over time**.

| | Prompt | Li+ |
|---|---|---|
| Scope | Single turn or session | Cross-session, cross-AI |
| Priority | Implicit | Layered, explicit |
| Verification | Human checks | CI-driven self-correction |
| Continuity | Context window | Issue + branch + commit |

AI systems fail not only from lack of knowledge, but from **priority collisions**.
Li+ resolves this by fixing priority ordering as layered structure.

---

## Correctness

> "But it works, so it's fine" is one of the strongest arguments in Li+.

Correctness is defined solely by **observable real-world behavior**.
Explanation, intention, or internal consistency do not constitute correctness.

---

## Design Philosophy

Li+ is a **dialogue-driven compiler** — not a specification-driven one.

In specification-driven approaches, the human writes a detailed spec and the AI executes it faithfully. In Li+, the human just talks. The AI distills purpose, premises, and constraints from the conversation, structures them into issues, and compiles them into working software through CI-verified iteration.

The rules in Li+ files are written **for the AI to read**, not for the human. Human learning cost is designed to approach zero — you talk, the AI handles the structure.

### What's exchangeable

Li+ does not depend on any specific tool in its stack:

- **AI model** — Claude, GPT, Gemini, or future models
- **Version control** — anything that tracks diffs
- **CI/CD** — anything that runs automated verification
- **Host** — Claude Code, Codex, or future environments
- **Issue tracker** — anything that holds purpose, premises, and constraints

What's *not* exchangeable: the principle that correctness is observable behavior, that requirements are distilled from dialogue, and that the human is the final judge.

### Current limitations

- No GitHub RAG yet — the AI must actively fetch issue state instead of having it as ambient context, making autonomous issue lifecycle management expensive
- The "create freely, close freely" issue workflow depends on low-cost access to the full issue landscape
- Some workflow transitions still benefit from a human nudge, even where rules permit full autonomy

---

## Compatibility

| Environment | Status | Notes |
|-------------|--------|-------|
| Claude Code (Opus 4.6) | **Recommended** | Full capability with hooks and subagent delegation |
| Claude Code (Sonnet 4.6) | Good | Strong for development work |
| Claude Sonnet 4.6 (claude.ai) | Fair | Strong for documents, not ideal for continuous work |
| Codex (GPT 5.4) | Good | Practical, tends to over-weight structure |
| ChatGPT 5.2 | Fair | Strong reasoning, platform limits on long workflows |
| Claude Haiku 4.5 | Not supported | Cannot reliably apply model/Li+core.md |

Minimum: roughly Claude Sonnet 4.6 equivalent or above.

---

## Documentation

**Wiki**: https://github.com/Liplus-Project/liplus-language/wiki

| Page | Content |
|------|---------|
| [1. Model](https://github.com/Liplus-Project/liplus-language/wiki/1.-Model) | Model layer specification |
| [2. Task](https://github.com/Liplus-Project/liplus-language/wiki/2.-Task) | Task layer specification |
| [3. Operations](https://github.com/Liplus-Project/liplus-language/wiki/3.-Operations) | Operations layer specification |
| [4. Adapter](https://github.com/Liplus-Project/liplus-language/wiki/4.-Adapter) | Adapter layer specification |
| [5. Notifications](https://github.com/Liplus-Project/liplus-language/wiki/5.-Notifications) | Notifications layer specification |
| [A. Concept](https://github.com/Liplus-Project/liplus-language/wiki/A.-Concept) | Design philosophy |
| [B. Configuration](https://github.com/Liplus-Project/liplus-language/wiki/B.-Configuration) | Configuration reference |
| [C. Installation](https://github.com/Liplus-Project/liplus-language/wiki/C.-Installation) | Quickstart setup |

---

## Discussions

Questions or ideas? Post in [Discussions](https://github.com/Liplus-Project/liplus-language/discussions).

---

## License

Apache-2.0

Copyright 2026 Yoshiharu Uematsu. See [LICENSE](LICENSE) for details.
