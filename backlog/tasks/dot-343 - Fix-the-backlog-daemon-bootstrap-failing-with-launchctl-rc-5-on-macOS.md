---
id: DOT-343
title: Fix the backlog daemon bootstrap failing with launchctl rc 5 on macOS
status: Done
created_date: 2026-11-10 17:36
labels:
- bug
priority: high
updated_date: 2026-11-17 22:39
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The Darwin bootstrap task in home/dotfiles/apps/backlog/tasks/install.yaml failed on 2026-11-10 with "Bootstrap failed: 5: Input/output error". The plist lints OK and launchd lists the label as enabled, but nothing listens on 127.0.0.1:18765, so the daemon is down.

Ship:

- a reproduction command that goes red on this failure before any fix
- a fix so the bootstrap task converges whether the service is loaded, half torn down, or absent
- a regression test for the task's behaviour

Constraints:

- diagnose before fixing (diagnosing-bugs); the candidate causes are unconfirmed: bootout returning before teardown finishes, `2>/dev/null` hiding a bootout failure, the mise shim in ProgramArguments
- gui-domain launchctl needs no sudo; do not add become
- deployed-tree change: branch, PR, human review
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The reproduction command is recorded in the notes and was seen red before the fix
- [ ] #2 The backlog topic run succeeds twice in a row on macOS and backlog-py daemon status --json exits 0
- [ ] #3 The regression test was seen to fail against the unfixed task (Mutation:/Failing-test: trailers)
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
