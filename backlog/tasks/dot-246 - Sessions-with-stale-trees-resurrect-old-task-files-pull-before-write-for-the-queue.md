---
id: DOT-246
title: Sessions with stale trees resurrect old task files — pull-before-write for
  the queue
status: To Do
created_date: 2026-10-27 22:24
labels:
- queue-integrity
ordinal: 0
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Observed 2026-10-27 during the DOT- prefix migration: task files that had been renamed (task-240, task-241, task-235) reappeared transiently with their old names while concurrent sessions were active — a session holding a stale working tree wrote back task files it had checked out before the renames. backlog-py doctor catches the resulting duplicate ids, but the loader silently SHADOWS one file until then, so a resurrected copy can make a real task invisible on the board. Candidate fixes: a pull-behind-main check on queue writes (the tool already refuses auto-commit on a dirty tree — the same guard could refuse writes when main is behind origin), or a house rule that sessions sync main before their first queue write of a session. Legacy: found during the DOT- prefix migration.
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
