---
id: DOT-251
title: Declare backlog-md-py in the mise config to close the ownerless pipx channel
status: To Do
created_date: 2026-10-28 02:54
labels:
- tool-ownership
ordinal: 1
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
backlog-py runs on this machine from ~/.local/share/mise/installs/pipx-backlog-md-py/2.2.0 — an install no topic declares, created during the 2026-10-27 cutover outside the mise config. TOPIC-RECIPES' tool-entry-ownership rule: every tool install has an owning entry. docs/BACKLOG-CUTOVER.md already designs the fix ('pipx:backlog-md-py through mise'); this executes it. Fix: add "pipx:backlog-md-py" = "latest" to the pipx section of dotfiles/apps/mise/files/config.toml, matching the pipx:pre-commit / pipx:git-filter-repo convention. mise's pipx backend will adopt the existing install (same layout) rather than reinstall. Legacy: the backlog cutover left the tool running ownerless.
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
