---
id: DOT-372
title: Bind push approvals to the exact commits the author saw
status: To Do
created_date: 2026-11-17 20:46
labels:
- process
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
On 2026-11-17 an agent made two pushes on one approval, and both pushes carried other sessions' commits that landed after the author said yes (retro, ses_e398d0a9). This agent's profile allows `git push *` (opencode.jsonc:476), so only judgement stood in the way.

Ship:

- AGENTS.md § push handoff: a push handoff names the exact sha shown to the author, `git push origin <sha>:refs/heads/<branch>`, so commits that land after approval stay local
- the rule says one approval covers one push; a second push needs its own approval

Constraints:

- AGENTS.md is a governance doc: branch, PR, human review
- keeps the existing explicit-expectation rule for force pushes
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 AGENTS.md states the sha-bound push form and the one-approval-one-push rule
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
