---
id: DOT-276
title: Deploy the mise global config as a chezmoi-managed copy
status: To Do
created_date: 2026-10-30 03:28
assignee:
- opencode
labels:
- mise
- chezmoi
- config
priority: high
references:
- decision-1
orchestration:
  status_key: inprogress
  lease_owner: opencode-mise-copy
  lease_expires_at: '2026-10-30T04:29:17.488808Z'
  version: 1
updated_date: 2026-10-30 04:06
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Per decision-1 item 5, replace the global mise config symlink with a regular chezmoi-managed copy. git pull and source edits must not change the live config; only a scoped chezmoi apply deploys it. Keep one topic-owned source of truth, preserve the separate source-tree copy, and replace PR #90 rather than rebasing its superseded symlink/ignore design. The branch must be reviewed and merged before the author applies the deployed config from main; no unmerged-branch apply to the real home. Keep DOT-240 as the separate design decision for deliberate tool-edit capture; no new watcher or automation in this task.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A scratch-home apply produces a regular ~/.config/mise/config.toml with the topic-owned contents; a pre-existing symlink is replaced safely,Source edits do not change a previously deployed target until another apply; applying then deploys the intended content,The source-tree copy is not deployed as a second live writer and ownership documentation no longer claims source edits are immediately live,Focused and full-suite gates pass and the author receives an exact scoped-apply test command
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
2026-10-29: closed PR #90 as superseded with a link to this task. Public-seam tests run real chezmoi apply in scratch homes. Before conversion: 3 failed (regular-file/source-edit isolation, old-symlink replacement, and no remaining symlink_ entries). After the copy template conversion: 3 passed. Temporary restoration of the symlink implementation also failed all three tests, then was reverted. Focused suite: 23 passed; Ruff, formatting, and skillet validation passed. Rendered target equals the topic-owned config byte-for-byte. No real-home apply was run. Source comments now state that mise use -g changes only the deployed copy; DOT-240 remains the deliberate-capture design.
2026-10-29: committed agent/mise-copy-deploy at 92e4735 (seven files: copy template, regression tests, ownership docs, changelog). Pre-commit ruff, ruff format, Pyrefly, documentation links, queue integrity, and proportionality passed. The author-facing test is deliberately scoped to ~/.config/mise/config.toml using -S "$PWD/home"; no real-home apply was run by the agent. The test guide proves regular-file conversion, unchanged operation of mise/backlog-py, and that a source-only edit waits for apply. It also supplies a restore command for the current main symlink if needed.
2026-10-29 sequencing correction: the author ruled that the global mise config fix must land before local testing; an unmerged branch must not be applied to the real home. The implementation remains scratch-home tested and will go through PR review and merge first. Only then will the author run the scoped apply from main. Full suite: 1213 passed, 6 skipped, 8 deselected in 290.14s; skillet validate passed. Live baseline before PR: readable mise symlink, mise 2026.10.17 and backlog-py 2.2.0 working, no scoped chezmoi status drift.
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 The copy deployment and its negative-path behavior are proven with real chezmoi in a scratch home; the old symlink behavior is seen to fail the new tests; human review precedes merge and the author performs the real-home apply.
<!-- DOD:END -->

## Run History
<!-- SECTION:RUN_HISTORY:BEGIN -->
<!-- RUN_HISTORY_ENTRY:BEGIN -->
```yaml
event_id: run-7d936764f8e844b5be9a08dacd51b6f5
type: claim_task
actor: opencode-mise-copy
timestamp: '2026-10-30T03:29:17.488895Z'
result: succeeded
task_id: DOT-276
from_status: todo
to_status: inprogress
metadata:
  lease_ttl_seconds: '3600'
```
Implement copy deployment in .worktrees/mise-copy-deploy for author testing before merge
<!-- RUN_HISTORY_ENTRY:END -->
<!-- SECTION:RUN_HISTORY:END -->
