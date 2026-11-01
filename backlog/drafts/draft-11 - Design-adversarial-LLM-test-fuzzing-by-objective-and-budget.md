---
id: draft-11
title: Design adversarial LLM test fuzzing by objective and budget
status: Draft
created_date: 2026-10-29 19:00
labels:
- design
- testing
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Design draft only. Explore LLM-assisted fuzzing that creatively generates user tests to break this repository. Each campaign targets a particular failure class and runs for either a fixed number of attempts or a time budget. Preserve minimal reproducible cases and use a meaningful oracle; an LLM inventing a failure claim is not proof. Keep generated material synthetic and isolated, enforce resource and egress policy, and feed confirmed failures into deterministic regression tests.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Define campaign objectives, attempt/time budgets, independent failure oracles, and reproducible case retention.
- [ ] #2 Choose an initial safe target and specify how confirmed failures become deterministic tests.
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
