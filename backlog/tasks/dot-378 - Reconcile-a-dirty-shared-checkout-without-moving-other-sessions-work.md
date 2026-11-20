---
id: DOT-378
title: Reconcile a dirty shared checkout without moving other sessions work
status: In Progress
created_date: 2026-11-18 06:37
orchestration:
  status_key: todo
  version: 2
updated_date: 2026-11-19 20:57
dependencies:
- DOT-305
documentation:
- https://github.com/bengineerdavis/dotfiles/pull/190
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
Handoff: no active lease remains. The implementation branch agent/retro-git-topic-docs at commit 245e006 is merged through PR #190 (merge a42039ef); worktree .worktrees/retro-git-topic is clean and ready for safe removal after the remote merge is verified. Re-claim this task only to re-run uv run --frozen pytest tests/docs -q after DOT-305 restores the two inherited .lore.md anchors. Expected inherited failures are tests/docs/test_lore_md_rules_survive.py::test_rule_survives_redistillation[requires_map undefined skips removal] and [work repos never committed]. Do not hand-edit .lore.md. All other acceptance criteria are complete.
Latest main HEAD check on 2026-11-19: uv run --frozen pytest tests/docs/test_lore_md_rules_survive.py -q gives 2 passed, 3 failed. The third inherited failure is [uv --frozen]. Do not hand-edit .lore.md; DOT-305 owns this failure class.
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
PR #190 merged on 2026-11-19 as a42039eff4c98ce05e9500d96af03425de760e84. The shared-checkout procedure and agent pointer landed. skillet validate . passed and scoped link checks returned 0 errors. uv run --frozen pytest tests/docs -q returned 26 passed, 2 failed: the two pre-existing .lore.md preservation cases, also red on the unchanged base. Acceptance criterion 5 remains open until DOT-305 makes that full command pass; this is not a regression from the documentation change.
<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->

## Run History
<!-- SECTION:RUN_HISTORY:BEGIN -->
<!-- RUN_HISTORY_ENTRY:BEGIN -->
```yaml
event_id: run-95c12330cd8c47bdaadfee917456432a
type: claim_task
actor: OpenCode retro-git-topic
timestamp: '2026-11-18T06:43:10.344804Z'
result: succeeded
task_id: DOT-378
from_status: todo
to_status: inprogress
metadata:
  lease_ttl_seconds: '3600'
```
Apply the approved shared-checkout guidance fix in an isolated documentation branch.
<!-- RUN_HISTORY_ENTRY:END -->
<!-- RUN_HISTORY_ENTRY:BEGIN -->
```yaml
event_id: run-5cb0c11421854486a0c5673923bc3e88
type: release_task
actor: OpenCode retro-git-topic
timestamp: '2026-11-19T20:57:33.660864Z'
result: succeeded
task_id: DOT-378
from_status: inprogress
to_status: todo
```
PR #190 merged; hand off the remaining pre-existing full-docs-suite failures to DOT-305.
<!-- RUN_HISTORY_ENTRY:END -->
<!-- SECTION:RUN_HISTORY:END -->
