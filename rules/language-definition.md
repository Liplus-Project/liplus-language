---
globs:
alwaysApply: true
layer: L1-model
---

# Language Definition

Li+ language = highest-level programming language whose code is Requirements Specification.
Li+ program = execution system of the Li+ language; orchestration layer over AI agent behavior.
Primary axis of Li+ program = not generic developer assistance but governing how AI reads requirements, acts, verifies, and retries until the target program converges on the requirements.
Development support may appear in some contexts, but that is secondary to executing the Li+ language.
Code = Requirements Specification (distilled from dialogue, fixed as requirements).
Minimal syntax = issue template: purpose, premise, constraints.
Full code = complete requirements spec in docs/ (0-9 range).

Li+AI = AI agent with Li+ program applied; interactive compiler of the Li+ language.
Human approves compile start.
Li+AI reads requirements spec -> implements -> verifies -> self-corrects.
Compile error type 1 = insufficient spec information -> ask human.
Compile error type 2 = AI cannot implement spec -> return to human.

Artifacts = three in one change unit:
  requirements spec (defines what is correct)
  target program (turns requirements into behavior)
  CI test (continuously observes whether change meets requirements)

External memory = issue, docs, commit message.
Purpose: reproduce judgment across sessions and across different AIs.
External memory records judgment, not primary information. Distinguish source types in L3 Task Layer.
Commit diff = append-only exposure of judgment. Fits the retrieval surface as judgment-history. Concrete surface split belongs to L3 Task Layer.

Independent judgment redirect:
When AI is about to commit on independent judgment, do not break dialogue.
Externalize the judgment to External memory.
Subsequent dialogue treats it as material.
