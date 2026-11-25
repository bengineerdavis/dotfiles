---
id: DOT-351
title: Report repository reconciliation without changing declarations
status: To Do
created_date: 2026-11-10 20:58
dependencies:
- DOT-306
labels:
- group:gita-and-machine-file-backup-approved-2026-09-23
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Why: Show which existing primary clones are shared, machine-specific, ignored, or unaccounted before redge-cli provides interactive adoption. Ship: A read-only reconciliation report over declarations and gita registrations, covering missing clones and drift without changing either source. Constraints: No prompts, declaration edits, automatic cloning, unregistration, or relocation. Work names stay machine-local. Linked worktrees are Git-managed and excluded from unaccounted-clone reporting. Incomplete or unreadable state is an error, not an empty result.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The report distinguishes shared, machine-specific, ignored, and unaccounted primary clones
- [ ] #2 Missing declared clones and gita registration drift are named without modifying declarations or registrations
- [ ] #3 Linked worktrees and explicitly ignored paths are not reported as unaccounted primary clones
- [ ] #4 Unreadable or incomplete state fails the report rather than appearing empty
- [ ] #5 Routine install and upgrade remain noninteractive
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
