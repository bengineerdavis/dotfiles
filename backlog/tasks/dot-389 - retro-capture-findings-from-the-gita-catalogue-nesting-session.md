---
id: DOT-389
title: 'retro: capture findings from the gita catalogue-nesting session'
status: Done
created_date: 2026-11-19 21:00
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->

Session retro (2026-11-19, gita-catalog-repoint worktree): the catalogue
re-point, layout migration, capture/skeleton topic work, and close-out.
Corrections and negative results recorded, not just successes.

**What landed**

- PR #177 merged (`f95af948`): catalogue re-point to type dirs; layout
  capture (`~/.local/state/layout/tree.yaml`) + type-directory skeleton in
  the gita topic, both flip-tested with Mutation/Failing-test trailers.
- PR #183 merged (`583de54b`): final nesting re-point after the disk moves.
- Disk migration completed: `~/code` = `AGENTS.md, forks, personal, work`;
  7 template + 3 try repos verified under `personal/`; nested worktrees
  inside a moved repo survived (relative gitdir pointers).
- Live gita state reconciled; duplicate rows repaired; DOT-366 closed at 5/6
  ACs; DOT-387/388 filed as the follow-ups.

**What went wrong (corrections)**

1. **The topic's blind `gita add` duplicated rows on move.** The install
   re-adds catalogue repos; gita keys by name and appends when the path
   differs, so one run after the migration left 7 duplicate-name rows (87
   rows / 78 repos) serving stale paths. Repaired by hand; the topic defect
   is DOT-387. Lesson: a first-party tool's re-add semantics are not
   idempotence — verify what a re-run does to state it does not own.
1. **The capture path first resolved via `ansible_user_dir`, which ignores
   `$HOME`** — the pytest sandbox wrote its tmp shape over the LIVE capture
   file (pytest-94's tree.yaml at ~/.local/state/layout/). Caught because
   the capture content named its own code_root; fixed to resolve from
   `$HOME` (commit c67a86f8 trailer). Lesson: any absolute write path in a
   topic must resolve through the same env the tests sandbox.
1. **The skeleton's `work` entry manufactured the tree the work-probe was
   meant to discover** — probe moved before the skeleton (commit c67a86f8
   trailer). Lesson: provisioning a directory changes the answer of any
   probe that runs after it; order probes before provisioning.
1. **The `.pr-body.md` residue in the moved repo's nested worktree** — my
   own leftover from PR authoring, found during close-out. Untracked, left
   in place (not my repo to clean in this session).
1. **A re-point matched the disk instead of the standard** (PR #177 shipped
   `templates/` top-level; LAYOUT.md wants it inside `personal/`). Caught by
   the author asking "are templates also under personal/?". Lesson: when a
   catalogue encodes a shape, diff it against the named standard, not the
   disk it observed — the disk is often the drift being repaired.

**Negative results**

- The Nov 12 `--check`'s 10 declared-but-not-cloned were each accounted for;
  the Nov 19 re-run's 11th was an honest new report (a worktree deleted from
  disk since), not a regression. Kept declared per author decision.
- pipx:ansible 14.6.0 (installed by a background upgrade 2026-11-16) is
  broken on python 3.15 (`dataclasses._is_type` AttributeError); the `14/`
  older install works. Worked around locally; DOT-371 already queued the
  python pin by another session.

**Follow-ups filed**: DOT-387 (re-register by name before add), DOT-388
(the AC-#4 drift check). DOT-172 (G3 clone-all) remains the next G-series
task, ready to scope.

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
