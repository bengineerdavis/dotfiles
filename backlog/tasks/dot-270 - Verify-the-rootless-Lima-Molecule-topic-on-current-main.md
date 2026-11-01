---
id: DOT-270
title: Verify the rootless Lima Molecule topic on current main
status: To Do
created_date: 2026-10-29 18:30
assignee:
- opencode
labels:
- testing
- molecule
priority: high
orchestration:
  status_key: inprogress
  lease_owner: opencode-lima-rebase
  lease_expires_at: '2026-10-29T19:32:57.731491Z'
  version: 1
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Rebase PR #99 onto current main. Verify the rootless Lima topic and delegated Debian scenario without disturbing other active VM processes. Preserve uncommitted work in the old worktree by using .worktrees/lima-rebase and a separate branch tracking the PR. Documentation consolidation comes afterward.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 PR #99 rebases onto current main with the home/ payload layout.
- [ ] #2 Focused contract tests and current real Debian guest lifecycle evidence pass.
- [ ] #3 Scenario teardown leaves no VMs or processes owned by the scenario; unrelated Rancher Desktop and Lima processes are untouched.
- [ ] #4 The updated PR records macOS evidence and the Linux-host limitation.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->

<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 The updated PR is ready for human review with focused and full-suite verification recorded.
<!-- DOD:END -->

## Run History
<!-- SECTION:RUN_HISTORY:BEGIN -->
<!-- RUN_HISTORY_ENTRY:BEGIN -->
```yaml
event_id: run-3c005e50afc94de2924068336132a727
type: claim_task
actor: opencode-lima-rebase
timestamp: '2026-10-29T18:32:57.731556Z'
result: succeeded
task_id: DOT-270
from_status: todo
to_status: inprogress
metadata:
  lease_ttl_seconds: '3600'
```
Rebase and verify PR #99 on the current payload layout
<!-- RUN_HISTORY_ENTRY:END -->
<!-- SECTION:RUN_HISTORY:END -->
