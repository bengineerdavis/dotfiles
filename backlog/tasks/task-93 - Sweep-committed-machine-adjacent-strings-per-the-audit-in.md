---
id: TASK-93
title: Sweep committed machine-adjacent strings, per the audit in
status: To Do
created_date: 2026-10-27 02:56
labels:
- now
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Sweep committed machine-adjacent strings, per the audit in
  `dotfiles/docs/MULTI-MACHINE.md` (2026-09-12). The audit found: employer-
  adjacent paths (`~/code/work/sentry/`, `sfw.security.sentry.io`), the §
  Private tasks section describing the work it points to (obfuscation that
  signals itself), environment mentions ("work machine", "the second
  machine", "a Seer clone", "the work workspace"), and session-claim
  provenance narration. Rewrites generalize to environment-neutral classes;
  the purge of employer strings itself stays under § Private tasks. Done
  when a grep over the committed tree for the audit's patterns comes back
  clean and the MULTI-MACHINE design's generalization test is applied to
  every rewritten line. **Wait for the council verdict first** — the council
  may change what "bounded pointer" means before the sweep rewrites
  pointers.
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
