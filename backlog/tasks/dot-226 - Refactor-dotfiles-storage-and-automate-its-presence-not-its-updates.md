---
id: DOT-226
title: Refactor dotfiles storage and automate its presence, not its updates
status: To Do
created_date: 2026-10-27 02:59
labels:
- planned
- group:refactor-b-factor-the-ai-llm-tooling-out-of-this-repo
updated_date: 2026-10-27 22:22
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Refactor dotfiles storage and automate its presence, not its updates.**
  Dotfiles stays a top-level repo (`~/.local/share/chezmoi`, deployed to
  `~/dotfiles`), outside the `~/code` taxonomy. Requirement (author
  2026-10-18): a target machine must GET dotfiles automatically, but dotfiles
  is never auto-updated — pulling is deliberate. Two parts: (a) automate the
  add — a fresh box gets the checkout from one step, no scheduled pass pulls
  it; (b) refactor how it is stored and how changes are made to it to be
  more seamless — this design is open. Interview the author before cutting
  tasks; record the storage shape in `PRD.md`/`docs/LAYOUT.md` and the work
  items here. Done when a fresh machine clones dotfiles automatically and no
  update path pulls it.
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
