---
id: DOT-378
title: Reconcile a dirty shared checkout without moving other sessions work
status: To Do
created_date: 2026-11-18 06:37
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Global session activity does not identify which files another session owns, and restoring another session's dirty task file risks losing its edits.

Ship:

- Document checkout-specific session inspection, merge with unrelated dirt intact, and a stop condition for overlapping dirty paths.
- Point agents to the detailed shared-checkout procedure from the existing working-alongside guidance.

Constraints:

- Do not clean, restore, stash, or commit another session's changes.
- Use the installed OpenCode API and Worktrunk help as evidence; do not build a session-waiting tool.
- Governance changes land through a branch and pull request.

Agreed with the maintainer 2026-11-18: apply the retro finding to repository guidance rather than editing the external retro skill.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The detailed worktree procedure says how to inspect sessions by exact checkout and distinguish coordination from independent work.
- [ ] #2 The procedure preserves unrelated dirty files and stops for overlapping dirty paths without restoring another session's file.
- [ ] #3 The existing agent guidance points to the detailed procedure.
- [ ] #4 skillet validate . exits 0 with no errors.
- [ ] #5 uv run --frozen pytest tests/docs -q passes.
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
