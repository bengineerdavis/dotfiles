---
id: DOT-272
title: Verify managed symlinks resolve after payload or path changes, in the VM gate
status: To Do
created_date: 2026-10-29 21:46
references:
- backlog/decisions/decision-1 - VM-verify-config-and-symlink-deployments-before-apply-merge-and-PR-gates.md
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Per decision-1 item 2: all managed symlinks are tested by default, especially when locations change. The mise breakage came from the .chezmoiroot payload move (e9fe86b) leaving ~/.config/mise/config.toml dangling until the next apply. Work: add a post-render/post-apply verification step that enumerates chezmoi-managed symlinks and asserts each target resolves on the target environment; run it inside the VM gate (DOT-271) and as the post-apply hook (DOT-273). A dangling managed symlink must fail loudly, never warn-and-continue. Done when: the mise failure class reproduces in a test and the check rejects it.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The check enumerates all chezmoi-managed symlinks and asserts each target resolves
- [ ] #2 A deliberately dangling symlink fails the check loudly (mutation recorded)
- [ ] #3 The check runs inside the VM gate and as the post-apply hook
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
