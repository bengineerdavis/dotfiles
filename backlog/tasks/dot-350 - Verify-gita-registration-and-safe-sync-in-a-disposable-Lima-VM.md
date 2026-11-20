---
id: DOT-350
title: Verify gita registration and safe sync in a disposable Lima VM
status: To Do
created_date: 2026-11-10 20:58
dependencies:
- DOT-173
labels:
- group:gita-and-machine-file-backup-approved-2026-09-23
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Why: Prove the daily gita bridge behavior in an isolated guest before the author depends on it. Ship: A focused scenario using synthetic local Git repositories and the existing shared Lima lifecycle, with a short assertion-and-evidence contract. Constraints: No live-home changes, GitHub access, or real work repository names. Construct primary clones and linked worktrees inside the guest. A clean clone advances; a dirty clone is fetched but unchanged; a failed fetch is observable; work registrations remain. Destroy the guest before deleting the worktree. Automatic cloning remains outside this scenario.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A clean synthetic clone advances after a new upstream commit through the topic lifecycle
- [ ] #2 A dirty clone is fetched but its working tree and local state remain unchanged
- [ ] #3 A failed fetch produces an actionable failure report and never appears up to date
- [ ] #4 Work registrations survive synchronization and linked worktrees are not independently registered or advanced
- [ ] #5 Missing fixtures or assertions fail the scenario; cleanup destroys the guest before worktree deletion
- [ ] #6 The report records assertion ID, expected and actual results, source revision, fixture hashes, and retained evidence
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
