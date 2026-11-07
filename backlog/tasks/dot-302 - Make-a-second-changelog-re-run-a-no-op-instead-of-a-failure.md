---
id: DOT-302
title: Make a second changelog re-run a no-op instead of a failure
status: To Do
created_date: 2026-11-07 18:44
labels:
- planned
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Make a second manual changelog re-run exit cleanly, instead of failing on a
fragment the first run already deleted.

PR #136 added `workflow_dispatch`, so a failed collection can be re-run by
hand — the first one works. A **second** re-run of the same PR hits this:

```
while IFS= read -r fragment; do
  test -f "$fragment"
  mv -- "$fragment" "$work/fragments/"
done < "$work/fragments-to-collect"
```

The first successful run deletes the fragment. Under `set -euo pipefail`,
`test -f` exits 1 and the job goes red — for a PR whose collection is already
correct. Measured 2026-11-07 by running the loop with the fragment absent:
exit code 1, no output naming why.

This is a small, real trap: pressing "Re-run" twice is the most natural thing
to do when you are unsure whether the first one worked, and the second press
reports failure on success. It teaches the reader that a red collection run is
noise, which is exactly the opposite of what DOT-301 is trying to establish.

The fix is a `[[ ! -f "$fragment" ]]` guard that skips the missing fragment and
continues, plus a check that exits 0 with "already collected" when nothing is
left to move. Skipping per-fragment rather than aborting matters: a PR with two
fragments where only one was collected should still collect the other.

The test that catches this has to assert the branch, not a phrase — a grep for
the message "already collected" also matches the later no-op block, so it stays
green against the unfixed loop. Assert `! -f` and `continue` inside the loop
body.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A second `workflow_dispatch` run of an already-collected PR exits 0 and reports that there is nothing to do
- [ ] #2 A PR with two fragments, one already collected, still collects the remaining one
- [ ] #3 The test asserts the loop's branch, not the presence of the message — and is seen to fail against the current bare `test -f`
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
The mutation to record: restore `test -f "$fragment"` in place of the guard.
A test that greps for "already collected" survives this mutation, because the
same message appears in the nothing-left-to-move block further down.
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 Re-running a completed collection twice in a row is green both times
<!-- DOD:END -->