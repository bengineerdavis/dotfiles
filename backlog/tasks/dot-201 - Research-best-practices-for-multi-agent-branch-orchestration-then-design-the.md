---
id: DOT-201
title: Research best practices for multi-agent branch orchestration, then design the
status: To Do
created_date: 2026-10-27 02:58
labels:
- planned
- group:refactor-b-factor-the-ai-llm-tooling-out-of-this-repo
updated_date: 2026-10-27 22:22
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Research best practices for multi-agent branch orchestration, then design the
  state file. Wanted: a file the orchestrating agent maintains that records which
  branch each work item is on, what it is based on, and what needs rebasing when
  main moves — so a subagent is handed a rebase instead of discovering a conflict
  mid-task. Stress-testing branch-per-item already surfaced what it must handle:
  stacked branches for dependent items (A3 on A2), items that must not be split
  (the original B4/B5 cut), shared `conftest.py` fixtures, and governance-doc collisions across
  unrelated branches. Use the questioning skill in
  `~/code/personal/ai-prompt-library`. Should land before more than two agents
  run in parallel.
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
