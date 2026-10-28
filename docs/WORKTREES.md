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

**The main checkout stays on `main`.** A task branch is never checked out
there: the main checkout is the collector every session shares, and its
branch is shared state — switching it moves governance files under every
other session's feet and turns branch hygiene into a stash dance (observed
2026-10-27, PR #87). Task branches get their own worktree from the start.

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
4. **Bucket** — when finished work needs more reviewable merges than the task
   planned, split it into buckets before publishing. See § Bucketing below.
5. **Collect** — merge serially, suite after each, ordered inert → behaviour →
   activating. Merging uses an **ephemeral scratch worktree**
   `.worktrees/<sid>_merge_<n>`, recreated per attempt from (base + input
   SHAs): re-running `git merge` in a conflicted tree is not idempotent;
   rebuilding from SHAs is.
6. **Reap** — a branch is deleted only after
   `git merge-base --is-ancestor <branch> main` proves the work landed. Never
   `git branch -D` before that check. A branch whose commits were
   cherry-picked into buckets never becomes an ancestor, because the copies
   have new SHAs; prove it landed with `git cherry main <branch>` instead,
   where every line starting `-` means that patch is already on main. Crash
   recovery is `git worktree remove --force <path>` plus `git worktree prune`.

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
