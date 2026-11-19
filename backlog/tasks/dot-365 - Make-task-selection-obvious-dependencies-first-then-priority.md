---
id: DOT-365
title: 'Make task selection obvious: dependencies first, then priority'
status: To Do
created_date: 2026-11-15 20:21
priority: high
updated_date: 2026-11-15 20:23
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Priority cannot break ties because almost everything carries the same grade.
Measured 2026-11-15 across the task files: 111 high, 19 medium, 2 low. A
session asking what to work on next gets no signal from the field, so
selection falls back to whatever is visible, and dependencies are read by eye.
Ordering is settled in principle — dependencies first, priority as the
tie-breaker, an explicit author override above both — but nothing states it
and nothing computes it.

Ship:

- The ordering written down: dependencies, then priority, with an author
  override outranking any grade
- A re-grade of the existing queue so priority discriminates again
- One command that answers what to work on next, respecting both rules
- The override recorded where it applies, so a reader sees why a task jumped

Constraints:

- Complement the backlog tool rather than replacing its selection: it already
  exposes dependencies, priority and orchestration eligibility
- An override is recorded with its reason; an unexplained jump is
  indistinguishable from a mistake
- Re-grading changes priority only, never status or ownership
- Changes land so the queue stays readable throughout — no bulk rewrite that
  invalidates other sessions' in-flight edits
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Task selection is defined as dependencies first, then priority as tie-breaker
- [ ] #2 A user override outranks any priority grade and is recorded as such
- [ ] #3 The priority field discriminates: the high bucket no longer holds the overwhelming majority
- [ ] #4 The next most critical task is obvious from one command
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
