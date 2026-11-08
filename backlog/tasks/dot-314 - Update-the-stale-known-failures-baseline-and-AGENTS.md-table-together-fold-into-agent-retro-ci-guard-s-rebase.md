---
id: DOT-314
title: Update the stale known-failures baseline and AGENTS.md table together — fold
  into agent/retro-ci-guard's rebase
status: To Do
created_date: 2026-11-08 20:55
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Both hand-maintained copies of the known-failures list are stale post-#114 (DOT-73 fixed every clipped failure) and post-#139 (the drift test now enforces their consistency): (1) scripts/check_suite_baseline.py EXPECTED_FAILURES still pins the 12 pre-DOT-73 exact node IDs (10 tests/clipped/test_clipped_cli.py + 2 tests/restart_stale/test_role.py) — all now passing, so every entry reports as expected-but-absent (nonfatal by design, but the baseline describes nothing real); (2) AGENTS.md § Known failures table still lists tests/clipped ~10 + tests/restart_stale 2 with the pre-DOT-73 '12 failed, 1093 passed, 20 skipped' shape and the --ignore fast-loop advice. FOLD DIRECTIVE (author, 2026-11-08): this lands as part of agent/retro-ci-guard's rebase onto current main — the branch is author-authored outside the DOT-73 session (6 commits: 191ed9b ci: run the suite judge by failure list, fe61f44 tests: Python floor sweep relative paths, fec0c13 ci: pin upload-artifact SHA, cec25c5 ci: fetch lint history, 7adfa35 ci: install test group + pyrefly from named source, 08c1f14 ci: exact node IDs + errors as failures; remote at 42773ab, no PR yet) and already owns the EXPECTED_FAILURES rework. The two copies must move together: edit table in PR -> drift test fails -> EXPECTED_FAILURES follows in the same change -> CI enforces (the update mechanism PR #139 landed). Also fold here (author directive): check_suite_baseline.py empty-run hole — pytest on an empty dir (rc=5, 'no tests ran') passes the gate green; fix direction recorded at .lore.md:180 (2026-11-06): count-mismatch validation (nonzero failed/error in summary + zero parsed outcome lines = incomplete evidence), NOT unconditional outcome-line demand (all-passed runs legitimately have none); test blind spot: test_no_summary_line_is_not_a_pass feeds 'collection error: no tests ran' — prefix blocks the regex, passes while real pytest output slips through. One change, one reviewer: CI-gate hardening as a unit.
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
