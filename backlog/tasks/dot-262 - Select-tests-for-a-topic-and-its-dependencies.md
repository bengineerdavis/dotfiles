---
id: DOT-262
title: Select tests for a topic and its dependencies
status: To Do
created_date: 2026-10-28 23:33
labels:
- testing
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Provide a fast, explicit test-selection interface for one topic or a topic plus selected dependencies, before commits and PR creation. Extend DOT-202 file-aware fast-loop work and DOT-78 topic-local test enforcement; do not create a second test runner.

The current suite has 1169 passing tests. Agents need to run targeted suites while developing, then run the complete suite on the exact PR head before review and again on the final approved merge base. Full-suite gates must not be replaced by selection or hidden in git add.

Requirements:
- Accept a topic and optional additional topic names; include tests for their declared topic_requires dependencies when requested, rather than guessing from names.
- Map topic-owned files and shared harness changes to the relevant suites, and make that mapping reviewable and testable.
- Report the selected topics, dependency expansion, test paths, and test count before running; fail if a requested topic has no selected tests.
- Work before PR creation, including in a worktree with uncommitted changes, without installing or applying anything to the deployed tree.
- Preserve a separate full-suite gate for the PR head and for the approved final merge state. Real-model llm_judge tests remain opt-in and named.
- Prefer an existing test runner/plugin or a small wrapper around the existing pytest interface; no bespoke test framework in this dotfiles repo without author approval.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A documented command selects one topic or a topic plus requested dependencies and includes declared dependency tests.
- [ ] #2 The selection report names topics, dependencies, suites, and count; an empty selection fails instead of passing vacuously.
- [ ] #3 Topic-local and shared harness changes select their relevant tests, with mutation evidence for the selection map.
- [ ] #4 The fast path works on uncommitted worktree changes before PR creation and does not modify deployed state.
- [ ] #5 Documentation requires the full suite before PR review and again on the approved final merge state, with llm_judge tests explicitly opt-in.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
Requested by the author 2026-10-28. Related but not sufficient alone: DOT-202 fast file-aware selection, DOT-78 topic-local tests, DOT-165 commit versus merge gates. DOT-255 owns the parallel VM matrix and per-platform coverage report.
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->
