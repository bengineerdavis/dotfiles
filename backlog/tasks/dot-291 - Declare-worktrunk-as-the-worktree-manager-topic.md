---
id: DOT-291
title: Declare worktrunk as the worktree manager topic
status: To Do
created_date: 2026-11-01 19:05
labels:
- dotfiles
- tooling
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Install worktrunk (wt) via mise/cargo and wire its shell integration declaratively through the dotfiles. References: https://worktrunk.dev/#install — 'cargo install worktrunk && wt config shell install'. Author-authorized follow-up: reuse the pattern of capturing command output (like wt config shell install prints) so setup becomes declarative — the capture/templating portion needs discussion with the author before implementation. Likely shape: apps/worktrunk topic with install + shell-integration tasks; the captured-output-to-template decision is the open design question.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A worktrunk topic installs the binary through mise (or documents why cargo directly) and is removable via the topic
- [ ] #2 Shell integration is declared, not hand-run: the install-time output is captured and reproduced by the topic, with the capture-vs-template approach agreed with the author first
- [ ] #3 Existing worktree flows (manual git worktree, .worktrees/ pattern) are either migrated to wt or explicitly kept, with the decision recorded
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
