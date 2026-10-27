---
id: TASK-63
title: Spec the zsh tooling standard — author interview first, then a review-best-practices
  pass, then coun
status: To Do
created_date: 2026-10-27 02:55
labels:
- now
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Spec the zsh tooling standard — author interview first, then a
  review-best-practices pass, then council critique.** Queued by the author
  2026-09-16, from the LANGUAGES.md zsh row: ~90 `.zsh` files are zsh
  lifecycle fragments, the extension marks how a file is used rather than a
  distinct language, and the bash standard already applies de facto — the
  pre-commit shellcheck hook matches `types: [shell]` and identify tags
  `.zsh` as `shell`. Interview first: fragment-vs-script semantics, which
  bash tools are trusted on zsh, tolerance for zsh-specific false positives
  (shellcheck does not support zsh — `typeset`, `${~spec}`, `=cmd` are known
  mismatch classes), whether `zsh -n` should gate commits, and where the spec
  lives (a `docs/LANGUAGES.md` row vs a new `docs/ZSH.md`). Then a research
  pass verifies the "zsh can use bash tools" claim rather than assumes it,
  with ranked options and rejections recorded. Then fresh-context subagents
  red-team the draft (the panel-of-judges question is itself unsettled; using
  the pattern here is the author's call). Done when a written recommendation
  exists with rejections recorded, the author's adopt/adapt/reject decision
  is recorded, and any wiring lands as queued tasks. [me]
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
