---
id: DOT-286
title: backlog-py branch snapshots serve phantom tasks — merged branches' stale task
  blobs list alongside live files
status: To Do
created_date: 2026-11-05 00:24
labels:
- queue-integrity
ordinal: 1
updated_date: 2026-11-12 03:26
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
2026-11-09: author-executed branch hygiene verified. Reaped: 15 worktrees, 15 merged local branches, 16 merged remote refs (all blob-carrying, all fully merged). Dot-108 blob-holders 42 -> 9. Remaining warnings (3 TASK- phantoms, DOT-108 + DOT-281-284 shadows) trace ONLY to the spared unmerged branches (agent_skills_refresh, lima-molecule, mise-remove-whisperx, mise-upgrade-result, molecule-qemu-loreai, docs-relocate-review, backup/main-before-sync-20261104) — real unlanded work 300-390 commits behind main. test_no_shadowed_task_ids still fails on those; documented-skip era continues until the spared branches land or die, or the 30-day window expires. checkActiveBranches stays on per author ruling.
2026-11-11: six duplicate-ID warnings blocked DOT-352's task commit on a main checkout that otherwise matched origin/main. They came from old task records at the tips of the backup, agent-skills-refresh, and gita-lifecycle-docs branches. DOT-353 temporarily sets checkActiveBranches to false after the maintainer chose that smaller repair over editing those sessions' task records. This task owns safe scanner repair and re-enablement. Retire only merged branches after proving they have landed; do not treat any historical-copy deletion as a substitute for the scanner fix.
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->
