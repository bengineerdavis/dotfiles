---
id: DOT-347
title: Research routing work across models by cost-performance frontier
status: To Do
created_date: 2026-11-10 17:37
labels:
- research
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Every session runs on the top-tier model, including mechanical work a cheaper model could do. The author wants the best models for decisions, instruction writing and code review, and price-efficient (pareto-frontier) models for the rest.

Ship:

- a cited research note on which OpenRouter models sit near the price/quality pareto frontier for planning, review, and implementation roles
- a routing proposal: which role and session kind uses which model, and how opencode selects it (agents, subagent model config)
- a plan to measure each candidate on this machine with model-fitness before adoption

Constraints:

- published benchmarks are leads, not evidence; adoption needs measured runs (model-fitness, AGENTS.md § Models)
- no hosted GPT or Grok as defaults; model calls go through the lore gateway
- planning sessions such as this one are the first consumer: split planning from execution so execution runs cheaper
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The research note exists with primary-source citations per candidate
- [ ] #2 The routing proposal maps each role to a model and an opencode config mechanism
- [ ] #3 Each proposed model has a model-fitness measurement plan, or a measured result
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
