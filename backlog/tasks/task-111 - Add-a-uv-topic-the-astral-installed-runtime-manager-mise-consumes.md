---
id: TASK-111
title: Add a `uv` topic — the astral-installed runtime-manager mise consumes
status: To Do
created_date: 2026-10-27 02:56
labels:
- planned
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Add a `uv` topic — the astral-installed runtime-manager mise consumes.**
  [agent: pyproject] `topic_name: uv`, `topic_provides: [uv]`, `topic_os:
  [Darwin, Debian]`, `topic_tier: runtime-manager`. install/upgrade run the
  astral installer at latest by default (a `uv_version` variable pins); remove
  deletes `~/.local/bin/uv` and `~/.local/bin/uvx`. Decision (author,
  2026-09-28): uv is system-level and latest at the user/global level;
  projects pin their own version and mise syncs to it. Done when a fresh run
  installs uv idempotently and remove tears it down.
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
