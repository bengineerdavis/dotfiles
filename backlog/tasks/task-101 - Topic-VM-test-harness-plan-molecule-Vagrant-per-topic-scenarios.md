---
id: TASK-101
title: Topic VM test harness — plan (molecule + Vagrant, per-topic scenarios)
status: To Do
created_date: 2026-10-27 02:56
labels:
- now
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Topic VM test harness — plan (molecule + Vagrant, per-topic
  scenarios).** [agent: orch_sub_vplan, worktree
  `.worktrees/orch_sub_vplan`] Builds on the molecule adoption already
  approved 2026-09-14 (§ Planned, "Adopt molecule for topic testing") —
  scenario co-location in `apps/<topic>/molecule/`, direct `molecule
  test` invocation, vagrant driver where containers cannot reach — read
  that item before writing anything. Author rulings 2026-10-10 for THIS
  work: durable capability, not a one-off; the agents-never-apply rule
  applies by reason — a Vagrant box is a separate machine with its own
  HOME and its own deployed tree, so agents may drive chezmoi and
  ansible there; and the first scenario is the apps/opencode v2
  migration — the run that confirms we are good to deploy (the author's
  ask: "enough virtualization with vagrant that we can inject ansible
  into a test box"). Design input for the plan, not a ruling: shape the
  wrapper interface so humans can explore stepwise
  (create/login/verify/destroy, linger in the box) while agents run
  `molecule test` non-interactively. Verified 2026-10-06 on this box:
  vagrant 2.4.9, VirtualBox present, /dev/kvm available. macOS is out
  of scope for VM testing (no macOS boxes exist); this confirms the
  Debian leg, and the plan says so plainly. Branches off main (post
  #46, including the apt hook-standards commit); PR to main from there.
  Plan lands at
  `dotfiles/docs/research/topic-vm-tests/PLAN.md`. Done when it names:
  the scenario layout and where it lives per TOPICS.md conventions, the
  wrapper interface (and the wrapper's own build-ladder justification),
  the molecule dependency install path per docs/PYTHON.md, exactly what
  the opencode scenario asserts (v2 formula present, v1 gone, config
  loads, skills synced), box-image and provider choices, destroy
  safety, the author-run vs agent-run split, and any open author
  decisions.
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
