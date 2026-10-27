---
id: TASK-228
title: Audit the three filled-in old-style root `tasks.yaml` files the A9 sweep
status: To Do
created_date: 2026-10-27 02:59
labels:
- planned
- group:refactor-b-factor-the-ai-llm-tooling-out-of-this-repo
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Audit the three filled-in old-style root `tasks.yaml` files the A9 sweep
  left behind. starship (169 lines), zim (111) and ollama (281) carry
  pre-roles-migration task bodies that nothing loads; the A9 sweep deleted
  the boilerplate and verified duplicates but left these three because
  their content may not have been fully absorbed by the migration —
  starship's Fira Code font install is the visible example. Done when each
  file's content is either confirmed absorbed by the topic's `tasks/`
  lifecycle files (and the file deleted) or the missing pieces are moved
  into the lifecycle files first. [unclaimed]
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
