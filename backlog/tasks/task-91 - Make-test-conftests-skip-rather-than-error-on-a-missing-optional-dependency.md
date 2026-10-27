---
id: TASK-91
title: Make test conftests skip rather than error on a missing optional dependency
status: To Do
created_date: 2026-10-27 02:56
labels:
- now
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Make test conftests skip rather than error on a missing optional dependency.
  `tests/ollama_evals/conftest.py` loads the eval harness as a module, and the
  harness imports Pillow at module level, so without `--with pillow` the whole
  directory produces 53 collection errors instead of 52 passes — the suite
  aborts instead of running what it can. Same class as the hypothesis guard
  fixed today, one layer deeper: the import happens before pytest can skip
  anything. `pytest.importorskip` in the conftest is the likely fix, but check
  what else the harness pulls in at import time first.
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
