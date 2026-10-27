---
id: DOT-117
title: Revisit the `$HOME`-exception list — reopen trigger, not a standing task
status: To Do
created_date: 2026-10-27 02:56
labels:
- planned
updated_date: 2026-10-27 22:21
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Revisit the `$HOME`-exception list — reopen trigger, not a standing task.**
  Author decision 2026-09-22: no test may touch real `$HOME` for now (find a
  workaround — mock the keychain, avoid `zsh -l` — for every case rather than
  naming exceptions), because the actual edge cases aren't known yet. Reopen
  when: the `$HOME`-sandbox fixture (§ Now, the xdist sub-item) is built and a
  real case resists sandboxing, or a second such case appears. Same shape as
  the O4/Renovate reopen trigger already used in this file — decide when the
  problem is real, not before.
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
