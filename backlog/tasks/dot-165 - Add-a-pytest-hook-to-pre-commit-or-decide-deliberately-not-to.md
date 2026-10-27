---
id: DOT-165
title: Add a pytest hook to pre-commit, or decide deliberately not to
status: To Do
created_date: 2026-10-27 02:58
labels:
- planned
updated_date: 2026-10-27 22:22
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add a pytest hook to pre-commit, or decide deliberately not to. The suite
  takes ~200s measured (215s and 199.5s on 2026-09-22, `-m "not llm_judge"`,
  documented command — the earlier 104s figure could not be reproduced and is
  treated as stale), which is too slow for every commit. **Three-tier design
  settled 2026-09-22 (shift-left study, advisor council, unanimous):** fast
  deterministic hooks only at commit; the full suite as an explicit
  **merge-gate** step, not pre-push — research found a 200s pre-push hook gets
  bypassed by habit within a week, and `--no-verify` silently kills the
  lint hooks sharing that stage too; `llm_judge` tests stay excluded-and-named,
  run by deliberate manual invocation, never in an automatic gate. This
  replaces the earlier "pre-commit fast / pre-push full" framing — pre-push is
  not the gate; the merge is.
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
