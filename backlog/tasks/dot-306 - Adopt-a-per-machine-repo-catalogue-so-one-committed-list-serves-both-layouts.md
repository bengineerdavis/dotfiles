---
id: DOT-306
title: Adopt a per-machine repo catalogue so one committed list serves both layouts
status: To Do
created_date: 2026-11-08 16:54
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The committed catalogue hardcodes one machine's `~/code` layout, and the two machines are at different migration stages. Measured 2026-11-07: main's `config/repos.yaml` resolves **44/44** paths on the un-migrated Linux box; PR #92's re-pointed catalogue resolves **3/49** because it was authored on the migrated Mac. Neither version works on both machines, so the re-point is a machine-migration artifact, not a shared-config change.

**Correction to the first draft of this task.** It proposed moving membership into `machines.yml`, citing LAYOUT.md. That design was deliberately deleted on 2026-11-04 (commit 8c008d1, PR #129): the per-machine `repos:` block had no consumer and was keyed by a hardware serial, which fails spec.md § Data's string test. `tests/topics/test_machines_registry_data.py::test_the_registry_carries_no_repo_membership` now forbids the block returning, so restoring it is not an option and was the wrong reading.

That leaves the question genuinely open, and it is a design question, not a mechanical one:

- **(a) Migrate this machine first.** LAYOUT phase 4: move the `projects/<category>/…` tree into the type dirs (25 git repos under `projects/` on the Linux box today), gita re-registers each on move. Done when `~/code` matches the taxonomy and every repo still fetches. The catalogue then describes one layout again and needs no per-machine variant.
- **(b) Make path resolution per-machine without per-machine membership.** Keep one shared list of *repos*, but resolve *paths* through the overlay that already exists for work repos (`~/.local/state/layout/machines.local.yaml`), or by matching remotes rather than paths — DOT-172 already specifies "match existing clones by normalised host/owner/repo remote before cloning anything".
- **(c) Accept a transient gap.** Leave the catalogue correct for the migrated machine and accept "declared but not cloned" on the un-migrated one until phase 4 lands. This is what main does today, inverted.

The author asked on 2026-11-07 for "a default catalogue that can be customized per machine", which (a)+(b) together satisfy: one canonical taxonomy, per-machine resolution. (a) alone may be enough if this machine migrates soon.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Whichever option is chosen, both machines resolve the same set of repos on a clean run
- [ ] #2 A repo the machine does not have on disk is reported as missing, naming the path it looked for — never silently dropped
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
