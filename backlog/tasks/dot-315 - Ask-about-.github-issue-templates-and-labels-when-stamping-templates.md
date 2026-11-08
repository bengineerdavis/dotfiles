---
id: DOT-315
title: Ask about .github issue templates and labels when stamping templates
status: To Do
created_date: 2026-11-08 21:30
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
When stamping down a new or updated template from
`~/code/projects/personal/templates/copier-template-copier-template`, ask
about `.github` issue templates and labels. The gap surfaced 2026-11-08 while
filing the DOT-59 feature request against `python-project-template`: that repo
has no issue templates or labels (`.github/` holds only three workflows), so a
separate session absorbing the feature request via `@askmatt` has no convention
to follow. The follow-up belongs to the copier-template-copier-template repo
(CTCT-N there) — this DOT task is the dotfiles-side pointer, and the source of
truth is that repo's queue. Do not commit to the foreign repo without the
maintainer's acknowledgment (AGENTS.md § Cross-repo changes).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
1. The question — "do you ship `.github/ISSUE_TEMPLATE` and `labels.yml`, or
   should the stamper ask?" — is recorded as a task in
   `copier-template-copier-template` (CTCT-N), filed on that repo's main via
   the author.
2. This DOT task points at that CTCT task so the two do not drift.
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