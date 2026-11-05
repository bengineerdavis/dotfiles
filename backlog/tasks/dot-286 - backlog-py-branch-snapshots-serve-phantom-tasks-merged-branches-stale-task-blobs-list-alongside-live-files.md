---
id: DOT-286
title: backlog-py branch snapshots serve phantom tasks — merged branches' stale task
  blobs list alongside live files
status: To Do
created_date: 2026-11-05 00:24
labels:
- queue-integrity
ordinal: 1
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Mechanism (source-read, backlog-py 2.2.0): with checkActiveBranches: true (activeBranchDays: 30), the loader (_load_active_branch_records, repository.py:363; list_active_branch_task_snapshots, git.py:240) walks recently active branch refs and serves their task blobs as candidates — a merged-but-undeleted branch carrying a task file under an old id serves that old id as a PHANTOM list entry with no file behind it. Observed 2026-11-04: after renumbering task-243 to dot-243 (DOT-249), TASK-243, TASK-242, TASK-244 all listed as phantoms from the merged loreai-gateway-service branch. Empirical proof: flipping checkActiveBranches to false made all phantoms vanish (count 0). Doctor stays silent because snapshots are not files — the queue-integrity hook (PR #93) also cannot see them. Repair options, in order: (1) delete merged branches (immediate fix, blocked here by ask-tier worktree/branch-delete — author decision); (2) set checkActiveBranches: false (blunter — loses the feature); (3) upstream backlog-md-py: auto-skip refs already merged into main. No upstream filing without the author (rmusser01 is the maintainer; do-not-submit directive).
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
