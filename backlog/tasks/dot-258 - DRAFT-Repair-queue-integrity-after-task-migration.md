---
id: DOT-258
title: 'DRAFT: Repair queue integrity after task migration'
status: To Do
created_date: 2026-10-28 17:47
labels:
- backlog
- process
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The full test suite on 2026-10-28 fails tests/backlog/test_queue_integrity.py::test_doctor_reports_no_problems. backlog-py warns that DOT-233 has an unterminated IMPLEMENTATION_NOTES owned section. It also reports duplicate task IDs for the old gateway/agent tasks and the newer task files. Determine the intended task ownership and migration state before editing; this is a queue-integrity repair, not permission to silently rewrite another session's in-flight task. DOT-249 records the deliberately deferred TASK-243 renumber. Decide whether that exception should remain and how to retire the other duplicate IDs. Preserve task history and other sessions' work. This is separate from the Lore gateway PR.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 backlog-py doctor reports no malformed owned sections or unintended duplicate task IDs.
- [ ] #2 The intended ownership/history of each affected task is preserved and any renumbering follows the queue migration rules.
- [ ] #3 uv run --frozen pytest tests/backlog/test_queue_integrity.py -q passes.
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
