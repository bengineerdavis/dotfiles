---
id: DOT-173
title: G4 — safely synchronize existing gita registrations
status: To Do
created_date: 2026-10-27 02:58
labels:
- planned
- group:gita-and-machine-file-backup-approved-2026-09-23
updated_date: 2026-11-10 20:56
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Ship safe synchronization for existing gita registrations on --tags upgrade. PR #152 supplies registration; automatic cloning in DOT-172 is not a prerequisite. Fetch every primary clone, including dirty and machine-local work registrations. Advance only clean, attached, non-diverged clones with an upstream through git merge --ff-only. Never merge, rebase, reset, stash, or relocate local work. Linked worktrees stay under Git and are not separately registered or advanced. Record per-repository fetch and blocked state; a failed fetch leaves freshness unknown and does not advance last-fetch. Report concise success and actionable per-repository exceptions. Repository-local problems do not abort later repositories or topics; provider and configuration defects fail the topic run. The bounded Ansible exception and eventual redge-cli handoff are recorded in decision-5. Prove behavior with synthetic repositories and deliberate mutations; VM execution is a separate verification task.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Every existing primary gita registration is fetched, including dirty and machine-local work registrations
- [ ] #2 Only clean attached non-diverged clones with an upstream advance through git merge --ff-only; local work is never merged, rebased, reset, stashed, or relocated
- [ ] #3 A failed fetch leaves freshness unknown and does not advance last-fetch
- [ ] #4 Dirty detached diverged no-upstream and mid-operation clones retain their state and receive explicit per-repository verdicts
- [ ] #5 A repository-local problem does not prevent later repositories or topics from running; provider and configuration defects fail the topic run
- [ ] #6 Linked worktrees remain Git-managed and are not independently registered or advanced
- [ ] #7 Routine success reports a concise summary and exceptions identify their repositories and reasons
- [ ] #8 Deliberate mutations prove a clean clone advances, a dirty clone is fetched but unchanged, and a failed fetch cannot appear up to date
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
Author decision, 2026-11-10: gita is the useful interim bridge; redge-cli is not a prerequisite. The existing PR #152 registration is the prerequisite, not DOT-172 automatic cloning. Preserve the topic-level lifecycle commands while improving their implementation. Synchronize gita's actual existing registrations, including the machine-local work group and manually registered primary clones, not only committed catalogue entries. Fetch every primary clone. Advance only clean, attached, non-diverged clones with an upstream using git merge --ff-only; do not merge, rebase, reset, stash, or relocate local work. Linked worktrees are Git-managed: do not treat them as separate gita registrations or fast-forward them independently; fetch their primary clone without touching any checked-out worktree. Failed fetch means unknown freshness and never advances last-fetch. Report per-repository outcomes; routine success is a concise summary with details for repositories needing attention. Individual repository problems stay non-aborting; missing gita/git, unreadable registration state, or malformed configuration fail the topic run. The existing gita pull path deliberately does not pass --rebase; preserve that safety property when replacing it. This transitional per-repository Git behavior is an explicit exception to docs/research/repo-manager/SPEC.md Boundary, limited to registration and safe synchronization. Declaration CRUD, interactive adoption, and remote discovery stay outside Ansible for redge-cli. VM verification is queued separately; do not claim live synchronization success without the synthetic clean/dirty/failed-fetch tests. Design record: decision-5.
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->
