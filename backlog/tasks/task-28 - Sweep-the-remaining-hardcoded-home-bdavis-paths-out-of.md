---
id: TASK-28
title: Sweep the remaining hardcoded `/home/bdavis` paths out of
status: To Do
created_date: 2026-10-23 16:49
labels:
- migration
ordinal: 26
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
`dot_zshrc.tmpl`.** Four of them, all inside the `{{ if eq .chezmoi.os
  "linux" }}` block (lines 69–459), so none render on macOS and none are broken
  today — they are correct only because the Debian box's username happens to be
  `bdavis`, which is precisely the failure the new convention in `AGENTS.md`
  § "Machine-specific values are resolved, never written out" exists to stop.
  Lines 331 and 355 both prepend `/home/bdavis/.local/bin` to `PATH` and can
  simply go: `~/.local/bin` is already on `PATH` via `zsh/path.zsh`, verified on
  this Mac. Line 381 sources the broot launcher by absolute path and needs
  `{{ .chezmoi.homeDir }}` or `$HOME`. Lines 89 and 267 are cosmetic — a
  compinstall marker and a shellcheck `source=` hint — and the real `source` on
  267 already uses `~`. Cannot be verified from this Mac: the block only renders
  on Debian, so `chezmoi execute-template` with a forced OS, or a check on the
  box itself, is the proof. Done when no `/home/` literal remains in the
  template and the rendered Debian output still sources broot and resolves
  `~/.local/bin`.

Legacy: TASKS.md § Now item 26 of 49, migrated to backlog 2026-10-23 (branch agent/backlog-migration).
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
