---
id: TASK-155
title: Move § Commit granularity and § Messages out of
status: To Do
created_date: 2026-10-27 02:57
labels:
- planned
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Move § Commit granularity and § Messages out of
  `dotfiles/docs/TOPICS.md` into `docs/COMMITS.md`. That document is
  titled "Topic conventions" and those two sections are not topic conventions —
  they are repository conventions that do not ship with the artifact, which is
  the split `docs/TOPICS.md` now describes. `AGENTS.md` § Commits cites
  them and would point at the new home.
  **Do it with the citation rewrite, not before.** 53 files reference
  `TOPICS.md`, 40 of them topic files using a deployed-tree-relative path,
  and those citations should be rewritten once rather than twice.
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
