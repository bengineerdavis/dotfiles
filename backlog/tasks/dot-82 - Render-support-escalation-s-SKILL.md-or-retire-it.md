---
id: DOT-82
title: Render `support-escalation`'s SKILL.md, or retire it
status: To Do
created_date: 2026-10-27 02:55
labels:
- now
priority: high
updated_date: 2026-10-27 22:21
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Render `support-escalation`'s SKILL.md, or retire it.** Moving it into
  `ai-prompt-library` on 2026-09-12 revealed it had never been a working skill:
  spec.md, 5 eval fixtures and a legacy `.skillet.yaml`, but no SKILL.md, so
  nothing could load it — it sat in the user-global path for two weeks doing
  nothing. `skillet status skills/support-escalation` will report the legacy
  format first; migrate that before rendering. Until a SKILL.md exists dotagents
  cannot discover it, which is the correct state for something unfinished. Done
  when `skillet validate` passes and it installs from the wildcard, or the
  directory is deleted and this line with it. [me]
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
