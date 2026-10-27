---
id: DOT-103
title: Topic VM test harness — run the v2 migration confirmation
status: To Do
created_date: 2026-10-27 02:56
labels:
- now
priority: high
updated_date: 2026-10-27 22:21
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Topic VM test harness — run the v2 migration confirmation.**
  [agent: orch_sub_vrun, worktree `.worktrees/orch_sub_vrun`] Execute
  the harness end to end on a clean box: create, converge (run-role
  path for apps/opencode), verify (v2 formula installed, v1 gone, the
  migrated config loads without diagnostics, skills synced), then the
  author's interactive flow exercised at least once (login, inspect,
  destroy). Record the evidence with its conditions — box image,
  provider, timings — and state the migration verdict naming what was
  and was not exercised (spec § Evidence). Done when the run is
  recorded on the PR and the verdict is explicit.
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
