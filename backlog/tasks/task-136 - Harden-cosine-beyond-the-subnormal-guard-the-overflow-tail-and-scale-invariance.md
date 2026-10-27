---
id: TASK-136
title: 'Harden cosine beyond the subnormal guard: the overflow tail and scale invariance'
status: To Do
created_date: 2026-10-27 02:57
labels:
- planned
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Harden cosine beyond the subnormal guard: the overflow tail and scale
  invariance.** The advisor pass found what 6c3079b's guard missed. Two
  tails: an overflow tail where sums overflow to inf and the quotient
  becomes NaN — and the coverage classifier counts NaN as classified
  (`nan < args.min_margin` is False), the exact "unknown becomes a claim"
  shape; and the guard breaks scale invariance (parallel tiny vectors score
  0.0), which no property test pins and which the centroid classifier hits
  for near-centroid prompts by construction. Candidate fix: max-abs
  pre-scaling (preserves invariance, fixes both tails), plus a
  scale-invariance property, a NaN-cannot-classify assertion, and an eval
  case pinning near-centroid behavior. Done when the properties exist, the
  counterexamples are pinned, and the mutation check shows the old guard
  failing them. [me]
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
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
