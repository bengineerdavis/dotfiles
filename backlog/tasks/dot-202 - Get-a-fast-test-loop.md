---
id: DOT-202
title: Get a fast test loop
status: To Do
created_date: 2026-10-27 02:59
labels:
- planned
- group:refactor-b-factor-the-ai-llm-tooling-out-of-this-repo
updated_date: 2026-10-27 22:22
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Get a fast test loop. The full suite takes ~200s measured (two runs
  2026-09-22: 215s, 199.5s; the older 104s figure is stale), which is too slow
  to run per change — at that price the loop collapses into run-once-and-hope,
  which is precisely how regressions slip through. Target a change-relevant
  subset in around ten seconds. `-m "not llm_judge"` exists already; what is
  missing is a way for an agent to select the suites matching the files it
  touched. Slowest offenders measured 2026-09-22 (`--durations`): the two
  `tests/topic_resolution/test_opencode_both_os.py` renders (18.1s, 12.4s),
  three `tests/binned/test_binned_judge.py` cases (6.7s, 6.7s, 4.5s), then a
  long ~3s tail of policy/guards subprocess tests. **Sequencing from the
  shift-left study's advisor council, unanimous: fix these five slow tests
  first (200s to an estimated ~120s serial, zero flake risk), add
  `pytest-randomly` as a cheap order-dependence detector, and only then
  consider `pytest-xdist`** — parallelizing a suite this skewed before fixing
  its outliers buys 3-4x at real flake cost for half the win a serial fix gets
  free. `pytest-testmon`/`pytest-picked` were researched and rejected for the
  file-selection half of this task: both are blind to shell/YAML/`topic.yml`
  changes (testmon traces Python coverage only; picked maps by path and
  this repo's `tests/<script>/` layout breaks that mapping), and picked can
  select zero tests and exit green — exactly this repo's signature failure
  mode. Any selection mechanism built here must therefore guard against
  silent zero-selection.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
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
