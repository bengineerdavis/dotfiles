---
id: DOT-373
title: Let the pre-switch sync branch from committed main when only other sessions
  dirty it
status: To Do
created_date: 2026-11-17 20:46
labels:
- process
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
scripts/sync-task-base.py refuses any `wt switch --create` while the main checkout has uncommitted changes, even when they belong to other sessions and the new branch would start from committed main. On 2026-11-17 this blocked two worktrees in one session (retro, ses_e398d0a9).

Ship:

- a design decision on when a dirty main may still seed a branch: for example, base the branch on origin/main after fetching, without touching the main checkout
- the change in sync-task-base.py, with tests for: clean main, dirty main, main behind origin, diverged main

Constraints:

- a diverged or behind main keeps failing closed unless the decision says otherwise
- never stash, commit or discard another session's files
- decide with the author before changing the gate (it guards every worktree)
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The decision is recorded in the task notes, approved by the author
- [ ] #2 Tests cover the four main states, and each was seen to fail against a broken copy
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
