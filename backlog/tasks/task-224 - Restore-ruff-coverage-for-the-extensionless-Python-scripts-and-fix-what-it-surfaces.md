---
id: TASK-224
title: Restore ruff coverage for the extensionless Python scripts, and fix what it
  surfaces
status: To Do
created_date: 2026-10-27 02:59
labels:
- planned
- group:refactor-b-factor-the-ai-llm-tooling-out-of-this-repo
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Restore ruff coverage for the extensionless Python scripts, and fix
  what it surfaces.** [queued 2026-10-13; follow-up to PR #49] The ruff
  hooks now select their input by type, and pre-commit's tags come from
  identify, whose shebang detection requires the exec bit — chezmoi sources
  carry that bit in the `executable_` name prefix at mode 644, so the ~15
  extensionless Python scripts under `bin/` (8 `python3` shebangs, 6-7 PEP
  723 `uv run --script` scripts) no longer reach ruff through any hook;
  measured, `identify` tags `bin/executable_mailbox` (`#!/usr/bin/env
  python3`) non-executable and not python. Restore the coverage as a test,
  not a filter: a pytest globs `bin/` and `dotfiles/`, selects scripts
  whose first line names `python` or `uv run --script`, and runs ruff with
  the repo config — the test can decide "is this Python" by shebang, which
  neither identify nor a filename filter can do here. One finding already
  measured: `bin/executable_triage` D205 (docstring layout); fix it in the
  same change so the test lands green. Done when: the test passes on every
  selected script, has been seen to fail (mutation: make the selector match
  nothing — the grep-over-empty trap), and no hook change is needed.
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
