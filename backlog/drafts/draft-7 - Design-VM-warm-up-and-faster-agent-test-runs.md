---
id: draft-7
title: Design VM warm-up and faster agent test runs
status: Draft
created_date: 2026-10-29 19:00
labels:
- design
- testing
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Design draft only. Investigate VM warm-up, snapshots, prebuilt images, reusable caches, and other ways to shorten Molecule feedback for both agents and humans. Measure create, converge, idempotence, verify, and destroy separately before choosing an optimization. Define what may be reused, how images stay current, how parallel runs remain isolated, and how teardown still proves its safety. The same commands must work for a human and an agent; an agent-only warm pool is not the goal. Interview the author before implementation.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Record current timings and the safe reuse options, with one recommended design and its tradeoffs.
- [ ] #2 Define ownership, freshness, isolation, resource budgets, and teardown for any warm or cached VM state.
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
