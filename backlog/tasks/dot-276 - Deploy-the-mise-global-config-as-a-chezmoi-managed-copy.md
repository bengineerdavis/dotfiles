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
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Per decision-1 item 5, replace the global mise config symlink with a regular chezmoi-managed copy. git pull and source edits must not change the live config; only a scoped chezmoi apply deploys it. Keep one topic-owned source of truth, preserve the separate source-tree copy, and replace PR #90 rather than rebasing its superseded symlink/ignore design. Do not run a real-home apply; prepare and verify the branch so the author can test the scoped apply on this Mac. Keep DOT-240 as the separate design decision for deliberate tool-edit capture; no new watcher or automation in this task.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A scratch-home apply produces a regular ~/.config/mise/config.toml with the topic-owned contents; a pre-existing symlink is replaced safely,Source edits do not change a previously deployed target until another apply; applying then deploys the intended content,The source-tree copy is not deployed as a second live writer and ownership documentation no longer claims source edits are immediately live,Focused and full-suite gates pass and the author receives an exact scoped-apply test command
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->

<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 The copy deployment and its negative-path behavior are proven with real chezmoi in a scratch home; the old symlink behavior is seen to fail the new tests; human review precedes merge and the author performs the real-home apply.
<!-- DOD:END -->
