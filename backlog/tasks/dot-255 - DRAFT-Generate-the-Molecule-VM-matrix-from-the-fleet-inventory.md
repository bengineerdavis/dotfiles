---
id: DOT-255
title: 'DRAFT: Generate the Molecule VM matrix from the fleet inventory'
status: To Do
created_date: 2026-10-28 16:05
labels:
- testing
- molecule
- design
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Extend the Molecule harness so its VM selection follows the machines this dotfiles repo supports, rather than requiring a hand-added scenario for every new host or OS upgrade.

The approved harness keeps topic scenarios under apps/<topic>/molecule/ and uses Molecule's native scenario orchestration (DOT-76, DOT-101). This task should build on that design and DOT-254's declared Vagrant/provider prerequisites, not invent a second harness.

Design the inventory-to-matrix path:

- Identify the authoritative machine/OS inventory and how each entry maps to a VM image, architecture, provider, and supported topics.
- Generate or select Molecule scenarios from that inventory for the requested topics, without changing the topic lifecycle or duplicating scenario logic per VM.
- Add newly supported machines and OS upgrades as inventory changes, with explicit overrides for exceptions and unsupported VM/provider combinations.
- Keep local developer runs bounded: default to a documented useful subset, with an explicit all-fleet mode for CI or maintainer runs.
- Keep macOS coverage distinct from Linux Vagrant/libvirt coverage; a machine inventory entry must not silently imply a working macOS VM provider.
- Make destroy/prune behavior and VM resource budgets explicit for a matrix that can grow.

This is a draft for design review, not authorization to implement. The PRD/roadmap and the existing harness decisions should be revisited before claiming it for execution.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The design names the authoritative machine inventory and defines deterministic inventory-to-VM/topic matrix selection.
- [ ] #2 Adding a machine or changing an OS release changes the selected VM coverage through inventory data, with tests for both cases.
- [ ] #3 Unsupported provider/OS combinations fail visibly or are explicitly excluded; no green run is reported for skipped platform coverage.
- [ ] #4 The design preserves per-topic Molecule scenarios and supports bounded local runs plus an explicit full-fleet run.
- [ ] #5 Resource, teardown, and CI behavior are specified before implementation tasks are created.
- [ ] #6 DOT-254 and the existing molecule harness decisions are reconciled rather than duplicated.
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
