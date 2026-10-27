---
id: DOT-230
title: Adopt the 2026-10-22 machines.yml refresh into the chezmoi source
status: Done
created_date: 2026-10-27 05:29
assignee:
- opencode session
updated_date: 2026-10-27 22:22
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Deployed ~/dotfiles/machines.yml was refreshed 2026-10-22 (16 personal, 6 templates, try: xerror, forks: promptlint) but never adopted; the chezmoi source still has the sparse 2026-09-15 version, so the next chezmoi apply would silently revert the membership. Adopt deployed->source (chezmoi -S add), land by PR. All added entries are public personal/template names — spec.md § Data holds; work repos stay in the machine-local overlay. Author-flagged 2026-10-26.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 source and deployed machines.yml are byte-identical after adoption
- [ ] #2 PR merged; chezmoi status shows no machines.yml drift
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
Adopted byte-identical; PR #79 merged 61bdcc6; branch+worktree reaped. Author applied 2026-10-27: chezmoi status shows no machines.yml drift, source == deployed (verified). Both ACs met.
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->
