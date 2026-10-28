---
id: DOT-258
title: 'DRAFT: Repair queue integrity after task migration'
status: To Do
created_date: 2026-10-28 17:47
labels:
- backlog
- process
priority: high
orchestration:
  status_key: inprogress
  lease_owner: opencode-queue-integrity
  lease_expires_at: '2026-10-28T20:08:43.251244Z'
  version: 1
updated_date: 2026-10-28 18:18
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The full test suite on 2026-10-28 fails tests/backlog/test_queue_integrity.py::test_doctor_reports_no_problems. backlog-py warns that DOT-233 has an unterminated IMPLEMENTATION_NOTES owned section. It also reports duplicate task IDs for the old gateway/agent tasks and the newer task files. Determine the intended task ownership and migration state before editing; this is a queue-integrity repair, not permission to silently rewrite another session's in-flight task. DOT-249 records the deliberately deferred TASK-243 renumber. Decide whether that exception should remain and how to retire the other duplicate IDs. Preserve task history and other sessions' work. This is separate from the Lore gateway PR.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 backlog-py doctor reports no malformed owned sections or unintended duplicate task IDs.
- [x] #2 The intended ownership/history of each affected task is preserved and any renumbering follows the queue migration rules.
- [x] #3 uv run --frozen pytest tests/backlog/test_queue_integrity.py -q passes.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
Completed implementation on main in 0b9448d. Doctor reports No problems found and 4 queue-integrity tests pass. DOT-233 preserves its substantive task content and has balanced owned sections. The Lore branch merged current main as b3237f2, inheriting the DOT migration; its old TASK-240/TASK-241 duplicates are gone. No additional queue branch is needed. Ready for maintainer acknowledgment; direct completed/done orchestration transitions are not supported by this CLI version.
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
event_id: run-4c204e9e2490465e8888550b36730b51
type: claim_task
actor: opencode-queue-integrity
timestamp: '2026-10-28T18:08:43.251320Z'
result: succeeded
task_id: DOT-258
from_status: todo
to_status: inprogress
metadata:
  lease_ttl_seconds: '7200'
```
Separate queue repair branch .worktrees/queue-integrity; preserve other sessions task edits.
<!-- RUN_HISTORY_ENTRY:END -->
<!-- RUN_HISTORY_ENTRY:BEGIN -->
```yaml
event_id: run-fa4de3070a6f45cd8fbdbcc177771ec9
type: record_run
actor: opencode-queue-integrity
timestamp: '2026-10-28T18:19:00.051759Z'
result: pr-ready
task_id: DOT-258
```
Queue repair landed on main in 0b9448d and all acceptance evidence passes. Lore branch merged main and its duplicate task IDs are resolved. Awaiting maintainer acknowledgment; no unsupported orchestration completion status forced.
<!-- RUN_HISTORY_ENTRY:END -->
<!-- SECTION:RUN_HISTORY:END -->
