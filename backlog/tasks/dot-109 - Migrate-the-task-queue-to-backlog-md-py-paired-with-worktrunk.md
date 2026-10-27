---
id: DOT-109
title: Migrate the task queue to backlog-md-py, paired with worktrunk
status: Done
created_date: 2026-10-27 02:56
labels:
- now
priority: high
updated_date: 2026-10-27 22:21
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Migrate the task queue to backlog-md-py, paired with worktrunk.**
  Promoted from § Planned 2026-10-22 (author direction of 2026-10-18);
  decisions settled with the author 2026-10-22: migrate EVERYTHING (§ Now
  and every § Planned essay becomes a backlog task), REMOVE the old
  workflow entirely (TASKS.md hand-maintained queue, TASKS-RESOLVED.md,
  tests/tasks_doc; PROCESS.md/AGENTS.md queue rules rewritten), pair
  worktrunk now, and land a decision PR before any migration work. Done
  when `TASKS.md` is an index over per-task files and a task line never
  lives only in a chat. **Done-condition amended 2026-10-22 (ruling 2):
  no TASKS.md survives — done when the cutover in
  docs/BACKLOG-MIGRATION.md § Procedure lands, `TASKS.md` and
  `TASKS-RESOLVED.md` are deleted, and `backlog/` is the one queue.**
  [agent: this session] (branch
  `agent/backlog_migration`, worktree `.worktrees/backlog-migration`).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->

<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Cutover complete 2026-10-27 (PR #73 decision, PR #78 migration, two conflict-resolution passes with the cutover winning per author ruling). 177 items imported; TASK-229 salvaged and later deduped to task-1; TASK-230/231/232/233/234 queued since. TASKS.md and TASKS-RESOLVED.md deleted; archive/tasks-md tag pins the old world. apps/backlog owns install + daemon service; MCP registered for opencode; worktrunk installed. docs/PROCESS.md, AGENTS.md, spec.md, WORKTREES.md rewritten; tests/backlog replaces tests/tasks_doc.
<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->
