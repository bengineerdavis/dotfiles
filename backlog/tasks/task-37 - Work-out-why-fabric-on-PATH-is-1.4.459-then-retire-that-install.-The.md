---
id: TASK-37
title: Work out why `fabric` on `$PATH` is 1.4.459, then retire that install.** The
status: To Do
created_date: 2026-10-23 16:49
labels:
- migration
ordinal: 35
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
orphaned `v1.4.478` tree is gone (72M reclaimed, `mise` took its `v1`/`v1.4`/
  `vlatest` symlinks with it), leaving `1.4.459` beside the current `1.4.478`.
  `1.4.459` is not safe to remove yet: it is the copy on `$PATH` in at least one
  running shell, even though `mise which`, `mise env` and `mise ls` all agree on
  1.4.478 and nothing in this repo writes the stale entry. Looks like
  session-inherited env rather than config, but that was **not** confirmed — a
  clean shell had no fabric on `PATH` at all, so the test proved nothing. Done
  when a brand-new terminal is checked: if it reports 1.4.478 this was stale env
  and `mise uninstall github:danielmiessler/fabric@1.4.459` closes it out; if it
  reports 1.4.459 something is writing that path and the uninstall would break
  a working command.

Legacy: TASKS.md § Now item 35 of 49, migrated to backlog 2026-10-23 (branch agent/backlog-migration).
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
