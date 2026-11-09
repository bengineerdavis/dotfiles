# WORKTREES.md

The naming contract and lifecycle for agent worktrees in this repository.
This file is the stable reference an agent checks before creating, merging, or
deleting a worktree.

**worktrunk** (mise entry, 2026-10-23) is the CLI for the mechanics:
`wt switch -c <sid>` creates and enters, `wt list` shows status, `wt merge`
and `wt remove` handle the end of a branch. Its path template is configured
to the Layout below; the contract itself — flat names, underscores, one
writer, the merge-base proof before deletion, one PR per work item — is
house policy, and worktrunk does not carry it. Opt-in features that
generate content (LLM commit messages, LLM list summaries) stay OFF:
commit messages follow CONTRIBUTING.md, full stop.

## Layout

Worktrees live **in-tree at `.worktrees/`**. The dot prefix makes them
invisible to chezmoi (probed 2026-09-22: a dot-prefixed source dir appears in
neither `chezmoi managed` nor `chezmoi status`), so they never deploy.
`.worktrees/` is in the tracked `.gitignore`.

**The main checkout stays on `main` — it is shared state, and chezmoi acts on
it.** chezmoi resolves its source dir to the main checkout
(`~/.local/share/chezmoi`) unless `-S "$PWD"` points at a worktree, and every
command that reads or writes source — `git pull`, `chezmoi apply`, `chezmoi
status`, `chezmoi diff` — acts on whichever branch is checked out there. A task
branch left checked out there poisons each of them:

