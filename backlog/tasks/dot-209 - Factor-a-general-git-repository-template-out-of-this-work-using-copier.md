---
id: DOT-209
title: Factor a general git repository template out of this work, using copier
status: To Do
created_date: 2026-10-27 02:59
labels:
- planned
- group:refactor-b-factor-the-ai-llm-tooling-out-of-this-repo
updated_date: 2026-10-27 22:22
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Factor a general git repository template out of this work, using copier
  (9.17.2, installed). **Its own repository at `~/code/personal/`**, alongside
  ai-prompt-library and impromptu — not a directory here, and not under
  `~/code/work/`. Name is not settled; it is the reusable half of this repo's
  practice, so something like `spec-driven-repo-template` describes it. What has
  earned its place and is not dotfiles-specific: the document set and its
  separation of concerns (PRD what-for, spec what-must-stay-true, ROADMAP
  what-is-next, TASKS what-is-now, AGENTS how), the RECL loop, the verification
  practices (both-directions, prove-the-test-fails, property and fuzz guidance),
  the branching and merge-gate conventions, and the Python toolchain section.
  Excluded: anything chezmoi, Ansible or model-specific, and anything
  language-specific — language conventions are a pluggable `<LANGUAGE>.md`
  chosen by copier prompt, so the template ships `docs/PYTHON.md` as one
  option rather than baking Python into AGENTS.md. `docs/` is the unit
  the template plugs into — adding a language means dropping one file there. That is what lets the template grow to
  cover other languages without a rewrite. This template IS the
  reusable AGENTS.md baseline, so the baseline-versus-overlay split happens here
  rather than separately. Done when a fresh repo scaffolded from it has the full
  document set, passes `skillet validate`, and asks its project-specific parts as
  copier prompts rather than leaving placeholders to hand-edit.
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
