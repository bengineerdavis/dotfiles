---
id: TASK-1
title: 'skill-trust resolve --revisit: change-of-mind workflow for recorded denials'
status: To Do
created_date: 2026-10-23 02:49
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Author request 2026-10-22: a user who previously denied a skill source or directory must be able to change their mind — an interactive workflow to authorize/re-authorize denied paths, not just trust remove plumbing. Scope settled with the author: 'resolve --revisit' walks store-level denials (deny_sources, deny_skills entries) showing each with its why and date, and offers keep / retract (judge on merits next run) / approve instead (source denial becomes an approval, skill denial becomes vendored), each with a fresh why recording the change of mind. Repo-level bans stay untouchable from the store (the layering rule) but are reported with where they live (rules.yaml names the topic caller) so reversal is an informed edit. Exclusions stay retractable via trust remove --exclude. Branch: the PR #71 fixes land first; this starts after merge, fresh worktree+branch per AGENTS.md.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 resolve --revisit lists store-level denials with why and date, and marks entries whose target is gone from disk
- [ ] #2 retract removes the denial (next run judges on merits); approve instead replaces it with an approval (source) or vendored entry (skill), each requiring a fresh why
- [ ] #3 repo-level denials are reported with their source (rules.yaml caller), never retracted from the store
- [ ] #4 tests seen to fail with mutation trailers; README gains the revisit workflow
- [ ] #5 PR open for human review (guard-adjacent behaviour)
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
