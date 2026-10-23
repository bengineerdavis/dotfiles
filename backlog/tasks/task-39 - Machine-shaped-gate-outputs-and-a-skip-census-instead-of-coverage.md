---
id: TASK-39
title: Machine-shaped gate outputs, and a skip census instead of coverage %
status: To Do
created_date: 2026-10-23 16:49
labels:
- migration
ordinal: 37
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
From the shift-left study's advisor council: every gate (prek, pytest,
  `skillet validate`) should emit exit code + `file:line` citations + one
  JSON artifact (`pytest-json-report`) — a check without a
  machine-consumable output does not exist for an agent to act on without
  narrative. Pair it with a skip/xfail-count trend (JSONL, one line per
  run): coverage % was researched and explicitly rejected as the
  quality-over-time metric — it measures execution, not verification, and a
  `pytest.mark.skip` body counts as "covered," so a healthy-looking percentage
  can coexist with this repo's actual failure mode (tests that pass while
  testing nothing). A rising skip count is the early-warning analog of that
  failure and is the one metric the study found that directly measures it.
  **Conditional on the author actually reading the trend** — a trend file
  nobody opens within two weeks is exactly the kind of mechanism that
  shouldn't exist (PRD.md's verification-effort-scales-with-blast-radius
  governor). Done when a run emits the JSON artifact, the skip count is
  appended to a trend file, and the author has used it at least once to make
  a decision.

Legacy: TASKS.md § Now item 37 of 49, migrated to backlog 2026-10-23 (branch agent/backlog-migration).
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
