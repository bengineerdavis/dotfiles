---
id: DOT-376
title: Reformat the three ollama_models test files that are format-dirty at HEAD
status: To Do
created_date: 2026-11-17 20:47
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Why: tests/ollama_models/test_adopt_command.py, test_comment_preservation.py and test_rewrite_units.py carry `ruff format` output in the working tree while HEAD does not, so the tree is dirty on a clean checkout and the format hook rewrites them on first touch. Measured 2026-11-17 in the shared checkout.

Ship:
- The three files reformatted and committed, so `ruff format --check` is clean at HEAD
- A note on how the drift arose, if it is discoverable

Constraints:
- Formatting only: no behaviour change, no test logic edits
- Check whether the drift is a symptom of a missing hook on whatever path writes these files before fixing it by hand
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 ruff format --check passes for tests/ollama_models at HEAD
- [ ] #2 No behaviour or assertion changes are included in the reformat commit
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
