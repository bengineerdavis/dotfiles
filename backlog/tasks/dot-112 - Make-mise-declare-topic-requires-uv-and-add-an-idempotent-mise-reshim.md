---
id: DOT-112
title: 'Make mise declare `topic_requires: [uv]` and add an idempotent `mise reshim`'
status: To Do
created_date: 2026-10-27 02:56
labels:
- planned
updated_date: 2026-10-27 22:21
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Make mise declare `topic_requires: [uv]` and add an idempotent `mise
  reshim`.** Decision (author, 2026-09-28): a runtime tool mise calls is a
  declared dependency of the mise topic. The reshim lands after "Materialize
  mise-managed tools" so stale shims (the U1 edge case) self-heal on every
  provision. Done when mise resolves uv first in the dependency graph and a
  stale-shim machine converges to system uv on a normal run.
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
