---
id: DOT-379
title: Give noninteractive chezmoi drift checks a czd fallback
status: In Progress
created_date: 2026-11-18 06:38
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
Handoff: no active lease remains. The implementation branch agent/retro-git-topic-docs at commit 245e006 is merged through PR #190 (merge a42039ef); worktree .worktrees/retro-git-topic is clean and ready for safe removal after the remote merge is verified. Re-claim this task only to re-run uv run --frozen pytest tests/docs -q after DOT-305 restores the two inherited .lore.md anchors. Expected inherited failures are tests/docs/test_lore_md_rules_survive.py::test_rule_survives_redistillation[requires_map undefined skips removal] and [work repos never committed]. Do not hand-edit .lore.md. All other acceptance criteria are complete.
Latest main HEAD check on 2026-11-19: uv run --frozen pytest tests/docs/test_lore_md_rules_survive.py -q gives 2 passed, 3 failed. The third inherited failure is [uv --frozen]. Do not hand-edit .lore.md; DOT-305 owns this failure class.
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
PR #190 merged on 2026-11-19 as a42039eff4c98ce05e9500d96af03425de760e84. The chezmoi fallback guidance landed. Installed chezmoi diff --help confirms --use-builtin-diff and absolute target paths; the scoped ~/.commit-message-template probe returned no drift. skillet validate . passed and scoped link checks returned 0 errors. uv run --frozen pytest tests/docs -q returned 26 passed, 2 failed: the two pre-existing .lore.md preservation cases, also red on the unchanged base. Acceptance criterion 5 remains open until DOT-305 makes that full command pass; this is not a regression from the documentation change.
<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->

## Run History
<!-- SECTION:RUN_HISTORY:BEGIN -->
<!-- RUN_HISTORY_ENTRY:BEGIN -->
```yaml
event_id: run-e644da86d27040fb95491b00a08a5645
type: claim_task
actor: OpenCode retro-git-topic
timestamp: '2026-11-18T06:43:11.002376Z'
result: succeeded
task_id: DOT-379
from_status: todo
to_status: inprogress
metadata:
  lease_ttl_seconds: '3600'
```
Apply the approved chezmoi fallback guidance in the same documentation branch.
<!-- RUN_HISTORY_ENTRY:END -->
<!-- RUN_HISTORY_ENTRY:BEGIN -->
```yaml
event_id: run-1f9be1e4b8ef4727893b03caa9256d3a
type: release_task
actor: OpenCode retro-git-topic
timestamp: '2026-11-19T20:57:34.446634Z'
result: succeeded
task_id: DOT-379
from_status: inprogress
to_status: todo
```
PR #190 merged; hand off the remaining pre-existing full-docs-suite failures to DOT-305.
<!-- RUN_HISTORY_ENTRY:END -->
<!-- SECTION:RUN_HISTORY:END -->
