# backlog-py branch-aware task-id allocation: research findings

Date: 2026-11-08. Question asked: does `backlog-md-py` (or upstream `Backlog.md`)
already handle worktree/branch-aware task-id allocation, or must DOT-328 build
it?

**Conclusion: upstream already fixed it.** The DOT-328 gap exists only in the
installed version (2.1.0). Upstream released **v2.2.0** (2026-10-19) with the
exact fix: `task create` (and draft promotion) no longer hands out an id an
active branch or another git worktree already uses. There is also a new
`task renumber` verb for the collision-recovery case that cost the DOT-323 →
DOT-326 rename. The durable answer for this repo is **upgrade `pipx:backlog-md-py`
from 2.1.0 to 2.2.0** — not building a local allocator.

## Primary sources

- **Installed source** (what actually runs today):
  `/home/bdavis/.local/share/mise/installs/pipx-backlog-md-py/2.1.0/backlog-md-py/lib/python3.14/site-packages/backlog_py/`
  — `backlog-py --version` → `2.1.0`.
- **Upstream repo**: `rmusser01/backlog-md-py` (default branch `main`, source
  under `src/backlog_py/`). Project-URL in the installed package's
  `backlog_md_py-2.1.0.dist-info/METADATA`.
- **Upstream CHANGELOG** (v2.2.0 tag):
  `https://raw.githubusercontent.com/rmusser01/backlog-md-py/v2.2.0/CHANGELOG.md`
- **Upstream source** (v2.2.0 tag): `src/backlog_py/core/repository.py`,
  `src/backlog_py/runtime/git.py`, `src/backlog_py/cli/main.py`.
- **Releases API**: `v2.2.0` is the latest published tag (2026-10-19); `v2.1.0`
  is 2026-09-03. Installed pipx lags one release.

## What v2.2.0 changed (the DOT-328 fix, upstream)

CHANGELOG § 2.2.0, "Fixed" (issue #194):

> `task create` (and draft promotion) no longer hands out an id that an active
> branch or another `git worktree` already uses. It read only this checkout's
> files, while `task list` showed those tasks and warned on the duplicate it had
> just made. Follows `checkActiveBranches`; ids given with `--id` are unchanged.

CHANGELOG § 2.2.0, "Added" (issue #193): `task renumber TASK_ID NEW_ID` — moves a
task and its subtasks to new ids (slugs preserved), repoints parent and
dependency references across active/completed/archived/draft, refuses an id
carried by two files, and refuses an id already used on another active branch or
in another `git worktree` (committed or not).

Source-verified implementation, v2.2.0 `src/backlog_py/core/repository.py`:

- `_allocation_reserved_ids()` (line 1029):
  `return self._reserved_task_ids().union(self._other_checkout_task_files())`
  — the id-allocation view now includes other checkouts' ids, exactly the union
  the installed 2.1.0 `_reserved_task_ids()` lacks.
- `_next_task_id()` (line 1161) now iterates `_allocation_reserved_ids()` instead
  of `_reserved_task_ids()`.
- `_other_checkout_task_files()` (line 1031) → `other_checkout_task_file_names()`
  (`runtime/git.py:285`): names only (an id reservation needs no content, so it
  skips the slow per-ref log walk), gated on `check_active_branches` and
  `_is_git_worktree`, and — critically — also lists **other `git worktree`
  directories** so an *uncommitted* task in another worktree (on no ref) is
  still seen. This closes the gap the 2.1.0 branch-snapshot read path cannot
  (snapshots are ref-bound; a staged/uncommitted sibling task is not).
- Docstring on `_allocation_reserved_ids` states the design: "Other checkouts'
  ids come from file names, which this tool writes as `<id> - <title>.md`.
  Explicit ids (`--id`) are still checked locally only." So the fix protects the
  *auto-allocation* path (DOT-328's concern); a hand-passed `--id` still only
  collides against the local checkout.
- CLI: `_TASK_USAGE` (cli/main.py:124) now advertises `task renumber TASK_ID
  NEW_ID`; dispatcher at :456. No `next-id`/`next_id` verb exists (searched the
  v2.2.0 CLI) — allocation stays internal to `task create`.

## Answered against the DOT-328 framing

1. **Is the installed `_next_task_id()` branch-blind?** Yes, at 2.1.0.
   `_reserved_task_ids()` → `_task_lookup_dirs()` reads only `backlog/tasks`,
   `backlog/completed`, `backlog/archive/tasks` on disk. Upstream 2.2.0 added the
   other-checkout union. (This repo's own prior source read confirmed the same
   lines in the installed 2.1.0 copy.)
2. **Does upstream already ship the fix?** Yes — v2.2.0, one release ahead of the
   installed 2.1.0.
3. **Is there a renumber verb?** Yes — `task renumber`, added in 2.2.0, with
   cross-branch/worktree refusal.

## Recommendation

Upgrade `pipx:backlog-md-py` to **2.2.0** (the mise `pipx` backend installs it;
`apps/mise/files/config.toml` is the entry). Then the DOT-328 mechanism is
upstream-provided: `task create TITLE` is branch-aware, and `task renumber` is
the recovery path for the DOT-323-class collision. A local allocator script is
**not** needed — building one would duplicate shipped upstream behavior and
re-introduce the fork-to-drift risk the repo already records for this tool
family (`docs/BACKLOG-UPSTREAM-CONFIG.md`).

Residual (unchanged by v2.2.0): `--id`/hand-passed ids are still local-only, so
a session that deliberately hand-pins an id (as this session did for DOT-328,
after its own all-refs scan) still needs that manual all-refs check. That is a
narrow, documented carve-out, not the DOT-328 allocation gap.