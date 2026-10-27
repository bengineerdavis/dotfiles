---
id: TASK-151
title: '[5] Give Ansible sole ownership of `_ollama_zsh_completion`'
status: To Do
created_date: 2026-10-27 02:57
labels:
- planned
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**[5] Give Ansible sole ownership of `_ollama_zsh_completion`.** Decided.
  chezmoi was involved because the file is a symlink; removing chezmoi's claim
  ends the dual ownership and the `chezmoi apply` reverts-a-re-download
  consequence documented in `apps/ollama/tasks/install.yaml`. Note the
  inversion while working: for this file the topic-root copy is live and the
  `files/zsh/` copy is dead, backwards from every other `*.zsh`.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
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
