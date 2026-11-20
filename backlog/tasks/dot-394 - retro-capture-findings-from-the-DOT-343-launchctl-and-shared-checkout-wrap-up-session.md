---
id: DOT-394
title: 'retro: capture findings from the DOT-343 launchctl and shared-checkout wrap-up
  session'
status: To Do
created_date: 2026-11-19 21:15
updated_date: 2026-11-20 16:42
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->

Session retro (2026-11-17 → 2026-11-19): a handoff told this session to work
the dotfiles queue starting at DOT-343. Almost none of it went as briefed. The
corrections below are recorded because the handoff's facts were wrong in ways
that cost work, and because two live sessions were editing the same checkout.

**What landed**

- DOT-343 already had a complete fix in `.worktrees/dot-343-launchctl-rc5` when
  this session arrived. PR #181 merged at 22:39Z without this session touching
  it — another session finished it while this session audited. Correct outcome;
  the session contributed verification, not code.
- Verified PR #181 independently in an isolated worktree: 26 tests green, and a
  mutation back to the original `bootout;bootstrap&&enable` chain turned 6 tests
  red, including live convergence against throwaway launchd labels. The merged
  claim holds.
- `preserve/queue-2026-11-19` (2 commits) carries the two artifacts that existed
  nowhere else: `docs/CHERRY-PICK-RECONCILIATION.md` and the DOT-393 task.

**What went wrong (corrections)**

1. **The handoff's git facts were stale, and acting on them would have rewritten
   history.** It said origin/main = `27a74504` and local main was 1 commit ahead.
   Measured: origin was `d84a6033` and local was 8 ahead, and by the end of the
   session local main was 28 ahead / 34 behind. Lesson: a handoff's SHAs are
   evidence about the moment it was written, never about now. Re-measure
   `git rev-list --left-right --count origin/main...main` before any push.
1. **`backlog-py task view` does not exist.** The correct spellings are
   `task <ID>` and `task list`. The handoff named a command that has never been
   in the CLI; every task read failed until it was corrected.
1. **Claiming a task wrote run-history into the working tree of a checkout
   another session was actively using.** The claim/release pair appended two
   `RUN_HISTORY_ENTRY` blocks to main's DOT-343 file. Reverted immediately, but
   the lesson stands: `orchestration claim` mutates the task file in the
   checkout, so it is a write, not a read — check `git status` before and after.
1. **Two sessions worked the same worktree at the same time.** While this
   session read `.worktrees/dot-343-launchctl-rc5`, another committed the
   `roles/services` role, opened PR #181, and pushed — the branch tip moved from
   `762a0417` to `f357ddf7` under this session. Nothing was lost because this
   session only read, but the worktree had no exclusive owner. DOT-378 and
   DOT-386 cover the general problem.
1. **A live session was committing to local main throughout the wrap-up.** main
   moved three times during the session (`9df1a609` → `b5d49ab0` → `b0996391`),
   each a DOT-349 backlog record. This is why the session did not reset main
   despite the author pre-approving cleanup: `reset --hard` would have destroyed
   another session's in-flight commits, which no wrap-up authorization covers.
1. **The branch-sync pre-push gate rejects the preservation branch.** Verified:
   `merge-tree --write-tree origin/main handoff/local-main-2026-11-19` conflicts
   on `.lore.md` and the DOT-381 task file, because the branch holds duplicates
   of already-cherry-picked commits. Preserving by pushing that branch therefore
   cannot pass the gate. The artifacts were instead cherry-picked onto a branch
   cut from current `origin/main`, which merges clean.
1. **A test run left 64 launchd override entries behind.** `launchctl print-disabled` accumulated `com.backlog-py.test-*` and `com.example.role-test-*`
   entries; the tests `enable` labels in cleanup but never remove the override
   record, and the override database has no delete subcommand. Harmless (all
   read `enabled`), but it is residue a live daemon now carries. Worth a test
   -hygiene note; not filed as a task because there is no fix short of
   `launchctl reset`, which clears the user's whole domain.

**Negative results**

- The `bootout` teardown race is real documentation but was **not**
  reproducible on this host (PR #181 records 0 failures in 25 attempts). Removing
  the wait survives the suite. Recorded as an honest gap in that PR rather than
  as a verified fix.
- Nothing in the DOT-343 failure involved the mise shim in `ProgramArguments`,
  `StandardOutPath` directory creation, or a nonexistent program path — all three
  were probed and returned rc 0.

**Follow-ups filed elsewhere, not duplicated here**

- DOT-373: the pre-switch gate refuses a dirty main even when the branch would
  be cut from committed main. This session hit it on every `wt switch --create`.
- DOT-378: reconcile a dirty shared checkout without moving another session's work.
- DOT-386: recover sessions orphaned by the directory move.
- DOT-393: whether a subagent can write a file (queued by another session).

<!-- SECTION:DESCRIPTION:END -->

## Definition of Done

<!-- DOD:BEGIN -->

<!-- DOD:END -->
