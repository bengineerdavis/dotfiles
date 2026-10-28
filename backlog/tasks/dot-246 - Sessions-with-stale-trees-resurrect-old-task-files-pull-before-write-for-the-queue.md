---
id: DOT-246
title: Sessions with stale trees resurrect old task files — pull-before-write for
  the queue
status: Done
created_date: 2026-10-27 22:24
labels:
- queue-integrity
ordinal: 0
orchestration:
  status_key: todo
  version: 2
updated_date: 2026-10-28 03:18
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
2026-10-28: repo-local half landed as PR #93 — tests/backlog now runs as a prek hook on backlog/ commits (mutation-proven: a copied task-235 resurrection fails the doctor check), plus the PROCESS.md sync-before-first-write duty. The tool-side pull-before-write guard is routed to backlog-md-py upstream — an author decision, not a repo-local build.
2026-10-28: merged as PR #93. Live proof followed within the hour — the next queue commit ran the hook on a backlog/-only diff instead of skipping. Upstream pull-before-write guard remains an open author decision (recorded in the PR).
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->

## Run History
<!-- SECTION:RUN_HISTORY:BEGIN -->
<!-- RUN_HISTORY_ENTRY:BEGIN -->
```yaml
event_id: run-47873022514d4f1986eca4e00e3ff27f
type: claim_task
actor: opencode-coordinator
timestamp: '2026-10-28T02:52:23.390989Z'
result: succeeded
task_id: DOT-246
from_status: todo
to_status: inprogress
metadata:
  lease_ttl_seconds: '3600'
```
Repo-local half of the fix: wire the queue-integrity checks into the commit hooks so a resurrected duplicate fails the commit instead of shadowing silently
<!-- RUN_HISTORY_ENTRY:END -->
<!-- RUN_HISTORY_ENTRY:BEGIN -->
```yaml
event_id: run-4f7e55e8cb8a48059373db697782a9fb
type: release_task
actor: opencode-coordinator
timestamp: '2026-10-28T02:55:51.862436Z'
result: succeeded
task_id: DOT-246
from_status: inprogress
to_status: todo
```
<!-- RUN_HISTORY_ENTRY:END -->
<!-- SECTION:RUN_HISTORY:END -->
