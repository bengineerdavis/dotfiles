---
id: TASK-215
title: Deal with `~/dotfiles/.claude/settings.local.json`
status: To Do
created_date: 2026-10-27 02:59
labels:
- planned
- group:refactor-b-factor-the-ai-llm-tooling-out-of-this-repo
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Deal with `~/dotfiles/.claude/settings.local.json` — **80 allow rules in no
  repository at all.** `~/dotfiles` is the chezmoi deploy target and a separate
  Claude project scope, so an agent started there gets these rules and none of
  the project's. One of them is `Bash(chezmoi apply *)`, which is the rule
  `AGENTS.md` § Applying is main-only exists to prevent. Not git-tracked and not
  chezmoi-managed, so nothing versions it and no review has seen it. Decide
  whether agents should ever run there at all — if the answer is no, the fix is
  to stop, not to curate the file.
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
