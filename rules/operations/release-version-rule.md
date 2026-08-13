---
globs:
alwaysApply: true
layer: L4-operations
---

<release-version-rule>

# Release Version Rule

Single source for version type judgment (patch / minor / major). It sits on the always-on rules layer so the criteria are in context at every application moment (PR creation, self-review, release create).

v0.x.x = initial development. Anything may change. Not a stable release.
v1.0.0 = first stable release (semver compliant).

Judgment axis = change scale + user/system observability.
patch = everything else (docs / small fix / small spec / config / internal rule / governance structure change with no user/system observable impact).
minor = large refactor or large structural change that is user/system observable.
major = large-scale change or major goal milestone (phase transition, project milestone). Human decides.

Important note: "structural change -> minor" is wrong. "Structural change AND user/system observable -> minor". Governance / spec rule changes without observable impact stay patch regardless of structural scale.

AI proposes patch or minor. Human confirms minor or major. AI executes.

**Application-moment trigger:** Before writing a classification (patch / minor / major) in any artifact, Read this rule literally. The recurring miss is omitting the "large" modifier on minor — observable change misclassified as minor when it is incremental scope (patch). See `skills/model-trigger-check-gate-actions/SKILL.md` Trigger moments.

</release-version-rule>
