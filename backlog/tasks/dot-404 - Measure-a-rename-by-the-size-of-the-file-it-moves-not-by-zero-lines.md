---
id: DOT-404
title: Measure a rename by the size of the file it moves, not by zero lines
status: To Do
created_date: 2026-11-25 04:50
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
`scripts/check_commit_proportionality.py` computes a change's size with
`git diff --cached --numstat` and sums added plus removed lines. A pure
rename reports `0 0` for both, so a rename of a large file measures as a
zero-line change and gets the 30-word mechanical-edit budget.

Measured 2026-11-24: a 13-file topic of 607 lines, moved wholesale with
`git mv`, budgeted 30 words and rejected a 97-word message that was well
under the real 210-word budget. The documented `Proportionality:` escape
carried both commits; the escape should not be the normal path for a move.

The existing suite has a `scope: rename a variable` case at
`tests/commit_proportionality/test_proportionality.py:91`, but it passes
`changed_lines=2` by hand — it tests the budget maths, never `staged_lines()`
against a real rename. The unit is covered; the seam that broke is not.

Ship:

- `staged_lines()` counts a rename's moved file by its size, so a move is
  budgeted like the change it is.
- A test that stages a real `git mv` in a throwaway repository and asserts
  the measured size, rather than passing a number in.
- A regression case for the mixed shape: one rename plus one edited file.

Constraints:

- Do not change the budget curve; only what a rename contributes to the line
  count.
- Do not weaken the escape hatch.
- Prove the test fails by reverting `staged_lines()` to the `--numstat` sum.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 `staged_lines()` counts a renamed file by its size rather than contributing zero
- [ ] #2 A test stages a real `git mv` in a throwaway repository and asserts the measured line count, rather than passing a number in
- [ ] #3 A mixed case is covered: one rename plus one edited file budgets as the sum of both
- [ ] #4 The budget curve and the `Proportionality:` escape are unchanged
- [ ] #5 The test was seen to fail against the current `--numstat` implementation, with the mutation recorded in a `Mutation:` trailer
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
