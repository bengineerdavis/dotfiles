---
id: DOT-379
title: Give noninteractive chezmoi drift checks a czd fallback
status: In Progress
created_date: 2026-11-19 21:28
dependencies:
- DOT-305
documentation:
- https://github.com/bengineerdavis/dotfiles/pull/190
updated_date: 2026-11-19 21:28
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
AGENTS.md directs agents to use czd, but its absence leaves no documented noninteractive fallback for a machine that has not deployed it.

Ship:

- Document a read-only chezmoi built-in-diff fallback and how to pass absolute target paths.
- Keep the czd exit-status contract distinct from chezmoi diff, which exits zero even with drift.

Constraints:

- Keep czd as the preferred command where deployed.
- Do not change the deployed czd script or run chezmoi apply.
- Verify command forms against the installed CLI help.

Agreed with the maintainer 2026-11-18: fix repository guidance and leave the external retro skill unchanged.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The guidance gives a built-in-diff command and absolute target-path example that needs no czd deployment.
- [x] #2 The guidance states that callers needing an exit status use czd when available.
- [x] #3 The fallback commands are verified against installed CLI help.
- [x] #4 skillet validate . exits 0 with no errors.
- [ ] #5 uv run --frozen pytest tests/docs -q passes.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
Handoff: PR #190 merged on 2026-11-19 as a42039eff4c98ce05e9500d96af03425de760e84. The implementation branch agent/retro-git-topic-docs at commit 245e006 was merged, and its local/remote branches and worktree were retired. skillet validate . passed and scoped link checks returned 0 errors. The full docs suite was 26 passed and 2 failed on the same .lore.md preservation cases as the unchanged base; a later HEAD check had 2 passed and 3 failed, adding [uv --frozen]. Do not hand-edit .lore.md; DOT-305 owns this class. Re-claim only to re-run uv run --frozen pytest tests/docs -q after that repair. Acceptance criterion 5 remains open.
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
PR #190 merged: chezmoi diff --use-builtin-diff -- ~/.gitconfig is documented as the read-only fallback, with czd retained for exit-status checks. The full docs-suite criterion remains open on pre-existing .lore.md preservation failures under DOT-305.
<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->
