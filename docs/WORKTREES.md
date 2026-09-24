# WORKTREES.md

The naming contract and lifecycle for agent worktrees in this repository. The
design rationale lives in `TASKS.md` § Now #1 and its sub-items; this file is
the stable reference an agent checks before creating, merging, or deleting a
worktree.

## Layout

Worktrees live **in-tree at `.worktrees/`**. The dot prefix makes them
invisible to chezmoi (probed 2026-09-22: a dot-prefixed source dir appears in
neither `chezmoi managed` nor `chezmoi status`), so they never deploy.
`.worktrees/` is in the tracked `.gitignore`.

Naming is **flat, never grouped**:

```
.worktrees/<sid>                  one agent session
.worktrees/<sid>_sub_<slug>       a sub-agent of that session
.worktrees/<sid>_merge_<n>        an ephemeral merge scratch worktree
```

Grouping (`<sid>/sub_a`) collides git's admin dirs across sessions —
`.git/worktrees/` keys on the basename only — and destroys the
admin-dir→path mapping exactly when debugging a wedged session.

## Branch names

**Underscore, never slash.** Refs are files: `refs/heads/agent/x` and
`refs/heads/agent/x/sub_a` cannot coexist, so `agent/<sid>_sub_<slug>` is the
form. A sub-worktree branches off its **parent branch**, not main. Git
enforces a single-branch lock — one branch may be checked out in exactly one
worktree — so a sub-agent never reuses its parent's branch name.

## One writer per worktree

A worktree is one index plus one mutable filesystem. Many readers, one
writer: read-only subagents (search, analysis, review) fan out freely inside
one worktree; every writer gets its own. Patch-producing writers are rejected
— a diff is good transport and a bad execution environment; patches are right
only for a read-only subagent proposing an edit it never ran.

Sub-agent venvs use `UV_LINK_MODE=copy` — independent bytes, so a sub-agent
can `uv add`/`remove` without corrupting the cache or a sibling. Venvs never
merge; only declarations (pyproject.toml, uv.lock) do.

## Lifecycle

One lifecycle for every worktree, so a wedged session is recoverable by
inspection:

1. **Spawn** — `git worktree add .worktrees/<sid> -b agent/<sid>`.
2. **Fan-out** — sub-worktrees off the parent branch, named as above.
3. **Provision** — venvs with `UV_LINK_MODE=copy`; consumers offline
   (`UV_OFFLINE=1 --frozen`), provisioners serialised.
4. **Collect** — merge serially, suite after each, ordered inert → behaviour →
   activating. Merging uses an **ephemeral scratch worktree**
   `.worktrees/<sid>_merge_<n>`, recreated per attempt from (base + input
   SHAs): re-running `git merge` in a conflicted tree is not idempotent;
   rebuilding from SHAs is.
5. **Reap** — a branch is deleted only after
   `git merge-base --is-ancestor <branch> main` proves the work landed. Never
   `git branch -D` before that check. Crash recovery is
   `git worktree remove --force <path>` plus `git worktree prune`.

## chezmoi from a worktree

chezmoi's source directory is fixed (`~/.local/share/chezmoi`), not
cwd-relative. From a worktree, `chezmoi add` needs `-S "$PWD"` or it writes
into the main checkout and silently lands work on another branch:

```bash
chezmoi -S "$PWD" add ~/bin/<script>
```

The deployed tree cannot be branched — `~/bin/<script>` is one file no matter
how many branches hold versions of it — so agents never run `chezmoi apply`
from a worktree (or at all; applying is main-only, by the author or a session
holding the apply claim).
