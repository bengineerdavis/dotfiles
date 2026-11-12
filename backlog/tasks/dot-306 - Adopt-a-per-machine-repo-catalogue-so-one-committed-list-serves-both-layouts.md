---
id: DOT-306
title: Adopt a per-machine repo catalogue so one committed list serves both layouts
status: To Do
created_date: 2026-11-08 16:54
updated_date: 2026-11-10 20:56
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Resolve shared repository identities through per-machine layouts, using option (b) from decision-5. Keep one committed registry of shared identities and allow unversioned local additions. Do not restore repository membership in machines.yml. Do not relocate the Linux inventory first, silently drop absent clones, or clone them automatically. Add the six approved existing Mac personal/fork clones as shared declarations after path resolution. Linked worktrees are Git-managed, not independent registry entries; their primary clone is the synchronization target. The bridge supports existing clones now and gives redge-cli a stable registry foundation later.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Both recorded machine layouts resolve the same shared identities without relocation
- [ ] #2 An absent clone is reported missing with its resolved path and is not cloned automatically
- [ ] #3 Local additions stay machine-specific and linked worktrees remain Git-managed
- [ ] #4 Decision-5 records option (b) and both rejected alternatives
- [ ] #5 Isolated tests cover both layouts, local additions, missing clones, and the six approved shared declarations
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
Author decision, 2026-11-10: choose option (b), per-machine path resolution without per-machine shared membership. Rejected: relocating the Linux inventory first; accepting unresolved repositories on one machine. Shared means manage wherever a clone exists, not clone everywhere. An absent clone is reported missing with its resolved path. Automatic cloning remains DOT-172. Add personal/backlog-md-py, personal/flagship, personal/roborev, forks/loreai, forks/opencode, forks/skillet after the resolver maps their paths. Ignore linked worktrees as independent declarations. Use recorded Linux inventory and isolated fixtures; do not change live-home state. See decision-5.
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->
