---
id: DOT-214
title: Rebuild the 64 allow rules in `~/.claude/settings.json`
status: To Do
created_date: 2026-10-27 02:59
labels:
- planned
- group:refactor-b-factor-the-ai-llm-tooling-out-of-this-repo
updated_date: 2026-10-27 22:22
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Rebuild the 64 allow rules in `~/.claude/settings.json`. One of four settings scopes on this machine (257 allow rules
  in total). Machine-local, applies to **every** project including work repositories, and deliberately left alone
  when the project config was rebuilt — changing it from inside this repo would
  have silently altered agent behaviour in `~/code/work/`. Same approach as
  `docs/PERMISSIONS.md`, but the allow set has to serve repos this one
  knows nothing about, so start by finding out which projects depend on it.
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
