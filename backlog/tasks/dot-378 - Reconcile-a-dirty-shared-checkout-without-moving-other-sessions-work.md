---
id: DOT-378
title: Reconcile a dirty shared checkout without moving other sessions work
status: In Progress
created_date: 2026-11-19 21:27
dependencies:
- DOT-305
documentation:
- https://github.com/bengineerdavis/dotfiles/pull/190
updated_date: 2026-11-19 21:28
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
- [x] #1 The detailed worktree procedure says how to inspect sessions by exact checkout and distinguish coordination from independent work.
- [x] #2 The procedure preserves unrelated dirty files and stops for overlapping dirty paths without restoring another session's file.
- [x] #3 The existing agent guidance points to the detailed procedure.
- [x] #4 skillet validate . exits 0 with no errors.
- [ ] #5 uv run --frozen pytest tests/docs -q passes.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
Handoff: PR #190 merged on 2026-11-19 as a42039eff4c98ce05e9500d96af03425de760e84. The implementation branch agent/retro-git-topic-docs at commit 245e006 was merged, and its local/remote branches and worktree were retired. skillet validate . passed and scoped link checks returned 0 errors. The full docs suite was 26 passed and 2 failed on the same .lore.md preservation cases as the unchanged base; a later HEAD check had 2 passed and 3 failed, adding [uv --frozen]. Do not hand-edit .lore.md; DOT-305 owns this class. Re-claim only to re-run uv run --frozen pytest tests/docs -q after that repair. Acceptance criterion 5 remains open.
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
PR #190 merged: shared-checkout guidance now filters by exact checkout, preserves unrelated dirty files, and stops on overlapping paths. The full docs-suite criterion remains open on pre-existing .lore.md preservation failures under DOT-305.
<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->
