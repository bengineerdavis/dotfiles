---
id: draft-9
title: Design tiered fast feedback tests for agents and humans
status: Draft
created_date: 2026-10-29 19:00
labels:
- design
- testing
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Design draft only. Define tiers for file-save/LSP feedback, git-add or pre-commit checks, pre-push verification, and merge gates. Mix deterministic checks with appropriate LLM tests so agents and humans get fast, useful failures without hiding important coverage. The author accepts some speed cost for better quality, but quality itself needs an architecture decision: detection value, false positives, actionability, determinism, security, and resource cost. Record what runs at each tier and why. Do not put unreviewed network egress into save-time hooks or equate more LLM judging with better quality.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Propose test tiers with target budgets, ownership, and promotion rules between fast and slow suites.
- [ ] #2 Define quality with the author and show how each proposed check earns its cost.
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
