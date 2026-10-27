---
id: TASK-123
title: Stop repo tooling leaking into `$HOME`
status: To Do
created_date: 2026-10-27 02:56
labels:
- planned
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Stop repo tooling leaking into `$HOME`.** `chezmoi managed
  --include=files` on 2026-09-23 (700 paths) lists `docs/LANGUAGES.md`,
  `docs/GLOSSARY.md` and `docs/WORKTREES.md` (→ `~/docs/`); `scripts/`, 3
  hook scripts (→ `~/scripts/`); and two `bin/` strays,
  `executable_archive.bk` and `executable_READMD.archive.md`. `tools/` (9
  files → `~/tools/`) belongs to the skill-trust install task. The guard's
  `GOVERNANCE_FILES_IN_DOCS` also omits `docs/LAYOUT.md`, ignored in
  `851a419` but unguarded. `docs/ARCHITECTURE.md` and `docs/USAGE.md`
  deploy on purpose. Until the guard sees worktrees (§ Now #1 (p) P2a),
  check fixes from the main checkout. Done when each leak is ignored,
  deleted or recorded as deliberate, and the guard lists every ignored
  convention doc. The `.chezmoiroot` item in `ROADMAP.md` would end this
  class of leak.
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
