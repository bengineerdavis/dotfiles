---
id: DOT-328
title: Make backlog-py task-id allocation branch-aware (a `next-id` verb)
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
`backlog/config.yml` `prefixes.task`) and `_reserved_task_ids()` already spans
`tasks/` + `completed/` + `archive/tasks/`, so completed ids are never reused.
The gap: it is **branch-blind**. `_task_lookup_dirs()` reads only the three
on-disk directories in the current checkout; it never reads other branches'
task files, so a sibling branch holding DOT-323/324/325 is invisible to it —
the exact collision this task records.

Meanwhile `checkActiveBranches: true` (backlog/config.yml) already makes the
*visible-record scan* load task files from other local branches — that is what
powers `tests/backlog/test_queue_integrity.py::test_no_shadowed_task_ids`. The
allocator and the guard read different views of the id space, so they disagree.

Goal: an id-allocator that resolves the SAME all-refs/active-branches view the
guard uses — a `backlog-py task next-id` verb (or equivalent) so an agent can
ask "what is the next free DOT id" and get a branch-aware answer, and `task
create TITLE` (no `--id`) stays correct even across sibling branches.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
1. There is a mechanical way to learn the next free id that scans ALL refs
   (the same input `checkActiveBranches`/the integrity guard uses), not just
   the three on-disk directories. Either a `backlog-py task next-id` verb or a
   small helper script in this repo.
2. The helper returns the largest id + 1 across `git for-each-ref` heads/remotes
   `ls-tree` of `backlog/`, and is seen to produce a *different* answer than the
   on-disk-only `_next_task_id()` when a sibling branch holds a higher id
   (mutation-proven against the DOT-323 case: it must return 324, not 323).
3. The finding is recorded as an upstream-or-local fix decision: if `backlog-py`
   can be patched upstream, the change is proposed there; if not, the local
   script is documented in `docs/agents/issue-tracker.md` so the next session
   reaches for it instead of hand-deriving `--id`.
4. `docs/agents/issue-tracker.md`'s "the tool owns ids" rule and the actual
   creation flow no longer contradict: either `--id` stops being the only way
   to specify an id, or the doc states the branch-aware path.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
Source of truth, verified 2026-11-08 by reading the installed `backlog_py`
source (pipx 2.1.0, Python 3.14):

- `repository.py:1006` `_next_task_id()` — `max + 1` over the prefix.
- `repository.py:205` `_reserved_task_ids()` — spans `list_tasks()` +
  `_lookup_task_records_cached()` (active + completed + archive).
- `repository.py:156` `_task_lookup_dirs()` — the three on-disk dirs only; this
  is the branch-blind gap.
- `checkActiveBranches` config feeds the visible-record scan, not the allocator.
- `decisions.py` `_next_decision_id`, `documents.py` `_next_document_id`,
  `drafts.py` `_next_draft_id` share the same `max + 1` pattern but are single-
  bucket (no cross-branch source for decisions/docs/drafts either).
- `cli/main.py:125` usage: `task create TITLE` (positional) is the documented
  create form; `--id` is optional and its omission already triggers
  `_next_task_id()` — but branch-blind.
- `backlog-py doctor --help` exists (reports unreadable files + duplicate ids,
  `--fix`/`--json`) but exposes no free-id query.

The free-id problem is symmetric with the shadowing the guard already solves:
both need the merged view of every branch's `backlog/tasks`. The cleanest fix
makes the allocator take the same input the guard takes, rather than adding a
third, separate scanner.

**The exact asymmetry (confirmed in installed 2.1.0, and to be re-checked
upstream — see `docs/research/backlog-id-worktree/FINDINGS.md`):** the READ path
is branch-aware and the WRITE path is not.

- `ReadOnlyRepository.__init__` (repository.py:91) sets
  `include_active_branch_snapshots=True`, so `task list` / `board` load
  `_load_active_branch_records()` from `runtime/git.py`
  `list_active_branch_task_snapshots()` (git.py:240, gated by
  `checkActiveBranches`). That is why the duplicate-id guard *sees* the sibling
  branch's DOT-323.
- `MutableRepository.__init__` (repository.py:501) sets
  `include_active_branch_snapshots=False`, and the mutation path —
  `create_task` → `_next_task_id` (repository.py:1006) → `_reserved_task_ids`
  (repository.py:205) → `list_tasks`/`_task_lookup_dirs` (repository.py:156) —
  all read **only the three on-disk dirs**. So `task create` computes its next
  id from the local working tree alone and will collide with a sibling branch
  holding a higher id.

The fix is therefore precise: make the *allocator* branch-aware — either by
giving `MutableRepository` the same `_load_active_branch_records` input the read
path already has (and having `_reserved_task_ids` fold those ids in), or by a
`next-id` verb that runs the branch-aware scan before `create`. The machinery
already exists in `runtime/git.py`; it is wired to the reader, not the writer.

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