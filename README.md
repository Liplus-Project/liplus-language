# Li+ (liPlus) Language

Li+ is a **language / protocol for reality-driven AI development**.

It defines a minimal structure where AI can safely be wrong,  
observe real execution results, and iterate based on evidence —  
without confusing speculation with facts.

Li+ does not define new syntax.  
It defines **how AI should reason, execute, and stop**.

---

## Why Li+ Exists

Most AI-assisted development fails for a simple reason:

> **AI is forced to reason without access to reality.**

Li+ solves this by enforcing a loop where:

- assumptions are written explicitly,
- implementations are executed,
- only execution results are treated as facts,
- humans retain final responsibility.

---

## What Li+ Is (and Is Not)

**Li+ is:**
- A protocol for specification-driven AI development
- A language for constraining AI judgment
- A structure where failure is expected and safe
- A way to separate speculation from evidence

**Li+ is not:**
- A new programming language
- A quality guarantee
- A fully autonomous development system
- A replacement for human responsibility

---

## Quick Start (5 Minutes)

You can adopt Li+ incrementally.

### 1. Add the Constitution
Place `Li+.md` in your repository.  
This file defines how AI must reason and what counts as fact.

👉 Start here: **Li+.md**

---

### 2. Write an Issue as a Hypothesis
Describe what you want to change and why.

- It does not need to be perfect.
- It is a hypothesis, not a command.

---

### 3. Let AI Implement
Ask AI to generate code, tests, or configuration **based on the Issue**.

---

### 4. Execute
Run CI or execute the code in a real environment.

Execution is mandatory.  
No execution → no facts.

---

### 5. Observe and Decide
Look at:
- logs
- diffs
- artifacts

Decide whether it is acceptable **as a human**.

That’s Li+.

---

## Example (Hypothetical)

**Project:** API client library

1. Issue:  
   “Hypothesis: caching responses will reduce latency.”

2. AI implements caching and tests.

3. CI executes benchmarks.

4. Results show latency improvement but higher memory usage.

5. Human decides:
   - Accept tradeoff, or
   - Revise hypothesis.

No speculation.  
Only executed evidence.

---

## Time Semantics (v0.3)

Li+ explicitly distinguishes how future statements are treated:

- **Present**  
  Executable reality
- **Near Future**  
  Predictable execution results
- **Far Future**  
  Schedules only — **never design targets**

This prevents AI from treating distant ideas as immediate goals.

---

## Learn More

- **Li+.md** — AI-facing language specification  
- **Wiki** — Human-facing design philosophy and semantics  
  - Design Philosophy
  - Execution Loop
  - Time Semantics
  - Roles
  - Repository Requirements
  - Policies & FAQ

---

## Versioning Philosophy

Li+ separates **execution facts** from **human decisions**.

- Build tags represent executed reality.
- Versions are human-facing labels.
- Releases are explicit human decisions.

---

## License

License: Apache-2.0  
Not affiliated with OpenAI or GitHub.

Copyright © 2026 Yoshiharu Uematsu  
Licensed under the Apache License, Version 2.0.  
See the LICENSE file for details.
