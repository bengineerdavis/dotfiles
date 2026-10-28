---
id: DOT-252
title: Fix the two pre-existing test_opencode_tiers failures (chezmoi apply block
  cases)
status: To Do
created_date: 2026-10-28 02:55
labels:
- policy
ordinal: 1
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
tests/permissions/test_opencode_tiers.py::test_both_blocks fails for the 'chezmoi apply ~/dotfiles-top-level' and 'chezmoi apply ~/dotfiles-autonomous' cases — found 2026-10-28 on main while gating PR #93 (2 failed, 1148 passed). The test expects these patterns to be BLOCKED by the opencode permission tiers; main's config no longer blocks them (or the fixture drifted). Read which side moved: if the config widened deliberately, update the test's expectation with the author's ruling recorded; if it widened silently, restore the block. Note: 'chezmoi apply' blocks are the last line of defense for the apply-tier rule — treat a silent widening as a policy regression, not a test chore.
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
