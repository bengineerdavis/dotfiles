---
id: DOT-313
title: A declared hook stage with a foreign shim is silently dead
status: To Do
created_date: 2026-11-08 20:46
labels:
- hooks
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Measured 2026-11-07 on this machine. .pre-commit-config.yaml declared docs-links-full and branch-sync at stages: [pre-push]. Neither had ever run: .git/hooks/pre-push was roborev's shim, which only calls roborev post-commit --flush-push and contains zero references to prek or pre-commit. core.hooksPath is unset, so nothing else supplied the stage.

The same defect hid a second dead stage: .git/hooks/commit-msg was absent entirely, so commit-proportionality has never run either.

Found only because a push that should have been refused succeeded. The config parses correctly, which is exactly what makes the gap invisible: a hook that cannot fire is indistinguishable from a hook that passed, and no local documentation existed to prompt the check (DOT-59, retire pipx pre-commit for prek, is still To Do).

Fixed on PR #131 by giving pre-push one owner: roborev's flush moved into a prek hook entry and prek's shim installed. Verified by running the stage, where branch-sync and roborev-flush both execute and docs-links-full ran for the first time.

Remaining work: a check that fails when a declared stage has no live shim, and the same for commit-msg. Done when a deliberately-uninstalled stage fails loudly rather than passing silently.
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
