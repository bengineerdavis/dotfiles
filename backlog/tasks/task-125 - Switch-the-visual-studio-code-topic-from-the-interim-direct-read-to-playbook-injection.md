---
id: TASK-125
title: Switch the visual-studio-code topic from the interim direct read to playbook
  injection
status: To Do
created_date: 2026-10-27 02:57
labels:
- planned
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Switch the visual-studio-code topic from the interim direct read to
  playbook injection.** The topic is already wired (2026-09-17, § Now):
  install/remove/upgrade consume `config/editors.yaml` through a
  role-relative direct read with the thin loop and gated teardown. When
  the subscription machinery above lands, replace the direct read with
  `topic_subscribes` + the injected slice — behavior must not change, and
  the switch is proven by being a no-op on the converged machine. Done
  when the direct read is gone, `--check --tags provision` still converges
  (changed=0), and the topic's CHANGELOG records the switch. [me]
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
