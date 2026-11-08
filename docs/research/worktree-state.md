# Worktree state: what exists, and the vendor-neutral seam

Research recorded 2026-11-08, before designing anything. Every claim below was
measured on this machine, not inferred from documentation.

## The problem

An agent working in a worktree cannot see what other worktrees are doing. Two
concrete failures, both measured:

1. **`backlog-py` cannot see an uncommitted task created in a worktree.** With
   `checkActiveBranches: true`, a task *committed* on another branch is visible
   from the main checkout — the tool reads branch snapshots. A task created
   but not committed is invisible, and `doctor` still reports "No problems
   found." That is the silent-resurrection shape DOT-246 exists to prevent,
   confirmed as a live property of the tool.
2. **Nothing records which agent holds which worktree.** Leases exist in
   backlog's orchestration metadata, but they are per *task*, not per
   *worktree*, and nothing connects a running agent process to a directory.

## What worktrunk already does

Worktrunk v0.81.0 is adopted here (mise config line 99). Its state model is the
important finding:

**State lives in plain git config, in the shared common dir, keyed by branch.**

```bash
$ wt config state vars set probe=hello
✓ Set probe for main

$ git config --local --get-regexp 'worktrunk.state'
worktrunk.state.main.vars.probe hello
```

Four properties follow, and they are what make it a usable seam:

| Property | Measured |
|---|---|
| Storage is git config | `git config --local`, not a private database |
| Namespace is stable | `worktrunk.state.<branch>.<key>` |
| Visible from every worktree | the common dir is shared, so a value set in one worktree reads in another |
| Keyed by branch, not global | a value set in a worktree did **not** appear when read from `main` — it sat under `worktrunk.state.agent/gita-worktree-registration.vars.wtprobe` |

That last row is the subtle one and the reason the seam works: the *store* is
shared, the *address* is not. State cannot leak between branches by accident,
but any worktree can read any branch if it names it.

Other state kinds worktrunk keeps, from `wt config state get`: default branch,
previous branch, branch markers (`worktrunk.state.<branch>.marker`), custom
vars, CI status cache, summary cache, git-commands cache, hints, operation logs
under `.git/wt/logs`.

Markers are already an agent-facing surface: its plugin sets `🤖` while an agent
works and `💬` when idle, and `wt list` renders them. For CLIs without a plugin,
the documented integration is three commands (`wt config state marker set`,
`set 💬`, `clear`) on session events.

## What is vendor-neutral about it

Nothing above requires worktrunk to *use* it. The seam is:

- **git config as the transport.** Any tool can write
  `git config --local <namespace>.<branch>.<key> <value>` and any other tool
  can read it. No daemon, no lock file, no schema server.
- **branch as the address.** A worktree is identified by its branch, which both
  git and every agent tool already know. No new identifier has to be invented
  or kept in sync with `git worktree list`.
- **namespaces per producer.** `worktrunk.state.*` is worktrunk's. A different
  producer writes its own namespace and neither has to know the other's
  internals — the same one-namespace-per-producer rule `refs/notes/*` follows.

So the shape a neutral layer could adopt:

```
<producer>.state.<branch>.<key> <value>
```

with the convention that consumers read unknown namespaces through git config
rather than a private API, and treat a missing key as unknown rather than as a
default.

## How backlog's task model informs this

Backlog stores one file per task, marker-delimited sections, and a front-matter
block carrying identity (`id`, `status`, `created_date`) plus orchestration
fields (`status_key`, `lease_owner`, `lease_expires_at`, `version`). Three
things that model gets right and a worktree-state design should copy:

1. **One record per addressable unit.** One file per task; one git-config key
   per branch-and-property. A single shared blob requires lock-and-rewrite, and
   two agents writing at once lose each other's updates.
2. **Identity in the record, not the path.** The task id survives a rename; the
   branch name survives a worktree move. Neither depends on a directory.
3. **A version field for optimistic concurrency.** Backlog's `version` makes a
   stale write fail cleanly instead of silently winning. Any state two agents
   may write needs the equivalent — or must be single-writer by construction.

And one thing it gets wrong, which is the defect in DOT-307: **the record's
location is not visible across worktrees.** A backlog task file lives in a
worktree's working tree, so it exists only on that branch. Git config does not
have this problem, because it lives in the common dir rather than any working
tree.

## What this suggests for the design

Not a conclusion yet — the options to weigh:

- **A. Adopt worktrunk's namespace directly.** Write `worktrunk.state.<branch>.*`
  keys from our own tooling. Zero new machinery, but couples us to an internal
  namespace worktrunk owns and may change.
- **B. A project-owned namespace alongside it.** `dotfiles.state.<branch>.*`,
  with docs describing how a consumer (including worktrunk) reads it. Neutral
  by construction, but nobody reads it until a consumer exists.
- **C. Use worktrunk's public `vars` command only.** `wt config state vars` is
  a documented interface; treat it as the API and never touch the config key
  directly. Stable against storage changes, but limited to what that command
  models and unavailable to tools that do not depend on worktrunk.
- **D. Do nothing structural; document the convention.** Record the
  `<producer>.state.<branch>.<key>` shape in `docs/WORKTREES.md` so any tool
  that arrives later has a defined place to write. Cheapest, weakest.

The measurement that should decide it: whether a consumer exists today. If the
only job is "an agent can see what other worktrees hold", then C plus D may be
enough, and A/B are speculative structure — the same "one adapter is a
hypothetical seam" rule `codebase-design` states.
