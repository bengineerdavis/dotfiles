---
id: DOT-122
title: Migrate the mise `python.uv_venv_auto` setting before mise 2027.7.0 removes
status: To Do
created_date: 2026-10-27 02:56
labels:
- planned
updated_date: 2026-10-27 22:22
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Migrate the mise `python.uv_venv_auto` setting before mise 2027.7.0 removes
  it — mise warned the deprecation during the herdr work (2026-09-19:
  `python.uv_venv_auto=true` must become `python.uv_venv_auto="create|source"`
  or `"source"` in `apps/mise/files/config.toml`).
  **Premise suspect, 2026-09-23; refined 2026-09-28:** the key is in no
  tracked file, and `mise settings get python.uv_venv_auto` returns `false`
  on the Linux box — yet `mise ls` and `mise settings` DO still emit the
  `python.uv_venv_auto=true is deprecated` warning. So the `true` value is
  injected from somewhere unseen (a settings file, env var, or default),
  while `settings get` reads a different layer. Track down the source before
  acting.
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
