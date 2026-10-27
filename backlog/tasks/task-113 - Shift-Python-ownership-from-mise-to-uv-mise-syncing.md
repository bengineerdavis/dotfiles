---
id: TASK-113
title: Shift Python ownership from mise to uv, mise syncing
status: To Do
created_date: 2026-10-27 02:56
labels:
- planned
- blocked
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Shift Python ownership from mise to uv, mise syncing.** Decision
  (author, 2026-09-28): uv is the better Python env manager. `uv python
  install X` installs, `mise sync python --uv` shares it, `mise use -g
  python@X` selects it; mise runs uv beneath and integrates Python with the
  other runtimes. Today `python = "3.14"` is mise-managed and mise
  `topic_provides: [python]`. Also set `python.uv_venv_auto = "source"` — the
  cookbook's non-deprecated form, which clears the stray deprecation warning
  (traced to `pypi.uvx = true`, not a config key). Done when Python installs
  via uv, is available to mise via sync, and the two no longer fight over the
  version. [blocked: the uv topic lands first]
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
