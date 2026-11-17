---
id: DOT-356
title: Research macOS guest VMs for topic testing on Apple silicon
status: To Do
created_date: 2026-11-12 22:55
dependencies:
- DOT-323
labels:
- research
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
DOT-346's macOS paths cannot be proven in Lima's Linux guests, and earlier decisions set macOS VMs aside. The author wants the options re-examined before settling for mocked probes.

Ship:

- a cited comparison of macOS-guest options on Apple silicon (Lima vz macOS guests, tart, UTM, Vagrant providers, anything else found): license limits, rootless use, disk and boot cost, whether molecule can drive it
- one option measured on this machine: boot a guest and run one trivial topic, or record why it failed
- a recommendation for DOT-346's test strategy

Constraints:

- the Apple EULA allows at most two macOS guests per Mac host; record this per option
- probe each tool's installed --help before claiming a capability
- research only: any install goes through a topic task
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The comparison note cites primary sources per option
- [ ] #2 One option is measured on this machine, with the result recorded
- [ ] #3 DOT-346 notes carry the recommended test strategy
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
