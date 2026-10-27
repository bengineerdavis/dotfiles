---
id: DOT-139
title: Extend `tests/tasks_doc` to fail on referenced paths that do not exist
status: To Do
created_date: 2026-10-27 02:57
labels:
- planned
updated_date: 2026-10-27 22:22
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Extend `tests/tasks_doc` to fail on referenced paths that do not exist.**
  The advisor pass found dangling references a validator would catch
  mechanically: `run-role.sh` unprefixed in AGENTS.md, `machines.yml`
  described as existing when it was a design, `.chezmoiignore` line-number
  decay, a task line naming one file twice where two were meant. Scope:
  parse backtick-quoted repo-relative paths and check existence; fail on
  section-heading mismatches. Done when the validator catches a deliberately
  planted dangling path (mutation-checked). [me]
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
