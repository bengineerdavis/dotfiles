---
id: DOT-328
title: Upgrade backlog-py to 2.2.0 for branch-aware task-id allocation
status: To Do
created_date: 2026-11-08 21:35
labels:
- backlog-py
- tooling
- queue-integrity
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Manual DOT-id allocation collided twice in one session: first DOT-323 (already
claimed on sibling `agent/vm-cleanup-impl`), then a hand-rolled `grep` loop
mis-read the id space (`^dot-$n -` never matches `dot-316 - Title.md`). The
queue-integrity guard caught the first collision at commit time — correctly,
fail-closed — but it only *surfaces* the collision; it does not *prevent* it.

The tool already allocates: `backlog_py/core/repository.py` `_next_task_id()`
computes `max + 1` over the configured prefix (`DOT`, from
`backlog/config.yml` `prefixes.task`) and `_reserved_task_ids()` spans
`tasks/` + `completed/` + `archive/tasks/`, so completed ids are never reused.
In the **installed 2.1.0** it is branch-blind: `_task_lookup_dirs()` reads only
the three on-disk directories in the current checkout, so a sibling branch
holding DOT-323/324/325 is invisible to it — the exact collision this task
records.

**The fix is upstream, not local.** `backlog-md-py` v2.2.0 (2026-10-19) added
branch-aware id allocation: `task create` (and draft promotion) no longer hands
out an id that an active branch or another `git worktree` already uses
(`_allocation_reserved_ids()` = `_reserved_task_ids().union(_other_checkout_task_files())`,
repository.py:1029), and added a `task renumber TASK_ID NEW_ID` verb that
refuses an id used elsewhere — the recovery path for the DOT-323-class
collision. Research record: `docs/research/backlog-id-alloc/FINDINGS.md`.

Goal: upgrade `pipx:backlog-md-py` from 2.1.0 to 2.2.0 so the branch-aware
behaviour is available here, instead of building a local allocator that would
duplicate shipped upstream behaviour.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
1. `backlog-py --version` reports `2.2.0` (or later) after apply. The entry is
   already `"pipx:backlog-md-py" = "latest"`
   (`home/dotfiles/apps/mise/files/config.toml:94`), so the `latest` float
   should resolve to ≥2.2.0; if it holds at 2.1.0 because mise's resolution is
   cached, pin `2.2.0` explicitly rather than leaving a stale `latest`.
2. `task create TITLE` (no `--id`) is proven branch-aware on this repo: with a
   throwaway sibling branch holding a task at a higher id than every on-disk
   task file, `task create` allocates an id above the sibling's — not the
   on-disk-only `max + 1` (mutation-proven against the DOT-323 case: it must
   not return the id a sibling branch already holds).
3. `task renumber` is exercised once as the collision-recovery path, and its
   cross-branch refusal is confirmed (renumbering onto an id held by another
   active branch/worktree is refused).
4. `docs/agents/issue-tracker.md`'s "the tool owns ids" rule and the creation
   flow no longer contradict: the doc states that `task create TITLE` (no
   `--id`) is branch-aware as of 2.2.0, and that a hand-passed `--id` is still
   checked locally only.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
Primary sources, verified 2026-11-08:

- Installed `backlog-py --version` → **2.1.0**; upstream latest release
  **v2.2.0** (2026-10-19). One release behind. Upstream source lives under
  `src/backlog_py/` (the installed sdist flattens it into `site-packages/backlog_py/`,
  which is why the raw `backlog_py/…` path 404s upstream).
- Upstream CHANGELOG v2.2.0 "Fixed" (#194): "`task create` (and draft
  promotion) no longer hands out an id that an active branch or another `git
  worktree` already uses… Follows `checkActiveBranches`; ids given with `--id`
  are unchanged."
- Upstream CHANGELOG v2.2.0 "Added" (#193): `task renumber TASK_ID NEW_ID`.
- v2.2.0 `repository.py:1029` `_allocation_reserved_ids()` =
  `_reserved_task_ids().union(_other_checkout_task_files())`; `_next_task_id`
  (line 1161) now iterates that union. `_other_checkout_task_files()` →
  `runtime/git.py:285` `other_checkout_task_file_names()`: names only (id
  reservation needs no content — skips the slow per-ref blob walk), gated on
  `check_active_branches` + `_is_git_worktree`, and ALSO lists `git worktree
  list --porcelain` dirs so an *uncommitted* task in another worktree is seen
  (ref-bound snapshots cannot see it).
- Docstring on `_allocation_reserved_ids`: "Explicit ids (`--id`) are still
  checked locally only." So auto-allocation is branch-aware; a hand-pinned id
  still needs a manual all-refs scan — the narrow carve-out this session used
  when filing DOT-328.

Build-vs-upgrade: this is an **upgrade**, not a build — the AGENTS.md outsource
ladder does not apply because nothing is being built here. The `pipx:` backend
already owns `backlog-md-py`; pinning a newer release is configuration.

Upgrade mechanics: change the `pipx:backlog-md-py` version in
`home/dotfiles/apps/mise/files/config.toml` (the `github:`-backend convention
is for release binaries; `pipx:` is the existing backend for this tool — keep
it). Apply is author-run (agents never run `chezmoi apply`); a re-apply of the
mise config plus `mise reshim` makes the new version live. Verify with
`backlog-py --version`.

Related: DOT-326 (the template-sweep tool), DOT-314/DOT-310 (queue-integrity
and `.molecule` scratch), the "task-242/task-244 TASK-prefix stragglers
collide with DOT ids" gotcha (renumber next-free, fail-closed).
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->