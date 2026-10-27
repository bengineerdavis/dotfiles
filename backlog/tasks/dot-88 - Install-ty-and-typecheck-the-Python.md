---
id: DOT-88
title: Install `ty` and typecheck the Python
status: To Do
created_date: 2026-10-27 02:56
labels:
- now
priority: high
updated_date: 2026-10-27 22:21
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Install `ty` and typecheck the Python. Named in the house toolchain and
  currently absent — not installed, zero references in the repo. 42 test files
  and 22 Python scripts are unchecked (counted 2026-09-23: 13 `uv run
  --script`, one the stray `bin/executable_archive.bk`; 9 `python3` — the
  earlier "32" and "36" were stale). `bin/executable_scanfiles` has a
  `# /// script` block under a `python3` shebang: inert, as it declares no
  dependencies, but against the `docs/PYTHON.md` rule. Note `ty` is
  pre-1.0; decide whether it
  gates commits or just reports before wiring it into `prek`.
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
