---
id: DOT-362
title: Detect ineffective session processes and surface them for a decision
status: To Do
created_date: 2026-11-15 20:21
priority: high
labels:
- research
updated_date: 2026-11-15 20:23
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Sessions do not notice their own ineffective processes. `/retro` performs this
analysis, but only after the fact, only when the author invokes it, and only
over one session — so a failure can recur for months before anyone looks. The
`git commit -o` violation ran three times across three months and two prior
incidents before a retro caught it; this session also asserted a CLI verb from
recall and corrected it a turn later, a loop nothing recorded. The hard part is
not capture but the trigger: three corrections in a row may be productive
debugging or a broken approach, and the signal that separates them is unknown.

Ship:

- Research into what signals distinguish productive iteration from an
  ineffective process: error-and-correct loops, repeated identical probes,
  expensive paths, rework after a correction
- A judgement on whether detection runs in-session or over session logs after
  the fact, with the cost of each
- A capture format a session can write without a human present, and a
  surfacing point where the author schedules or makes the decision
- A recommendation naming what was rejected and why

Constraints:

- Research first: this is a question before it is a build, and the deliverable
  is a decision with reasoning rather than a survey
- Search established practice as well as tools; what practitioners do is
  evidence about options, never evidence of fit
- Verify any capability claim against the artifact before a design leans on it
- Time-boxed: a search that finds nothing is finished — say so and propose
  building
- Detection reports; it never silently changes session behaviour
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Signals distinguishing productive iteration from ineffective process are named, with the evidence for each
- [ ] #2 A judgement is recorded on in-session versus post-hoc log detection, with costs
- [ ] #3 A capture format exists that a session can write unattended
- [ ] #4 A surfacing point is defined where the author schedules or makes the decision
- [ ] #5 Rejected approaches are recorded with their disqualifying reason
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
