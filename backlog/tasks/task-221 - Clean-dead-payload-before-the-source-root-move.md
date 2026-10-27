---
id: TASK-221
title: Clean dead payload before the source-root move
status: To Do
created_date: 2026-10-27 02:59
labels:
- planned
- group:refactor-b-factor-the-ai-llm-tooling-out-of-this-repo
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Clean dead payload before the source-root move.** [prep for the
  `.chezmoiroot` refactor] Root `executable_update.sh` is managed yet
  references a nonexistent root `playbook.yaml` — it deploys to
  `$HOME/executable_update.sh` broken today. `crontab/` is fully ignored,
  its `run_onchange_after_install-crontab.sh.tmpl` never runs, and nothing
  reads it. Delete both. Done when: both gone from source, `chezmoi
  status` shows exactly the two targets as pending removals and nothing
  else, suite green. Hands the move item a payload with no known-dead
  entries. Touches managed files → PR + human review. [unclaimed]
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
