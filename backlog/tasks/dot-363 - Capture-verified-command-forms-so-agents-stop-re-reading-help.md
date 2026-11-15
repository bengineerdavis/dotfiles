---
id: DOT-363
title: Capture verified command forms so agents stop re-reading help
status: To Do
created_date: 2026-11-15 20:21
priority: high
dependencies:
- DOT-362
updated_date: 2026-11-15 20:23
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
AGENTS.md § Working alongside other sessions already rules that a tool's
surface is probed before it is asserted, and the rule is unambiguous. It still
failed this session: `backlog-py task show DOT-233` was asserted from recall,
errored, and `task --help` then showed the documented form is `task <id>`.
Re-reading help on every call is the opposite failure — slow and wasteful when
the form is already known. The missing piece is memory of verified forms with
the cases they serve, and a fallback that re-reads help when a command stops
producing the expected result.

Ship:

- A capture of verified command forms, each recorded with the use case it
  serves and the probe that verified it
- A fallback rule: an unexpected result or a failing loop sends the agent back
  to `--help`, after analysing the cause rather than retrying blind
- The link to detection (DOT-362): a failing loop is one of the signals that
  work is going wrong

Constraints:

- This records what was verified; it never replaces verification for a new
  claim
- No contradictory instruction may result — the existing probe-before-assert
  rule stands, and this narrows when re-probing is needed
- A captured form that fails is removed or re-verified, never silently kept
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Verified command forms are captured with the use case each applies to
- [ ] #2 A failed or unexpected result falls back to reading --help, after analysing the cause
- [ ] #3 Successive failing loops on one command trigger re-verification rather than retry
- [ ] #4 The capture is readable by a session without a human present
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
