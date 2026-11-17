---
id: DOT-369
title: Correct the home key in OpenCode template test overrides
status: To Do
created_date: 2026-11-17 16:51
updated_date: 2026-11-17 16:52
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Twelve OpenCode config tests fail because their --override-data supplies chezmoi.home while the template reads top-level .home. A direct render reproduces: map has no entry for key home.

Ship:

- Supply the template's top-level home value from the existing render seam without changing its machine-specific assertions.
- Restore the twelve failing template tests.

Constraints:

- Change test fixture data only; do not alter deployed OpenCode configuration or its permission behavior.
- Keep machine-specific paths resolved by chezmoi, not hardcoded.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The direct template render succeeds with the fixture corrected home key.
- [ ] #2 tests/topics/test_opencode_config_layers.py passes.
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
