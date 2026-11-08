---
id: DOT-306
title: Adopt a per-machine repo catalogue so one committed list serves both layouts
status: To Do
created_date: 2026-11-08 16:54
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The committed catalogue hardcodes one machine's `~/code` layout. Measured 2026-11-07: main's `config/repos.yaml` resolves 44/44 paths on the un-migrated Linux box; PR #92's re-pointed catalogue resolves 3/49 because it was authored on the migrated Mac. Neither version works on both machines, so a re-point is a machine-migration artifact, not a shared-config change.

Per docs/LAYOUT.md the design already exists: `machines.yml` is the committed per-machine map and `~/.local/state/layout/machines.local.yaml` is the machine-local overlay for work names. What is missing is the catalogue reading it — today repos.yaml is a flat list of type-dir paths.

Decide between: (a) migrate this Linux box to the type dirs first (LAYOUT phase 4, 25 git repos under projects/), keeping one catalogue; or (b) make the catalogue per-machine — machines.yml carries each machine's repo membership and the topic resolves paths per host, so a migrated and an un-migrated machine both work. Option (b) is what LAYOUT.md already prescribes and what the author asked for on 2026-11-07 ('a default catalogue that can be customized per machine'); it is also more work and touches shared config.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Whichever option is chosen, both machines resolve the same set of repos on a clean run
- [ ] #2 A machine with no entry does not silently register zero repos — it reports the gap and names the fix
- [ ] #3 The choice and its rejected alternative are recorded as a decision record
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
