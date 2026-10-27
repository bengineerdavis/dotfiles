---
id: TASK-119
title: Author the `explain-calibration` skill — whether and how much to explain
status: To Do
created_date: 2026-10-27 02:56
labels:
- planned
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Author the `explain-calibration` skill — whether and how much to
  explain.** Queued from the 2026-09-22 handoff (decisions 25, 31–33). Lives
  in ai-prompt-library, authored with skillet-authoring — this line tracks it
  here because spec.md § Writing now binds the outcome and references the
  skill for the method. The skill carries the method the spec defers: ask the
  question that sits under the most terms, not the term in front of you; ask
  a reasoning question, not a vocabulary one; infer down and verify cheaply
  with one gloss — being wrong costs one parenthesis. Compactness method:
  conclusion in one sentence, plain meaning in one clause, the consequence
  that makes it matter, evidence only if load-bearing. Optional-dependency
  discovery (decision 27): it looks for feynman-explanation and, if absent,
  asks permission to probe for an installer, else asks the user's preference;
  no preferences saved by default. Done when the skill exists in
  ai-prompt-library, passes `skillet validate` and its own evals, and is
  installed here through the machine's skill manager.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->

<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->
