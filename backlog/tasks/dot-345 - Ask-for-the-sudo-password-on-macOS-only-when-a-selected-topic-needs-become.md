---
id: DOT-345
title: Ask for the sudo password on macOS only when a selected topic needs become
status: To Do
created_date: 2026-11-10 17:36
labels:
- feature
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
home/dotfiles/executable_update.sh adds -K (--ask-become-pass) only on Linux. macOS topics that need root, such as softwareupdate, have no way to get a password.

Ship:

- update.sh asks for the become password, on macOS and Linux, only when a topic in the selected run declares that it needs become
- a topic.yml field (or an equivalent) that declares become need, documented in docs/TOPICS.md
- tests for both the prompt and the no-prompt path

Constraints:

- the prompt fires once per run, before any topic starts
- a run with no become topics never prompts
- secrets never touch disk
- deployed-tree change: PR
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A run that selects a become topic prompts once on macOS and on Linux
- [ ] #2 A run with no become topics does not prompt
- [ ] #3 The become field is documented in docs/TOPICS.md
- [ ] #4 The prompt and no-prompt tests were each seen to fail against a broken copy
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
