---
id: DOT-353
title: Repair shadowed queue IDs left on the main backup branch
status: Done
created_date: 2026-11-12 03:10
assignee:
- OpenCode
labels:
- backlog
- repair
priority: high
orchestration:
  status_key: todo
  version: 2
updated_date: 2026-11-12 03:27
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Historical queue records on active local branches reuse IDs that now belong to different tasks on main. backlog-py's active-branch scanning shadows one record in each collision, so the queue-integrity commit hook fails.

Ship:

- Disable backlog-py's active-branch scanning in backlog/config.yml as a temporary repair that preserves every branch and task record.
- Keep DOT-286 open for the scanner's stale-snapshot behavior and its safe re-enablement.
- Restore a passing queue-integrity check so DOT-352 can be committed normally and pushed.

Constraints:

- Do not delete or rename branches or tasks, rewrite history, or alter other sessions' worktrees.
- Do not bypass queue-integrity or other commit hooks.
- Keep unrelated files and in-flight sessions' changes untouched.

Agreed with the maintainer 2026-11-11: temporarily disable active-branch scanning rather than editing other sessions' queue records.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 backlog/config.yml disables checkActiveBranches and records why this is temporary beside the setting.
- [x] #2 DOT-286 retains the active-branch scanner repair and re-enablement follow-up.
- [x] #3 uv run --frozen pytest tests/backlog/test_queue_integrity.py -q passes.
- [x] #4 No branch or other task record is renamed, deleted, or rewritten by this repair.
- [x] #5 DOT-352 is committed without a hook bypass.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
Verified 2026-11-11: backlog-py's active-branch loader reads task blobs at branch tips, not every past revision. An initial archive-ref proposal was therefore unnecessary and was corrected before implementation.
Verified 2026-11-11: changing historical queue IDs on active branches would touch three other sessions' branches. The maintainer approved the smaller repo-local scanner-disable repair; this does not repair the scanner itself. An initial archive-ref proposal was unnecessary and was corrected before implementation.
Implementation branch agent/dot-352-global-config, commit 036011e7. Only backlog/config.yml and DOT-286 changed. Queue-integrity suite: 6 passed. DOT-352 and this task are committed with normal hooks; no hook bypass. No branch or unrelated task was renamed or deleted.
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Temporarily disabled backlog-py's active-branch scanning. Preserved every branch and task record. DOT-286 owns the scanner repair and safe re-enablement. Queue integrity passes: 6/6.
<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->

## Run History
<!-- SECTION:RUN_HISTORY:BEGIN -->
<!-- RUN_HISTORY_ENTRY:BEGIN -->
```yaml
event_id: run-d6948bb96a5445988d6e744e47c0b731
type: claim_task
actor: OpenCode git-topic session
timestamp: '2026-11-12T03:10:39.081398Z'
result: succeeded
task_id: DOT-353
from_status: todo
to_status: inprogress
metadata:
  lease_ttl_seconds: '3600'
```
Repair duplicate queue IDs blocking the authorized Git configuration task commit.
<!-- RUN_HISTORY_ENTRY:END -->
<!-- RUN_HISTORY_ENTRY:BEGIN -->
```yaml
event_id: run-2df2be074b9e431998f319ad176482be
type: release_task
actor: OpenCode git-topic session
timestamp: '2026-11-12T03:34:09.685988Z'
result: succeeded
task_id: DOT-353
from_status: inprogress
to_status: todo
```
<!-- RUN_HISTORY_ENTRY:END -->
<!-- SECTION:RUN_HISTORY:END -->
