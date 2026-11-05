---
id: DOT-249
title: Renumber the leased gateway task to DOT-243 when its lease releases
status: Done
created_date: 2026-10-28 01:23
labels:
- queue-integrity
ordinal: 3
updated_date: 2026-11-05 00:24
orchestration:
  status_key: todo
  version: 2
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
TASK-243 (Add a gateway service to apps/loreai, claimed by the loreai-gateway-service session) is the one task deliberately left TASK-prefixed after the 2026-10-27 DOT- migration — its orchestration lease made renumbering it mid-flight unsafe. When the lease releases (check: backlog-py orchestration claims), run: backlog-py task renumber TASK-243 DOT-243. Until then it is the only TASK- file in backlog/tasks/, and the queue-integrity test tolerates both prefixes for exactly this case. Legacy: the DOT- prefix migration, 2026-10-27.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
2026-10-28: lease-state refinement — the lease expired (4h TTL) but PR #88 is still OPEN: the gateway session is mid-flight, not done. Lease release alone is not the safety condition; the PR merging is. Renumber only after PR #88 merges, or the session's next record-run writes task-243 back from its stale tree — the exact DOT-246 pattern.
2026-11-04: executed via the real mechanism — git mv task-243 to dot-243 + frontmatter id flip. The task's named command 'backlog-py task renumber TASK-243 DOT-243' does not exist in backlog-py 2.2.0 (verified against the command list); the original migration (f4ad28d) used git mv + frontmatter edits. Precondition verified: PR #88 merged 2026-10-28, gateway branch fully merged (empty main..loreai-gateway-service), its worktree holds only untracked residue. FINDING (empirically confirmed by flipping checkActiveBranches to false — the phantom vanished): backlog-py's branch-snapshot loader (checkActiveBranches: true, 30-day window) serves the merged branch's stale task-243 blob as a phantom TASK-243 list entry alongside the live DOT-243; doctor stays silent because snapshots are not files. The phantom clears when the branch is deleted or the 30-day window passes. Branch deletion is blocked by the branch's worktree + ask-tier permissions — author decision. Also observed: task-242/244 phantoms from the same mechanism; a cosmetic DOT-108 completed/ shadow (filename task-108, id DOT-108, only copy — no live shadow).
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
event_id: run-7bc8648cd8084ab8897abc41e4702e36
type: claim_task
actor: opencode-coordinator
timestamp: '2026-11-05T00:15:50.484839Z'
result: succeeded
task_id: DOT-249
from_status: todo
to_status: inprogress
metadata:
  lease_ttl_seconds: '3600'
```
PR #88 merged 2026-10-28 — precondition met, no leases active; executing the renumber now
<!-- RUN_HISTORY_ENTRY:END -->
<!-- RUN_HISTORY_ENTRY:BEGIN -->
```yaml
event_id: run-13db936feda843b8b91755941286c9ea
type: release_task
actor: opencode-coordinator
timestamp: '2026-11-05T00:24:06.823064Z'
result: succeeded
task_id: DOT-249
from_status: inprogress
to_status: todo
```
<!-- RUN_HISTORY_ENTRY:END -->
<!-- SECTION:RUN_HISTORY:END -->
