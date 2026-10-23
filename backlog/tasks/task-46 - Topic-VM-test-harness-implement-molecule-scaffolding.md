---
id: TASK-46
title: Topic VM test harness — implement (molecule scaffolding +
status: To Do
created_date: 2026-10-23 16:50
labels:
- migration
ordinal: 44
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
apps/opencode scenario).** [agent: orch_sub_vimpl, worktree
  `.worktrees/orch_sub_vimpl`] From the plan: wire the molecule
  dependency the plan chose, build the wrapper (minimal, documented,
  human-and-machine callable), and write apps/opencode's scenario
  asserting the v2 migration end state on a Debian box. The scenario's
  verify phase is the test suite for this work — plus pytest coverage
  for the wrapper's argument handling where the house layout wants it.
  Done when `molecule test` passes end-to-end against the real box and
  each phase verb works when run alone.

Legacy: TASKS.md § Now item 44 of 49, migrated to backlog 2026-10-23 (branch agent/backlog-migration).
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
