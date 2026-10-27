---
id: TASK-220
title: Make docs repo-only by relocating them out of the payload
status: To Do
created_date: 2026-10-27 02:59
labels:
- planned
- group:refactor-b-factor-the-ai-llm-tooling-out-of-this-repo
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Make docs repo-only by relocating them out of the payload.** [decision
  2026-10-03: docs are excluded from provisioned files; ROADMAP "Docs
  excluded from provisioned files"] `git mv dotfiles/docs/*` into root
  `docs/`, reconciling the two ARCHITECTURE.md and two USAGE.md copies —
  the maintained `dotfiles/docs/` content wins where the copies differ,
  root `docs/` becomes the one docs tree — and update every citation
  (~39 topic files cite `dotfiles/docs/TOPICS.md`; AGENTS.md, spec.md,
  CONTRIBUTING.md, ROADMAP-topic-cli). Root `docs/ARCHITECTURE.md`,
  `docs/USAGE.md` and `RESOURCES.md` drop out of `chezmoi managed` here or
  at the payload move, whichever lands first. Done when: nothing remains
  under `dotfiles/docs/`; `chezmoi managed` lists no docs path; doc-link/
  doc-integrity tests and skillet green; AGENTS.md § What this repo is
  points at root `docs/`. Lands before the payload move so that move
  carries no docs; the move item inherits a smaller tree. [unclaimed]
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
