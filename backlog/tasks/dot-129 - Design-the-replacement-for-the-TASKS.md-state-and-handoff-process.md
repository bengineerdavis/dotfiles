---
id: DOT-129
title: Design the replacement for the TASKS.md state-and-handoff process
status: To Do
created_date: 2026-10-27 02:57
labels:
- planned
updated_date: 2026-10-27 22:22
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Design the replacement for the TASKS.md state-and-handoff process.** The
  queue has become a second codebase: a handoff snapshot two machines rewrite
  under each other (the 2026-09-14 merge conflict was predicted and then real),
  resolved tasks with no home (the stopgap `TASKS-RESOLVED.md` exists for
  exactly that), claims, hazards, standing reminders, and five governance docs
  all pointing at each other. Design what replaces it — what state lives
  where, how two machines merge without hand-reconciling prose, how resolution
  is recorded without growing a second file — and get the author's approval
  before cutting TASKS.md to match. Done when a written design exists, the
  author has approved it, and the re-cut file (or its successor) passes
  `tests/tasks_doc` with the resolved-tasks stopgap retired. Handoffs get an
  advisor review before taking effect — the 2026-09-14 review ran with the
  producing agent alone, exactly the self-certification the panel-of-judges
  item warns about — so the design must make the advisor pass real rather
  than optional. **Advisor pass v1 has now run** (2026-09-15): three
  fresh-context subagents — records auditor, red-team critic, cold-start
  usability — reviewed the session's records and decisions; intra-model by
  weights, independent by context and brief, and it caught real errors the
  self-review missed (a wrong diagnosis, an asymmetric routing test, a
  bypassed verification standard). Findings are applied or queued in this
  file. The design must still supply an independent-model pass and must NOT
  pre-commit whether multi-agent review beats self-review — that is the
  panel-of-judges research's measured question. [me]
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
