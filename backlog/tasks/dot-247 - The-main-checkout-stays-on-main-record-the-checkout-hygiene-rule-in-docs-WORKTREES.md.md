---
id: DOT-247
title: The main checkout stays on main — record the checkout-hygiene rule in docs/WORKTREES.md
status: Done
created_date: 2026-10-28 01:01
labels:
- queue-integrity
- docs
ordinal: 0
orchestration:
  status_key: inprogress
  lease_owner: opencode-coordinator
  lease_expires_at: '2026-10-28T02:01:38.294561Z'
  version: 1
updated_date: 2026-10-28 01:02
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
During the DOT- prefix docs work (PR #87, 2026-10-27) the agent created the task branch by switching the SHARED main checkout's branch, then switched back — requiring a stash dance and briefly moving governance-file state under every other session's feet. The main checkout is the collector: its branch is shared state. Task branches get their own worktree, always. Fix: one line in docs/WORKTREES.md stating the rule, so the contract names the failure mode. Legacy: author correction 2026-10-27 — 'these separate tasks should each be getting their own git branch and worktree'.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
Landed as PR #91 (fc30e84): the rule now lives in docs/WORKTREES.md § Layout, written from its own worktree per the corrected pattern.
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
event_id: run-742b6485a7e042cd9c88e8cb5044ecb7
type: claim_task
actor: opencode-coordinator
timestamp: '2026-10-28T01:01:38.294646Z'
result: succeeded
task_id: DOT-247
from_status: todo
to_status: inprogress
metadata:
  lease_ttl_seconds: '3600'
```
One-line governance addition; doing it with the corrected pattern itself — own worktree, own branch
<!-- RUN_HISTORY_ENTRY:END -->
<!-- SECTION:RUN_HISTORY:END -->
