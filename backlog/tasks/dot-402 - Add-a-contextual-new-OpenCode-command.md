---
id: DOT-402
title: Add a contextual /new OpenCode command
status: To Do
created_date: 2026-11-24 22:04
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Ship a global OpenCode /new command that names the current session from HANDOFF.md or other project context, then resumes that work. Manual counterpart to DOT-344, which titles a session automatically when it claims a task.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The command deploys to ~/.config/opencode/commands/new.md through chezmoi and is discovered by OpenCode as /new.
- [ ] #2 It names a session from project context, falls back when no HANDOFF.md exists, and accepts $ARGUMENTS.
- [ ] #3 It makes no git mutations unless the user asks.
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
