---
id: TASK-190
title: Add bundle-aware limiting to the parent playbook
status: To Do
created_date: 2026-10-27 02:58
labels:
- planned
- group:topic-bundles-data-first-grouping
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add bundle-aware limiting to the parent playbook: `-e bundle=<name>` with
  `--tags install|upgrade|remove` runs only that bundle's members for this
  machine (os-filtered). Done when a limited install touches exactly the
  bundle's members here, and a limited remove still consults `requires_map`
  before tearing any shared dep.
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
