---
id: DOT-336
title: Give the shadow guard an exemption for the commit that removes the duplicate
status: To Do
created_date: 2026-11-09 15:44
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
`test_no_shadowed_task_ids` reads branch snapshots, not the tree being
committed. When a stale branch holds an older copy of a task whose duplicate
this commit deletes, the guard reports the duplicate the commit exists to
remove, so the commit cannot land.

Measured twice: DOT-104 (2026-11-05) and DOT-311 (2026-11-08). In the second,
another session had created a new DOT-311 while the deletion of the old one sat
uncommitted; both `main` and `agent/session-close` still carried the old file, so
the guard fired on a duplicate that only the blocked commit could clear. The
escape used was `SKIP=queue-integrity`, which bypasses every check in the stage.

Ship:

- The guard distinguishes "a duplicate that exists after this commit" from "a
  duplicate this commit removes", and fails only on the first.
- The mechanism by which it learns what the commit touches is chosen and
  recorded — `pass_filenames` is currently `false` for this hook, so the test
  receives no paths at all.
- A test reproduces the deadlock: a commit deleting one of two same-id files
  passes, while an unrelated duplicate still fails.
- The `SKIP=queue-integrity` escape from 2026-11-08 is no longer needed, proven
  by re-running the original scenario end to end.

Constraints:

- `checkActiveBranches: true` is global (`backlog/config.yml`) with only
  `activeBranchDays` as a knob; the fix must not disable branch scanning, which
  is what catches genuine shadowing.
- The guard keeps failing closed on every other duplicate shape; this exempts
  one case, it does not relax the rule.
- Flipping `pass_filenames` changes the contract for all six queue tests, so the
  change states what each of them does with paths it did not previously receive.

Decision 2026-11-09: queued rather than fixed in the session that hit it, because
the fix changes the hook's contract and the prek stash behaviour (DOT-312) is a
separate blocker on the same stage.

<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A commit that deletes one of two same-id task files passes the queue-integrity hook, proven by a test that fails against the current implementation.
- [ ] #2 An unrelated duplicate that the commit does not remove still fails the hook, proven by a test.
- [ ] #3 The mechanism by which the guard learns which paths the commit touches is recorded in the task or a code comment, naming why the rejected alternative was rejected.
- [ ] #4 The 2026-11-08 scenario is re-run end to end and the commit lands without SKIP=queue-integrity, with the result recorded.
- [ ] #5 `checkActiveBranches` remains true in backlog/config.yml — branch scanning is not disabled to dodge the race.
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
