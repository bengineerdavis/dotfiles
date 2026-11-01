---
id: DOT-280
title: Remove whisperx from the managed toolset on both machines
status: To Do
created_date: 2026-10-30 06:38
labels:
- mise
- teardown
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Author ruling 2026-10-29: drop whisperx for now on the Mac and Linux machine instead of repairing its Python 3.14 incompatibility. During the upgrade, mise uninstalled the previous working 3.8.5 before failing to resolve torch 2.8 for cp314; there is no compatible installation to preserve. Remove the managed pipx:whisperx entry and add idempotent lifecycle handling so any versions installed by this topic are removed on each machine during its next approved upgrade. Do not touch ffmpeg or other shared tools. Do not uninstall anything live or run chezmoi apply; prove the command with an isolated mise installation root and a stub tool manifest. This is a distinct removal outcome from DOT-277 (upgrade-result reporting) and will use its own worktree and PR.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The managed config no longer requests pipx:whisperx
- [ ] #2 An idempotent upgrade-path lifecycle command removes only topic-managed whisperx installs and leaves other tools and ffmpeg untouched
- [ ] #3 A missing whisperx installation relents without failing the upgrade; tests exercise removal and the absent case, with mutation evidence
- [ ] #4 Both-machine behavior follows the shared mise topic, and the task records that no live uninstall was performed
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
