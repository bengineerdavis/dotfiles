---
id: DOT-366
title: Restore the personal subdirectory structure gita failed to migrate across machines
status: To Do
created_date: 2026-11-15 22:08
priority: high
updated_date: 2026-11-15 22:09
dependencies:
  - DOT-171
  - DOT-172
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->

`docs/LAYOUT.md:14` requires the named subdirs to sit inside `personal/`,
never as siblings at the top level. Measured on L37V3P6GQ3 2026-11-16: seven
template repos sit at `~/code/templates/`, `try/` holds three repos and
`captures/` exists, all at `~/code/` — while `~/code/personal/templates/` is
an empty directory created 2026-11-14. The catalogue records the intended
shape correctly (`projects/personal/templates/agentic-project-template`), so
the structure held on the Linux machine and flattened on migration to this
Mac. 43 of 49 catalogue entries carry the `projects/` prefix that no longer
matches either machine, which is why gita re-registered the repos wherever
they happened to land instead of restoring their nesting.

Ship:

- The named subdirs moved under `personal/` on this machine: `templates/`,
  `try/`, `captures/`, with the empty duplicate removed
- Catalogue paths that match where repos actually live, with the stale
  `projects/` prefix resolved
- Gita registrations re-pointed to the moved paths so `gita ll` reports the
  real locations
- A check that fails when a declared repo's path does not match its
  catalogue entry, so the next migration cannot silently flatten the tree

Constraints:

- Verify each repo's remote and branch survive the move before removing any
  old path; a move that loses uncommitted work is worse than the drift
- Gita registers repos on disk and never clones as a side effect, so moves
  happen first and registration follows
- Paths stay machine-agnostic in the catalogue — the layout is shared, the
  absolute prefix is not
- Other sessions hold worktrees under these repos; moving a repo invalidates
  worktree gitdir pointers, so check for live worktrees before moving and
  repair or defer those repos
- The second machine needs the same end state, so record what it must run
  rather than assuming it is already correct

<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria

<!-- AC:BEGIN -->

- [x] #1 templates/, try/ and captures/ sit under personal/ on this machine, and the empty personal/templates/ duplicate is gone
- [x] #2 Catalogue paths match where repos actually live, with the stale projects/ prefix resolved
- [x] #3 gita ll reports the moved paths, with no registration pointing at a vanished location
- [ ] #4 A check fails when a declared repo's path does not match its catalogue entry
- [x] #5 Live worktrees under moved repos are repaired or the move is deferred, with no broken gitdir pointer left behind
- [x] #6 The second machine's required end state is recorded, not assumed

<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->

**Relation to the G-series.** DOT-171 (G2) defines the catalogue and
machine-file contract, including that declarations say what should exist while
gita and disk say what is actually cloned. DOT-172 (G3) clones missing
declarations and adopts existing registrations. This task is neither: it
repairs drift that already happened on one machine, where disk and catalogue
disagree about nesting rather than about membership. It depends on both
because the path convention has to be settled before paths are rewritten, and
because adoption is what will re-register the moved repos.

**Evidence gathered 2026-11-16 (L37V3P6GQ3).** `~/code/` holds `archive`,
`captures`, `forks`, `personal`, `templates`, `try`, `work` as siblings;
`docs/LAYOUT.md:38` lists `templates/`, `try/`, `captures/` and `interviews/`
as subdirs of `personal`. `~/code/templates/` holds seven repos
(agentic-project-template, Best-README-Template, copier-cat,
copier-mise-sandbox, copier-template-copier-template, copier-testkit,
dotfile-topic-copier); `~/code/personal/templates/` is empty.
`home/dotfiles/config/repos.yaml` has 49 declarations, 43 carrying a
`projects/` prefix from the Linux layout, and `gita group ls` shows three flat
groups (personal, forks, work) with no subdirectory awareness.

**Open question for the author.** The catalogue's `projects/` prefix predates
the `~/code` layout. Whether to rewrite those 43 entries to the current shape
or treat the prefix as a machine-local root is a contract question owned by
DOT-171; this task should not invent an answer.

<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

**Done on the Mac, 2026-11-19.** Four of six ACs hold with evidence; #4 is
handed off as its own task (DOT-388), #5 verified by inspection.

- **#1 — moved and verified.** `~/code` is `AGENTS.md, forks, personal, work`
  (measured 2026-11-19); templates (7 repos) and try (3) sit under
  `personal/`; `captures/` and `interviews/` exist under `personal/` (both
  were empty — the moves renamed the dirs). The top-level `templates/` husks
  (two AGENTS.md-only dirs from a partial earlier migration) were removed with
  the author's approval.
- **#2 — PR #177 merged** (`f95af948`, 2026-11-17): catalogue re-pointed to the
  type dirs; **PR #183 merged** (`583de54b`, 2026-11-19): final nesting —
  `personal/templates/…`, `personal/try/…`, `tutorial/` re-homed. 49
  declarations, no stale top-level refs, `tests/gita` 17 passed on both.
- **#3 — live state reconciled.** Topic install run 2026-11-19 re-registered
  the moved repos; the run's blind `gita add` left 7 duplicate-name rows in
  repos.csv (old path + new path per name, 87 rows / 78 repos) — repaired by
  hand (`gita rm` + `gita add` per name, verified 0 dupes, 78 rows). That
  defect is DOT-387, not left in the topic.
- **#5 — nested worktrees survived.** `git worktree list` inside the moved
  `copier-template-copier-template` shows its two `.worktrees/` checkouts
  resolving at the new path and `git status` runs clean inside them (gitdir
  pointers are relative; measured 2026-11-19).
- **#4 — NOT done; handed off as DOT-388** (a check that fails when a
  declared repo's path does not match its catalogue entry). Next session
  picks it up there.
- **#6 — recorded:** the Linux box needs the same three mv steps plus a topic
  install run; its catalogue will report ~44 declared-but-not-cloned until its
  own migration lands (docs/LAYOUT.md phase 5, DOT-306).

Remaining live-state note: `ai-prompt-library-escalation-writing` is a gita
registration and catalogue entry whose repo was deleted from disk after
2026-11-12 — the author decided to keep it declared (flagged in PR #183), so
it reports declared-but-not-cloned by design until DOT-172 (G3) or a future
sweep resolves it.

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done

<!-- DOD:BEGIN -->

<!-- DOD:END -->
