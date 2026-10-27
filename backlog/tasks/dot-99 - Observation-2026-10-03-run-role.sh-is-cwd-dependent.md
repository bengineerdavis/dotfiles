---
id: DOT-99
title: 'Observation, 2026-10-03: run-role.sh is cwd-dependent'
status: To Do
created_date: 2026-10-27 02:56
labels:
- now
priority: high
updated_date: 2026-10-27 22:21
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Observation, 2026-10-03: run-role.sh is cwd-dependent.**
  `dotfiles/executable_run-role.sh uv` from the repo root fails with
  "no such topic playbook: apps/uv/playbook.yaml" — the script resolves
  `apps/<topic>/playbook.yaml` relative to cwd, so it only works when run
  from inside dotfiles/ (AGENTS.md § Commands reads as if run from the
  root). One-line fix: `cd "$(dirname "$0")"` after set -euo pipefail.
  Deployed-tree file, so the fix goes to the author for review.
  Fix ready 2026-10-09 on branch `run-role-cwd-fix` with
  `tests/run_role/` (real script from a foreign cwd against a fake mise
  recording its argv: foreign-cwd resolution, unknown-topic error naming,
  second arg as `--tags`). Mutation-verified: with the `cd` line removed,
  the foreign-cwd and tags tests go red; the unknown-topic test correctly
  stays green (it asserts error naming, not cwd). PR to follow.
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
