---
id: TASK-102
title: Topic VM test harness — implement (molecule scaffolding + apps/opencode scenario)
status: To Do
created_date: 2026-10-27 02:56
labels:
- now
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Topic VM test harness — implement (molecule scaffolding +
  apps/opencode scenario).** [agent: orch_sub_vimpl, worktree
  `.worktrees/orch_sub_vimpl`] From the plan: wire the molecule
  dependency the plan chose, build the wrapper (minimal, documented,
  human-and-machine callable), and write apps/opencode's scenario
  asserting the v2 migration end state on a Debian box. The scenario's
  verify phase is the test suite for this work — plus pytest coverage
  for the wrapper's argument handling where the house layout wants it.
  Done when `molecule test` passes end-to-end against the real box and
  each phase verb works when run alone.
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
