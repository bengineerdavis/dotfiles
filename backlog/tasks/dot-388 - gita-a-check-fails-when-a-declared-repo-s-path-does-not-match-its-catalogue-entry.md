---
id: DOT-388
title: 'gita: a check fails when a declared repo''s path does not match its catalogue entry'
status: To Do
created_date: 2026-11-19 21:00
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->

Handed off from DOT-366 (AC #4, the one AC its 2026-11-19 close-out did not
land): a check that FAILS when a declared repo's path does not match its
catalogue entry, so the next layout migration cannot silently flatten the
tree (the DOT-366 incident: 43 of 49 catalogue entries carried a stale
`projects/` prefix and gita re-registered repos wherever they happened to
land, nobody was told).

Shape: extend the gita topic's install (or its test suite) so that a
catalogue entry whose path does not resolve on disk — while the repo's
basename DOES exist somewhere under ~/code — is a loud mismatch report, not
a silent declared-but-not-cloned line. The declared-but-not-cloned report
itself stays (it is correct for genuinely not-cloned repos); the new signal
is "declared at X, found at Y" drift.

Constraints:

- Never relocate a repo to match the catalogue (DOT-366's own constraint:
  moves happen first, registration follows)
- Machine-agnostic: paths in the catalogue are relative to ~/code; the check
  must work on both machines
- tests/gita covers: catalogue path X + repo at Y under ~/code → failure or
  loud report; catalogue path X + repo nowhere → declared-but-not-cloned
  (unchanged)

<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria

<!-- AC:BEGIN -->

- [ ] #1 A catalogue entry whose basename exists on disk at a DIFFERENT path than declared produces a loud (exit-nonzero or FAIL-class) report naming both paths
- [ ] #2 A catalogue entry whose repo is genuinely absent stays a declared-but-not-cloned report (no false alarm)
- [ ] #3 tests/gita covers both cases with a fixture tree

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
