---
id: DOT-370
title: Say in CROSS-PLATFORM.md which sed dialect each macOS context gets
status: To Do
created_date: 2026-11-17 17:19
dependencies:
- DOT-368
labels:
- docs
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
docs/CROSS-PLATFORM.md says BSD and GNU flags differ but not which one this fleet's Macs use. An agent wrote BSD `sed -i ''` on 2026-11-17 where interactive zsh had GNU sed (retro, ses_e398d0a9).

Ship:

- one paragraph under § Command flags: GNU-first is deliberate (decision-6), it holds only in interactive zsh until DOT-368 lands, and agents check with `<tool> --version` instead of assuming

Constraints:

- docs-only diff: branch `docs-gnu-dialect`, the doc-link tests and `skillet validate .` gate it
- once DOT-368 merges, drop the "interactive only" caveat in the same PR or a follow-up
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 § Command flags names decision-6, the contexts that get GNU, and the --version check
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
