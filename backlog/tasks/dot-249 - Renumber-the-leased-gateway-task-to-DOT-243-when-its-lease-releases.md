---
id: DOT-249
title: Renumber the leased gateway task to DOT-243 when its lease releases
status: To Do
created_date: 2026-10-28 01:23
labels:
- queue-integrity
ordinal: 3
updated_date: 2026-10-28 02:51
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
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->
