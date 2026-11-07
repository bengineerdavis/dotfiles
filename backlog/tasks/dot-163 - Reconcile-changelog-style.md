---
id: DOT-163
title: Reconcile changelog style
status: To Do
created_date: 2026-10-27 02:58
labels:
- planned
updated_date: 2026-10-27 22:22
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Reconcile changelog style: plain language, the house commit style in
  `docs/TOPICS.md` § Commit granularity, and the changelog standard have to
  intersect without contradicting.
  **[corrected 2026-09-16: the "no CHANGELOG.md — git log is the changelog"
  premise is stale. The repo adopted scriv (00e278e): fragments live in
  `changelog.d/` and collect into `CHANGELOG.md` on release, per
  `CONTRIBUTING.md` § Writing a changelog entry. Same session observed a
  second gap: sessions intermittently skip fragments — the 2026-09-16 opencode
  permission rework landed 14 commits with none, later backfilled — and nothing
  enforces one. The reconciliation should cover fragment *reliability*, not
  style alone.]**
  **[open question: which changelog standard to cite. `CHANGELOG.md` already
  names Keep a Changelog 1.1.0; `ai-prompt-library/CHANGELOG.md` cites 1.0.0.
  Common Changelog is the other candidate. Confirm which before writing the
  rule.]**
  **[added 2026-11-07, from PR #136's "deliberately left out" list: two
  concrete defects this task should fix, both measured on `main`.

  (1) A bare category word leaks through instead of becoming a heading. PR
  #103's collected entry reads `## PR #103 — 2026-10-29` followed by a plain
  line `changed`, then the bullets — the fragment's category word was never
  turned into `### Changed`. It is still there on `main` at `CHANGELOG.md`
  line 207, the only one of 21 category markers that is not a heading.

  (2) The bold-versus-heading split. Collected entries use `### Added`,
  `### Changed`, `### Fixed` (21 headings), while hand-written fragments in
  `changelog.d/` used `**Added**`. scriv normalises what it understands, so the
  mismatch shows up as entries that read differently depending on whether a
  human or the collector wrote them. Settle on one form — the headings, since
  that is what 21 of 21 collected entries already use — and state it in
  `CONTRIBUTING.md` § Writing a changelog entry so a fragment author gets it
  right without reading the collector.]**
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
