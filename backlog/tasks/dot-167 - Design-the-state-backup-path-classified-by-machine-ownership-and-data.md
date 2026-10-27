---
id: DOT-167
title: Design the state backup path, classified by machine ownership and data
status: To Do
created_date: 2026-10-27 02:58
labels:
- planned
updated_date: 2026-10-27 22:22
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Design the state backup path, classified by machine ownership and data
  sensitivity. **First slice approved 2026-09-23: BK1–BK4 below cover
  configuration backups**, under `PRD.md` § Configuration backups. They must
  pass their restore drills before real data enters the new machine files.
  The broader state design stays open: identify expensive-to-regenerate
  state (model weights, eval results, benchmark history), apply `spec.md`
  § Data to usage-derived content, and regenerate everything else. The
  configuration exception does not relax the internal-disk rules for other
  data. The AI state-contract item B3 precedes backing up those stores,
  not the machine-file slice. Done when the remaining stores have owners,
  retention rules and permitted destinations, and implementation tasks are
  queued. No backup mechanism has been verified yet. [me]
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
