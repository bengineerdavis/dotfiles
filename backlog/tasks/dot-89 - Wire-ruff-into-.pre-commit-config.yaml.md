---
id: DOT-89
title: Wire `ruff` into `.pre-commit-config.yaml`
status: To Do
created_date: 2026-10-27 02:56
labels:
- now
priority: high
updated_date: 2026-10-27 22:21
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Wire `ruff` into `.pre-commit-config.yaml`. It is installed and the toolchain
  names it, but the hook config runs shellcheck and bats only, so no Python file
  in this repo is linted on commit. Settle the ruleset first — 22 scripts written
  before any linter will not pass a default config cleanly.
  mise also declares ruff twice — `ruff` (`apps/mise/files/config.toml:147`)
  and `pipx:ruff` (line 186) — so pick one first; § Now #1 (p) may pin it in
  a lock group instead.
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
