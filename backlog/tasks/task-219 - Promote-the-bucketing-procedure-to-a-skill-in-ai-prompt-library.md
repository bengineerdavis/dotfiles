---
id: TASK-219
title: Promote the bucketing procedure to a skill in `ai-prompt-library`
status: To Do
created_date: 2026-10-27 02:59
labels:
- planned
- group:refactor-b-factor-the-ai-llm-tooling-out-of-this-repo
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Promote the bucketing procedure to a skill in `ai-prompt-library`.**
  Author-chosen 2026-09-24 over docs-only and a tool requirement. The steps in
  `docs/WORKTREES.md` § Bucketing are repo-agnostic, so a skill carries them to
  every repo an agent works in. Per AGENTS.md § Observations are deliverables,
  promote once the practice has earned its keep: trigger is PR #11 and #12
  reaching merge through the procedure, so the skill is written from two real
  cycles (PR #5's split, and that merge) rather than one. Lives in
  `ai-prompt-library`, not here. Automating the checks (bucket detection,
  merge-tree in every order, combined suite) is a separate, later requirement
  for the merge-gate checker above.
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
