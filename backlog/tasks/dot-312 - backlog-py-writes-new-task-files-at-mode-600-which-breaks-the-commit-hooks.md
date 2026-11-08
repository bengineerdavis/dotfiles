---
id: DOT-312
title: An intent-to-add path breaks the queue-integrity hook's stash
status: To Do
created_date: 2026-11-08 20:34
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Measured 2026-11-08, twice, and misdiagnosed both times before the cause was found by reproduction.

**Correction first.** The original version of this task blamed file mode 600. That is wrong, and the wrongness is worth recording: `git` does **not** track read/write permission bits. A mode-600 file is stored as `100644`, and `chmod 600 -> 644` produces no diff at all:

    $ chmod 600 f.md; git add f.md; git ls-files -s f.md
    100644 ... f.md
    $ chmod 644 f.md; git status --porcelain f.md
    (empty)

So mode was a red herring. It correlated with the failures because the same tool writes both, not because it causes them.

**The actual cause: `git add -N` (intent-to-add) breaks `git stash`.** The queue-integrity hook stashes unstaged changes before running `pytest tests/backlog`. When a path is staged with `-N`, the stash refuses:

    error: Entry 'backlog/tasks/dot-311 - ...md' not uptodate. Cannot merge.

Reproduced in a throwaway repo:

| Staging | `git stash push --keep-index --include-untracked` |
|---|---|
| `git add -N b.md` | `error: Entry 'b.md' not uptodate. Cannot merge.` |
| `git add b.md` | succeeds |

The symptom is confusing because the tests themselves pass (6 passed) while the hook reports Failed — the failure is in the stash, not the assertions. The advice the hook prints is about test failures, so the real cause is invisible unless you reproduce it.

**What to fix.** The queue-integrity hook should not depend on a stash that a legitimate staging state can break. Options, to be decided here:
1. Make the hook tolerate intent-to-add paths (stage them for real before stashing, or stash with a form that handles them).
2. Have the hook compare against `HEAD` instead of the working tree, so no stash is needed.
3. Detect the specific error and report it plainly, naming `git add -N` as the cause, instead of the current generic "tests failed" framing.

Whichever is chosen, the guard must be able to run on a tree that a developer has legitimately staged with `-N` — that is a normal `git add -p`/`-N` workflow outcome, not an error.

Note that removing the file-mode claim means normalising the thirteen 600-mode task files is **not** part of this task; it is cosmetic and separately owned.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The queue-integrity hook passes on a tree where a task file is staged with `git add -N` — that is a normal staging outcome, not an error
- [ ] #2 If the hook cannot run, the message names the actual cause (`git add -N` / stash conflict), not a generic test failure
- [ ] #3 A test reproduces the original failure and fails against the current implementation, proving the fix addresses the cause rather than the symptom
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
