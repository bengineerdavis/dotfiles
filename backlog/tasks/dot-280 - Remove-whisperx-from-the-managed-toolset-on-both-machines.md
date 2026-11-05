---
id: DOT-280
title: Remove whisperx from the managed toolset on both machines
status: To Do
created_date: 2026-10-30 06:38
labels:
- mise
- teardown
priority: high
orchestration:
  status_key: inprogress
  lease_owner: opencode-mise-remove-whisperx
  lease_expires_at: '2026-10-30T16:00:26.433302Z'
  version: 1
updated_date: 2026-10-30 15:10
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Author ruling 2026-10-29: drop whisperx for now on the Mac and Linux machine instead of repairing its Python 3.14 incompatibility. During the upgrade, mise uninstalled the previous working 3.8.5 before failing to resolve torch 2.8 for cp314; there is no compatible installation to preserve. Remove the managed pipx:whisperx entry and add idempotent lifecycle handling so any versions installed by this topic are removed on each machine during its next approved upgrade. Do not touch ffmpeg or other shared tools. Do not uninstall anything live or run chezmoi apply; prove the command with an isolated mise installation root and a stub tool manifest. This is a distinct removal outcome from DOT-277 (upgrade-result reporting) and will use its own worktree and PR.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The managed config no longer requests pipx:whisperx
- [ ] #2 An idempotent upgrade-path lifecycle command removes only topic-managed whisperx installs and leaves other tools and ffmpeg untouched
- [ ] #3 A missing whisperx installation relents without failing the upgrade; tests exercise removal and the absent case, with mutation evidence
- [ ] #4 Both-machine behavior follows the shared mise topic, and the task records that no live uninstall was performed
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
2026-10-30: removal tests initially failed against the old config/remove task, then 3 passed. Real Ansible runs the lifecycle with a temporary stub mise inventory: two whisperx versions are removed, ffmpeg and pipx:ruff survive, and an already-absent install relents with changed=0. Mutation making the uninstall condition false failed test_upgrade_removes_only_topic_managed_whisperx; restored implementation passed again. No real mise uninstall, playbook, or chezmoi apply was run. Full suite is running against this branch.
2026-10-30: committed agent/mise-remove-whisperx as 58442eb (four files: managed config, retirement lifecycle, real-Ansible temporary-stub tests, changelog). ruff, format, Pyrefly, documentation links, queue integrity and commit proportionality hooks passed. No live uninstall or chezmoi apply was run; the removal takes effect on each machine only after review, merge and the approved upgrade.
2026-10-30: final full suite against the committed branch: 1216 passed, 6 skipped, 8 deselected in 289.08s; skillet validate passed. Final focused run: 3 passed. PR handoff at .worktrees/mise-remove-whisperx/.review-artifacts/pr-body.md. No live uninstall or apply performed.
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->

## Run History
<!-- SECTION:RUN_HISTORY:BEGIN -->
<!-- RUN_HISTORY_ENTRY:BEGIN -->
```yaml
event_id: run-6a470c71062f46969ea5ff800fb855a8
type: claim_task
actor: opencode-mise-remove-whisperx
timestamp: '2026-10-30T15:00:26.433374Z'
result: succeeded
task_id: DOT-280
from_status: todo
to_status: inprogress
metadata:
  lease_ttl_seconds: '3600'
```
Remove whisperx from the shared mise topic for both machines in a fresh worktree
<!-- RUN_HISTORY_ENTRY:END -->
<!-- SECTION:RUN_HISTORY:END -->
