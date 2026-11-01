---
id: draft-15
title: Assign model cost and latency budgets by service role
status: Draft
created_date: 2026-10-29 19:02
labels:
- design
- models
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Design draft only. Review which models are used for each role across roborev, LoreAI, local evals, and other agent services. Current choices may be too expensive or slow. Compare candidate models on this hardware for the actual tasks, with measured quality, latency, context, memory, and dollar cost. Define where smaller local models suffice, where stronger hosted models earn their cost, and how provider and egress policy constrain each choice. Do not switch defaults on published benchmarks or assume one model is best across services. Coordinate with the model-fitness and domain-backlog work before changing role assignments.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Inventory model roles and current cost/latency constraints across roborev, LoreAI, and other services.
- [ ] #2 Define a measured evaluation matrix and role-specific selection criteria, with quality floors and fallback behavior.
- [ ] #3 Record candidate assignments, their measured tradeoffs, and the human approval needed before adoption.
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
