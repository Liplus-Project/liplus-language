# Li+ (liPlus) Language

Li+ is the **highest-level programming language**.

`Li+ program` is the **execution system of that language**, running on top of AI agents.

`Li+AI` is an AI agent with `Li+ program` applied; it functions as an **interactive compiler**.

"Highest-level" means it sits above high-level languages and above one-shot prompts.

```text
Human requirements
↓
Li+ language (requirement specification)
↓
Li+AI / Li+ program (interactive compiler / execution system)
↓
AI agent (Codex / Claude Code / Devin / etc.)
↓
Programming language (Python / Rust / TypeScript / etc.)
↓
Machine code
```

High-level languages like C, Python, and Rust solved *how to write code*.
`Li+ language` addresses **what should be satisfied**.
`Li+ program` governs **how an AI should prioritize, act, verify, and retry until the target program converges on those requirements**.

---

## What is Li+?

`Li+ language` does not introduce a new syntax.
It treats **requirement specifications as code**.
`Li+ language` is the description layer whose code is requirement specifications.
`Li+ program` is the execution system that runs that code on top of an AI agent.
The execution focus is not merely to help a human write code faster, but to carry fixed requirements into aligned target programs across sessions.

Humans communicate requirements in natural language.
The AI distills them into specifications, implements them, verifies them through CI, and self-corrects when possible.

Internally, **requirement threads** such as GitHub Issues function as the minimum form of code.
The smallest syntax is:

- purpose
- premise
- constraints
- completion condition

Li+ is therefore not just a prompt.
It is a layered execution model that defines:

- what counts as code
- how priorities are ordered
- how rules are re-applied across sessions
- how implementation, CI, and release flow are orchestrated

---

## Li+ Above Prompts and Agents

Prompt engineering designs an instruction.
Li+ designs the **structure that governs instructions over time**.

Agent products provide hands: file access, shell execution, web access, GitHub access.
Li+ provides the **ordering and behavioral constraints** for those hands.

| Layer | Role | Example |
|-------|------|---------|
| Connection protocol | Link AI to tools and data | MCP, Function Calling |
| Instruction file | Provide project-local notes | `AGENTS.md`, `CLAUDE.md` |
| Agent product | Execute work with tools | Codex, Claude Code, Devin |
| **Orchestration / execution protocol** | **Govern how the agent reads, acts, verifies, and retries** | **Li+** |

Li+ is not an agent product.
Li+ is not RAG.
Li+ is the behavioral and operational layer that runs on top of agents.

---

## Li+ as Layered Programming

Li+ can be viewed as **layered programming for AI behavior**.

| Layer | Role |
|-------|------|
| Requirement layer | Fix what is correct |
| Core layer | Fix invariant behavior and dialogue weighting |
| Operations layer | Fix GitHub / CI / release rules |
| Adapter layer | Inject Li+ into each runtime |

Upper layers constrain lower ones.
The goal is not more text. The goal is stable priority ordering.

This is why Li+ often works where ordinary prompts drift:
AI systems fail not only from lack of knowledge, but from **priority collisions**.

---

## Li+ Program (`Li+core.md`)

`Li+core.md` is the **first program written in the Li+ language**.

It is also the first visible part of the **Li+ program**: executable text passed to an AI so the language can be run with stable behavior.
An AI with Li+ program applied responds as either **Lin** or **Lay**.

---

## Definition of Correctness

> "But it works, so it's fine" is one of the strongest arguments in Li+.

Specifications are hypotheses. Design is prediction. Internal elegance is not correctness.

Correctness is defined solely by **observable real-world behavior**.

---

## Current Status

The practical milestone for **Li+ v1.0.0** has already been treated as achieved:
an AI-built DDNS implementation satisfied the same requirements as a human-built equivalent.

That proves Li+ can function as a highest-level language in practice.
The next phase is **generalization**:

- across different tasks
- across different AI systems
- across different runtimes
- under lighter, more portable rule sets

---

## Setup

👉 **[Installation Guide](https://github.com/Liplus-Project/liplus-language/wiki/E.-Installation)**

Simply place Li+config in your workspace, and the AI will automatically apply Li+ at session start.

---

## Documentation

👉 **Wiki**: https://github.com/Liplus-Project/liplus-language/wiki

| Setting | Description |
|---------|-------------|
| `GH_TOKEN` | GitHub Personal Access Token |
| `USER_REPOSITORY` | Target working repository |
| `LI_PLUS_MODE` | `clone` recommended |
| `LI_PLUS_CHANNEL` | `release` recommended (includes pre-releases) |
| `LI_PLUS_EXECUTION_MODE` | `trigger` (human-driven) or `auto` (AI autonomous). If not set, configured automatically at session start |

---

| Page | Description |
|------|-------------|
| [What is Li+](https://github.com/Liplus-Project/liplus-language/wiki/A.-Liplus-language_Concept) | Design philosophy and concepts |
| [Li+core](https://github.com/Liplus-Project/liplus-language/wiki/B.-Liplus_core) | Core specification (persona, behavior, priorities, task mode, Loop Safety) |
| [Operational GitHub](https://github.com/Liplus-Project/liplus-language/wiki/C.-Operational_GitHub) | Canonical issue rules and label dictionary |
| [Li+config](https://github.com/Liplus-Project/liplus-language/wiki/D.-Li+config) | Configuration reference and startup flow |
| [Installation](https://github.com/Liplus-Project/liplus-language/wiki/E.-Installation) | Quickstart setup guide |
| [Hooks Spec](https://github.com/Liplus-Project/liplus-language/wiki/F.-hooks-spec) | Claude adapter layer and runtime hook behavior |
| [Operations](https://github.com/Liplus-Project/liplus-language/wiki/G.-Operations) | Event-driven operations, milestones, labels, and discussions |

---

## Minimum Requirements

Functioning as a Li+-driven AI agent requires adequate capability.

| Model | Result | Reason |
|-------|--------|--------|
| ChatGPT 5.2 | △ | Strong reasoning, but platform limits make long commit-heavy workflows harder |
| Claude Haiku 4.5 | × | Cannot reliably apply `Li+core.md` |
| Claude Sonnet 4.6 (claude.ai) | △ | Strong for documents. Not ideal for continuous practical work |
| Claude Code Sonnet 4.6 | ○ | Strong for development work |
| CODEX GPT5.4 (desktop) | ○ | Practical for development work, but tends to over-weight structure |
| **Claude Cowork (recommended)** | **◎** | **Current recommended environment. File access, GitHub integration, and Li+config auto-apply in one place** |

**Minimum requirement: an AI roughly equivalent to Claude Sonnet 4.6 or above**

---

## Version Type Rules

| Version | Condition |
|---------|-----------|
| patch | Bug fix, configuration, or rule change |
| minor | New feature or behavior change |
| major | Breaking change or spec incompatibility |

---

## Discussions

Have a question or idea? Post it in [Discussions](https://github.com/Liplus-Project/liplus-language/discussions).

A bot is stationed there that can create and read GitHub issues on your behalf.

---

## License

License: Apache-2.0

Copyright © 2026 Yoshiharu Uematsu
Licensed under the Apache License, Version 2.0.
See the LICENSE file for details.
