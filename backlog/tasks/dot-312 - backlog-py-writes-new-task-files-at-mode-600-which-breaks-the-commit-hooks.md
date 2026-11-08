---
id: DOT-312
title: backlog-py writes new task files at mode 600, which breaks the commit hooks
status: To Do
created_date: 2026-11-08 20:34
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Measured 2026-11-08. `backlog-py task create` writes the new file mode 600 (`-rw-------`). Twelve task files in `backlog/tasks/` are currently 600; the rest are 664.

Why it breaks commits: `core.fileMode` is true in this repo, so the 644-vs-600 difference is a real content change to git. The queue-integrity pre-commit hook stashes unstaged changes before running `pytest tests/backlog`, and that stash fails with:

    error: Entry 'backlog/tasks/dot-311 - ...md' not uptodate. Cannot merge.

so the hook reports Failed while the tests themselves pass (6 passed). The commit aborts with 'Stashed changes conflicted with hook auto-fixes', and the reason is invisible unless you know to check the file mode. Two earlier attempts were misdiagnosed as a test failure.

Workaround that works: `chmod 644` the task file before committing.

Two things to fix, and the second is the one that keeps it fixed:
1. Normalise the twelve files already at 600.
2. Make new tasks land at the repo's mode — either backlog-py writing 644, or a step in the queue-integrity hook/test that asserts task modes match, so the trap fails loudly with a mode message instead of a stash error from git.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A newly created task file lands at the same mode as its neighbours without manual chmod
- [ ] #2 If backlog-py itself cannot be changed, a test names the mode mismatch rather than letting git's stash error be the only symptom
- [ ] #3 The twelve existing 600 files are normalised
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
