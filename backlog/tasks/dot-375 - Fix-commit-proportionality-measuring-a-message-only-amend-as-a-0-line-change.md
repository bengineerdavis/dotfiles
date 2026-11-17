---
id: DOT-375
title: Fix commit-proportionality measuring a message-only amend as a 0-line change
status: To Do
created_date: 2026-11-17 20:47
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Why: scripts/check_commit_proportionality.py measures `git diff --cached`, so a message-only `git commit --amend` sees 0 changed lines and a 30-word budget, then rejects a body proportionate to the real change. Measured 2026-11-17 during DOT-343: a 184-word body against a 14-line change failed with "0-line change; the budget is 30", and the workaround was a soft reset plus a fresh commit.

Ship:
- A fix so the hook judges an amend against the change the commit actually carries, not the empty index
- A regression test proving a message-only amend with a proportionate body passes

Constraints:
- The hook is a commit-time gate: a fix must not weaken it for ordinary commits (a genuinely oversized message on a small change must still fail)
- No --no-verify bypass as the resolution
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The hook passes a message-only amend whose body fits the commit's real diff size
- [ ] #2 The hook still rejects an oversized body on a genuinely small change
- [ ] #3 The regression test was seen to fail against the unfixed hook (Mutation:/Failing-test: trailers)
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
