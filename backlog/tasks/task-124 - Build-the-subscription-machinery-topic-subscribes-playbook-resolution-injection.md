---
id: TASK-124
title: 'Build the subscription machinery: `topic_subscribes` + playbook resolution
  + injection'
status: To Do
created_date: 2026-10-27 02:57
labels:
- planned
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Build the subscription machinery: `topic_subscribes` + playbook
  resolution + injection.** The mechanism half of the adopted system-config
  model (resolved council entry, `TASKS-RESOLVED.md` 2026-09-17): a topic
  declares `topic_subscribes: [<catalogue>]` in `topic.yml`; the parent
  playbook validates each subscribed catalogue exists as
  `dotfiles/config/<catalogue>.yaml` (unknown catalogue fails loudly naming
  both sides), resolves each subscriber's slice — entries matching that
  consumer, availability verdicts applied — and injects it as a var;
  topics carry only a thin install-and-report loop over the list they were
  handed, so unresolvable verdicts fail at the playbook layer before
  anything installs. Resolution lives in `roles/`, per the
  `roles/topic-resolution` precedent (playbook pre_task logic extracted
  2026-09-15 so the playbook stays readable and the logic is testable —
  `tests/topic_resolution/` is the shape to follow). **Gated on the
  normative topic spec landing first** — the subscribes key is `topic.yml`
  schema the spec governs — and on the catalogue seed in § Now. Tests
  first and mutation-proven per `spec.md` § Verification; the resolution
  filter is pure set/merge logic, so it takes a property test. Done when
  resolution is tested, the playbook fails loudly on an unknown catalogue
  or an unresolvable verdict, and the injected-var contract is documented
  in `dotfiles/docs/TOPICS.md`. [me]
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
