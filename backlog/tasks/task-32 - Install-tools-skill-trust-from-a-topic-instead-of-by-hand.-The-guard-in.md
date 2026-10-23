---
id: TASK-32
title: Install `tools/skill-trust` from a topic instead of by hand.** The guard in
status: To Do
created_date: 2026-10-23 16:49
labels:
- migration
ordinal: 30
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
`roles/guards/` now shells out to it, so a machine without it provisions no
  further — correct, but the fix is currently a human running
  `uv tool install <chezmoi source>/tools/skill-trust`. That is the bootstrapping
  shape `apps/opencode`'s brew check already has: a topic should own it, and
  `tools/` will grow more inhabitants with the same need. Decide whether that is
  a `tools` topic installing everything under `tools/`, or each consumer
  declaring what it needs. Note where it lands: `tools/` sits at the chezmoi *source root*, so it
  deploys to `~/tools/`, not to `~/dotfiles/tools/` beside the Ansible tree —
  a topic would install from `~/tools/skill-trust`. Worth deciding whether it
  should deploy at all: if the tool is installed rather than cloned, the copy
  in `$HOME` is redundant and `.chezmoiignore` should skip it. Done when a fresh
  machine gets skill-trust without anyone typing a uv command. [me]

Legacy: TASKS.md § Now item 30 of 49, migrated to backlog 2026-10-23 (branch agent/backlog-migration).
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
