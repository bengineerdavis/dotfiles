---
id: draft-8
title: Design bounded Molecule test lifetimes and dormancy teardown
status: Draft
created_date: 2026-10-29 19:00
labels:
- design
- testing
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Design draft only. Explore whether Molecule or its wrapper can impose bounded runtimes and clean up dormant test VMs, analogous to a watchdog for a cron-scheduled service. Distinguish a VM making no progress from a legitimately slow active test and from a hung host process. Check Molecule, Ansible, and wrapper timeout capabilities before proposing new machinery. Define timeout budgets, progress signals, ownership of process groups, and guaranteed scenario-scoped teardown. Ask the author which dormancy signal and default budget are acceptable; do not implement a timeout policy from this draft alone.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Document native timeout options, dormancy versus slowness semantics, and safe cleanup for each timeout layer.
- [ ] #2 Include failure and recovery cases that cannot kill another session or delete a live VM.
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
