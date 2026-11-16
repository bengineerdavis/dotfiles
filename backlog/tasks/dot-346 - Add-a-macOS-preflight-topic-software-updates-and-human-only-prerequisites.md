---
id: DOT-346
title: 'Add a macOS preflight topic: software updates and human-only prerequisites'
status: To Do
created_date: 2026-11-10 17:37
dependencies:
- DOT-345
- DOT-296
- DOT-356
labels:
- feature
priority: high
updated_date: 2026-11-12 22:55
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
macOS machines have steps Ansible cannot finish alone: Xcode Command Line Tools (DOT-296), Rosetta 2 on Apple silicon, and pending OS updates. Today these fail mid-run, and the error names the consumer instead of the cause.

Ship:

- a preflight topic that runs first, both on a managed machine and in bootstrap on a new machine
- a check for pending updates with `softwareupdate -l`, and an install with `softwareupdate -ia` when the operator opts in
- checks for Xcode CLT and Rosetta 2 (only where the CPU needs it) that print the exact command for a human to run, then stop the run so the next one is uninterrupted
- molecule scenarios for the logic

Constraints:

- the install needs become, so this depends on DOT-345
- never trigger a restart without an explicit opt-in
- Lima/molecule cannot easily boot macOS guests: probe whether a macOS guest works before writing the scenarios; otherwise test the decision logic with mocked probes and record the gap (see DOT-323)
- deployed-tree change: PR
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The preflight topic runs before every other topic, in both update and bootstrap
- [ ] #2 Pending updates are reported, and installed only with the opt-in
- [ ] #3 A missing CLT or Rosetta prints the exact human command and stops before any other topic runs
- [ ] #4 The molecule scenarios cover the present, missing, and opt-in cases, and each was seen to fail against a broken copy
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
Author feedback 2026-11-10:
- Agreed: softwareupdate reports by default and installs only on opt-in. Build requirement: as many early checks as needed, so that every human-only step or blocker is raised at the start of the run, clearly, before any topic runs.
- macOS VM testing is still open. The author has not given up on it: explore the options (Lima macOS guests via Virtualization.framework, tart, UTM, Vagrant) before writing the scenario ACs. Earlier "no macOS VMs" decisions are inputs, not a ruling.
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->
