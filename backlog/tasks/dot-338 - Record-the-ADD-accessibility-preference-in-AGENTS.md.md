---
id: DOT-338
title: Record the ADD accessibility preference in AGENTS.md
status: To Do
created_date: 2026-11-10 04:48
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The user has ADD (noted in map.md 2026-11-09, currently only in agent memory —
invisible to other sessions and agents). Sessions should keep output scannable
and present decision points as labeled options, because the reader gives terse
approvals that accept the suggested path, so any recommendation must be honest.

Ship:

- A § Communication or equivalent subsection in AGENTS.md recording the
  accessibility preference: scannable output, decision points as labeled
  options, honest recommendations the reader may accept with a one-word reply.

Constraints:

- Write the rule in plain language per the repo's Writing section; state the
  reason (terse approvals follow the recommendation) so the honesty requirement
  is checkable, not vibes.
- Map.md is agent-session state, not the durable home for a standing
  preference; AGENTS.md is.

Decision record: Agreed with the author 2026-11-09: record the preference as a
tracked task rather than leaving it only in memory.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 AGENTS.md contains the accessibility rule (scannable output, labeled decision options with recommendations) in its own subsection
- [ ] #2 The rule text states the reason — the reader's terse approvals follow the recommendation — so the honesty requirement is verifiable
- [ ] #3 `grep -i "ADD\|accessib" AGENTS.md` finds the section, and `backlog-py board` shows DOT-338 with the full description intact
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
