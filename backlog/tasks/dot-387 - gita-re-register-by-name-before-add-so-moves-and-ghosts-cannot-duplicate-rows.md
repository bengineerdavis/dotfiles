---
id: DOT-387
title: 'gita: re-register by name before add so moves and ghosts cannot duplicate rows'
status: To Do
created_date: 2026-11-19 21:00
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->

The gita topic's registration step runs `gita add <path> -g <group>` for every
catalogue repo that exists on disk. `gita add` keys by repo NAME and appends a
row when the path differs from what the CSV already holds — it does not update
in place. Measured 2026-11-19 (L37V3P6GQ3): after the layout migration moved 7
repos from top-level `templates/`/`try/` into `personal/templates/`/`personal/try/`,
one topic install left repos.csv with BOTH paths per name — 87 rows for 78 repos,
7 duplicate names (`agentic-project-template`, `copier-cat`, `copier-mise-sandbox`,
`copier-template-copier-template`, `dotfile-topic-copier`, `Best-README-Template`,
`xerror`). Gita's own reads then served the stale path. Repaired by hand
(`gita rm <name>` + `gita add <new-path>` per repo, verified 0 dupes after) —
but the topic must not recreate the state on the next run or on the Linux box's
phase-5 migration.

Ship: the registration step re-registers by name — for each catalogue repo,
a `gita rm <name>` (tolerating absence) before the `gita add`, so a moved repo
has exactly one row at its current path and a ghost row for a deleted repo is
swept rather than accumulated. Alternatively verify a newer gita version
updates paths on re-add and pin/document that instead.

Constraints:

- `gita rm` of an absent name must not fail the run (tolerate, then add)
- The reconcile sweep and the work-root walk keep their current semantics
- Tests: tests/gita covers the duplicate case — a fixture CSV with a stale
  path plus a live repo at a new path must converge to one row at the new path

<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria

<!-- AC:BEGIN -->

- [ ] #1 An install run over a repos.csv that already holds a repo at a stale path (repo since moved) converges the CSV to exactly one row for that name, at the current path
- [ ] #2 A ghost registration (name in CSV, repo deleted from disk) is swept by the registration step, not silently retained
- [ ] #3 tests/gita covers both: a fixture CSV with stale path + live repo at new path, and a ghost row

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
