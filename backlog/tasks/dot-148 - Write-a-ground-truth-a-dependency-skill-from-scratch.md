---
id: DOT-148
title: Write a `ground-truth-a-dependency` skill from scratch
status: To Do
created_date: 2026-10-27 02:57
labels:
- planned
updated_date: 2026-10-27 22:22
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Write a `ground-truth-a-dependency` skill from scratch.** The recurring need
  is what the 2026-09-12 dotagents failure took: reading a dependency's shipped
  source to find behaviour its docs never mention — an uncaught `SymlinkError`
  reaching stderr while stdout stayed empty. The method used that day is the
  whole content and owes nothing to any employer artifact: read the installed
  package rather than trusting docs, reproduce in an isolated `HOME` before
  believing a diagnosis, and mutation-test the resulting guard so a test that
  cannot fail is caught. **`what-would-kobby-do` is not a source** — it is an
  unlicensed internal tool, so it may not be read, quoted, paraphrased or
  "generalised". Name the skill for the work, not "reverse engineering", which
  drags in binary analysis and a legal frame that does not apply. Done when it
  takes an undocumented dependency failure to a cause with every claim tied to a
  file and line, authored in a session where the exclusion list below was in
  force.
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
