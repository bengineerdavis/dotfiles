---
id: DOT-273
title: Wire the post-apply/post-pull verification hook for chezmoi apply and chezmoi
  update
status: To Do
created_date: 2026-10-29 21:46
references:
- backlog/decisions/decision-1 - VM-verify-config-and-symlink-deployments-before-apply-merge-and-PR-gates.md
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Per decision-1: the VM-verified config gate also runs after chezmoi apply/update completes, and on git pull. Gates 1 (pre-PR) and 2 (CI) are DOT-271; this task is gate 3. Because git post-merge hooks are local config, not repo-shipped, the work must document or automate the install step (a mise task or chezmoi-managed hook) rather than assume it exists. Done when: running chezmoi apply (or update, or a pull that changes managed files) triggers the symlink and config verification automatically, proven by a broken-state run that fails the hook.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 chezmoi apply/update triggers symlink + config verification automatically on completion
- [ ] #2 a git pull that changes managed files triggers the same verification
- [ ] #3 the hook install path is documented or automated (no assume-installed local config)
- [ ] #4 a deliberately broken deployed state fails the hook loudly (mutation recorded)
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
