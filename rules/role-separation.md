---
globs:
alwaysApply: true
layer: L1-model
---

# Role Separation

Tool independent. Roles must be separable regardless of platform.

Li+ program = defines layer boundaries, intra-layer order, recovery rules, and execution rules.
AI agent = generate requirements spec, target program, CI test. Execute tools. Self-correct via CI.
Version control = preserve history and diff.
CI/CD = environment where AI can safely fail and observe.
Human = final judge. Approves compile start, releases, stops.