- `git pull` reconciles the wrong branch ("main is behind" reads the task
  branch's tip);
- `chezmoi apply` deploys that branch's files over the single deployed tree;
- `chezmoi status` / `chezmoi diff` report phantom drift — source is the stale
  branch, so a target whose deployed copy already matches `main` reads as `M`.

So a task branch never sits in the main checkout (observed 2026-10-27, PR #87),
and before any reconcile or apply there, run `git branch --show-current` and
stop unless it is `main`. Measured 2026-11-08 (a reconcile on a concurrent
session's branch reported non-fast-forward with no local commits) and 2026-11-09
(a phantom `M dotfiles/update.sh` where the deployed copy already carried
PR #154's `-K` logic).

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

## Is this work owned?

Before touching a branch, ask whether another session is already on it. An
empty claims board is not an answer — `AGENTS.md` § Branches and integration
explains why it cannot be. Three signals, cheapest first:

1. **A claim** on the covering task (`backlog-py orchestration claims`).
2. **A live worktree** for the branch — `git worktree list`, plus whether its
   working tree has uncommitted edits.
3. **A recent PR update** — `gh pr view <n> --json updatedAt`. Treat a PR
   updated within roughly the last 30 minutes as owned. Measured 2026-11-09: a
   branch whose claim board was empty had landed a review-fix commit at 08:35Z,
   and only `updatedAt` distinguished it from three idle siblings. Merging
   under that author would have landed a state they had not finished.

Two sessions building the same feature costs more than either alone: the merge
conflicts, and one of the two gets closed unreviewed. When signals disagree,
trust the most recent activity and ask rather than assume.

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

1. **Spawn** — `git worktree add .worktrees/<sid> -b agent/<sid>`. With
   Worktrunk, `wt switch --create <sid>` runs the pre-switch helper first:
   clean `main` is fetched and fast-forwarded before the branch is created.
   Dirty or diverged `main` stops creation; existing task branches and stacked
   parents are not reset. See `docs/BRANCH-SYNC.md`.
2. **Fan-out** — sub-worktrees off the parent branch, named as above.
3. **Provision** — venvs with `UV_LINK_MODE=copy`; consumers offline
   (`UV_OFFLINE=1 --frozen`), provisioners serialised. Before a rebase,
   commit `.lore.md` as a lore-sync commit (7b16160 and d346429 are
   this): a background process owns its content, `git stash` moves it
   out from under that process, and a stash that pops mid-rebase
   collides. `git rebase --autostash` is a stash too — it does not make
   the rule moot.

   The same rule covers ordinary commits, because the pre-commit hook
   stashes too. When a commit aborts with "Stashed changes conflicted
   with hook auto-fixes" while the hook's own tests passed, the cause is
   usually `.lore.md` churn mid-run: commit `.lore.md` alone first, then
   the real commit. Measured 2026-11-09 across four failed commits; the
   hook's message names test failures, so the real cause is invisible
   unless the ordering is known.
4. **Bucket** — when finished work needs more reviewable merges than the task
   planned, split it into buckets before publishing. See § Bucketing below.
5. **Collect** — merge serially, suite after each, ordered inert → behaviour →
   activating. Merging uses an **ephemeral scratch worktree**
   `.worktrees/<sid>_merge_<n>`, recreated per attempt from (base + input
   SHAs): re-running `git merge` in a conflicted tree is not idempotent;
   rebuilding from SHAs is.
6. **Reap** — a branch is deleted only after you have proven the work landed
   on `main`. Never `git branch -D` before that check. `git merge-base
   --is-ancestor <branch> main` proves it only for a real merge commit; the
   repo squashes PRs, and squash rewrites every commit SHA, so the branch tip
   is never an ancestor and the check reports "not merged" even after the PR
   merged. Verify by content instead: the squashed files and lines are present
   on `main` (`git show main:<path>`), or `git cherry main <branch>` — every
   line starting `-` means that patch is already on `main`. Crash recovery is
   `git worktree remove --force <path>` plus `git worktree prune`.

## Arriving from a PR

A session can be summoned by a PR instead of the queue — a review comment, a
review request, a merge job. The entry path is identical for a human, an
agent, or automation:

1. **Fetch and locate.** `git fetch origin`, then find the PR branch —
   `gh pr view <n> --json headRefName -q .headRefName`. Worktree it:
   `git worktree add .worktrees/<sid> <branch>`. If git refuses because the
   branch is already checked out elsewhere — the authoring session may still
   hold it — fall back to the sub-branch form: `.worktrees/<sid>_sub_<slug>`,
   branching off the PR branch.
2. **Claim.** An orchestration lease names the task and the worktree,
   so a live authoring session sees it before it pushes.
3. **Work and push.** Feedback applied on the PR branch — or on a sub-branch
   merged back into it — updates the PR on push. Merge gates apply to what
   the push contains, not to who asked for it.
4. **Reap** as in the lifecycle: a PR branch becomes an ancestor of `main`
   when its PR merges, and is then deleted like any other.

Pull requests go into `main` and nowhere else — see § Bucketing step 6 for
the failure that rule prevents.


## Bucketing

A bucket is one set of commits that merges as one pull request. Most
bucketing happens earlier, when a task is written: `docs/PROCESS.md` § Decomposing
work into items cuts the queue so that one task is one merge. This section
covers the case the plan missed — a task whose finished work turns out to
hold more than one merge.

**The test for a bucket: describe it in one sentence without "and".** The
sentence names one outcome for one thing — a topic, a role, a script or a
document. One topic can need several buckets: owning 1Password's desktop app
and restarting it when stale are two features of one topic, and each could
merge alone. Whether to split them is a judgment call: PR #12 keeps them
together by the author's choice. CONTRIBUTING.md § Commit granularity applies the same test to a
single commit.

1. **Bucket.** Sort the commits by outcome. Split a commit that fails the
   test. Keep a commit's tests in the same bucket as the commit.
2. **Order.** Classify each bucket's dependency (`docs/PROCESS.md` § What kind of
   dependency is it). A bucket that stands alone branches from `main`; one
   that needs another's code branches from that bucket's branch. Stack two
   deep freely.
3. **Build.** Give each bucket its own branch and worktree, named for its
   outcome, and copy commits in with `git cherry-pick -x` so each records its
   original SHA. Revise the task so each bucket has its own task file.
4. **Check each alone.** Every commit passes its focused tests, so
   `git bisect` works across the bucket. The tip passes the full suite.
5. **Check them together.** Merge every open bucket with `git merge-tree`,
   which writes no refs and touches no worktree, in more than one order.
   Every order must produce the same tree. Run the full suite on that tree in
   a scratch worktree. When the buckets replace an existing branch, diff the
   combined tree against that branch merged into `main`: only intended
   differences may remain.
   Expect one kind of conflict: task lines that two buckets appended to the
   the queue. Keep both tasks; the bucket that merges
   second resolves it.
6. **Publish.** Pull requests go into `main` and nowhere else. Feature
   branches may take commits and merges from each other freely, with no PR.
   A PR opened against another feature branch merges into that branch, not
   `main`: PR #12 did, after its parent #11 had landed, and had to be
   re-landed as #15.
   - A bucket that branches from `main`: push it and open its PR with
     `gh pr create --base main`.
   - A bucket that branches from another bucket: push it, but open no PR yet.
     When the parent merges, rebase the child onto `main` (or merge `main`
     into it), re-run step 4, then open its PR against `main`.
   - To let the reviewer see a child early, link its branch from the parent's
     PR description, for reading only.
7. **Supersede.** Close whatever the buckets replace, with links to them;
   update handoffs; reap with `git cherry` as in step 6 of the lifecycle.

PR #5 (split into #11 and #12 on 2026-09-24) is the worked example.

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
