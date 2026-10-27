---
id: DOT-204
title: Add a `collected == 0` tripwire
status: To Do
created_date: 2026-10-27 02:59
labels:
- planned
- group:refactor-b-factor-the-ai-llm-tooling-out-of-this-repo
updated_date: 2026-10-27 22:22
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add a `collected == 0` tripwire. A pytest hook that fails loudly if a run
  collects no tests — cheap (a few lines), and it closes the exact failure
  class already hit twice in this repo (the `clipped.bats` path pointing at a
  nonexistent binary; the empty-grep-passes pattern named in AGENTS.md §
  Prove the test fails). Named 2026-09-22 by the shift-left study's advisor
  council as the single highest payoff-per-line item researched. Done when a
  deliberately-broken test path or an empty `-k` filter is shown to fail the
  run rather than exit 0.
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
