---
id: DOT-200
title: Build a CLI that manages provisioning config and state, including
status: To Do
created_date: 2026-10-27 02:58
labels:
- planned
- group:refactor-b-factor-the-ai-llm-tooling-out-of-this-repo
updated_date: 2026-10-27 22:22
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Build a CLI that manages provisioning config and state, including
  bootstrapping. Think mise or apt, but for topics and their files: scaffold a
  new topic from a template, add or remove a dependency, run the bootstrap, and
  report state. One of the refactors named in `PRD.md`.
  Why it is worth building rather than tolerating:
  - It is what makes the PRD's complexity governor true instead of aspirational.
    The governor says a routine change must never require touching `spec.md` or
    writing a test — that only holds if a tool does the routine change correctly
    by construction.
  - It makes `spec.md` § Layering — teardown changes with the thing it creates
    structural rather than a discipline. A template that scaffolds install and
    removal together cannot forget the removal, which is the exact failure that
    rule was bought by: a hand-copied `launchctl unsetenv` list silently stopped
    covering a newly added variable.
  - Adding a topic by hand is the current cost, and it is being paid right now
    for the chrome topic. That is the motivating case, not a hypothetical.
  Target shape: the CLI is the trusted process, and an agent drives it rather
  than editing topic files directly. The CLI stays as the fallback for when the
  agent is not trusted or not present, so machine configuration can be updated
  as-you-go by either. Both paths go through one implementation, because two
  paths means two behaviours.
  Constraints it inherits: it belongs to the provision layer, so it may install
  and trigger but must never hold a tool's logic or state (`PRD.md`
  § Architecture). It must be topic-neutral — no topic gets special handling —
  and it consumes policy generally rather than embedding rules, per the policy
  generalisation item above.
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
