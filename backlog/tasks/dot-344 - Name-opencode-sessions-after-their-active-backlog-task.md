---
id: DOT-344
title: Name opencode sessions after their active backlog task
status: To Do
created_date: 2026-11-10 17:36
labels:
- urgent
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
With 10 or more opencode sessions running, nothing links a session to its backlog task, so working out who owns a dirty or ahead main is close to impossible. On 2026-11-10 a dirty main blocked a worktree, and the owning session could not be identified.

Ship:

- sessions are titled `<backlog id>-<short slug of the task title>` when they claim or start a task, and retitled when they switch tasks
- a way to map a dirty file or an unpushed commit on main back to the session that made it

Constraints:

- use what exists first: opencode session_rename, backlog-py orchestration claims, an AGENTS.md rule; anything that needs new code goes up the build ladder (AGENTS.md) before it is built
- titles stay short enough to scan across 10+ sessions
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A session that claims a task shows the title <id>-<slug> in the opencode session list
- [ ] #2 A documented command maps a dirty file or ahead commit on main to the owning session or claim
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
