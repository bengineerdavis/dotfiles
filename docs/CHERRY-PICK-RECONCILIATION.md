# Local `main` holds duplicates of PR #186

**For any session working in this checkout.** Read this before reconciling
`main`.

On 2026-11-19 the 15 commits behind PR #186 were **cherry-picked** onto a branch
cut from `origin/main`, then merged. The originals are still on this checkout's
local `main`, which has never been reset. So the same changes exist twice under
different SHAs.

They are duplicates, not separate work. **Do not re-apply them, and do not
assume local `main` contains unmerged contributions.**

## The mapping

Old SHA (local `main`) → new SHA (on `origin/main` via `fb141d52`). Verified by
diffstat, not by commit-message similarity: `8cd1b650`→`3de4aada` (1 file,
+75), `063897e1`→`eaf4126a` (3 files, +310/−22), `628a7171`→`838b924d`
(1 file, +116).

| Old        | New        | Subject                                                                 |
| ---------- | ---------- | ----------------------------------------------------------------------- |
| `8cd1b650` | `3de4aada` | backlog: decision-7 — chezmoi owns the ~/code tree                      |
| `baac9b90` | `74856845` | backlog: decision-7 — record the impact graph                           |
| `d11a7746` | `48fa9226` | backlog: decision-7 — correct the graph where the probes disagreed      |
| `6233d445` | `3ddba0c7` | docs: capture gita's breakage as redge design feedback                  |
| `ac4c5198` | `455a104c` | backlog: queue DOT-381                                                  |
| `063897e1` | `eaf4126a` | loreai: add a docs map and a regenerable index                          |
| `eec0e6bf` | `1b031c9d` | backlog: correct DOT-381 — .lore.json exists                            |
| `fe906440` | `4fb68aa6` | backlog: queue DOT-382                                                  |
| `1dbe711b` | `420486f7` | backlog: DOT-382 — a VM must preview the target                         |
| `9d38b1eb` | `33aa5e02` | backlog: DOT-382 — prove dependencies, do not reproduce the environment |
| `cd6f8ce9` | `f9a1eeef` | backlog: DOT-382 — state the warrant                                    |
| `17e1a897` | `50d26ba1` | backlog: queue DOT-383                                                  |
| `812c83ca` | `6bcf8403` | backlog: DOT-382/384 — name pop-os                                      |
| `fadfecf8` | `6897660b` | backlog: queue DOT-385                                                  |
| `628a7171` | `838b924d` | backlog: queue DOT-386                                                  |

One extra commit exists only on origin: `efc0fdc3` — "DOT-381 — each repo imports
its own lore knowledge, no shared config". It was made on the branch after the
cherry-pick and has no old-SHA counterpart.

## The other commits on local `main` are NOT duplicates

They were excluded from the cherry-pick because they belong to other sessions.
Local `main` is 31 commits ahead of origin in *their* work, not just mine
(measured 2026-11-20; re-measure with `git rev-list --count origin/main..main`
before trusting this number).

**Read this before resetting anything.** A commit is only safe to drop if it is
reachable from a branch that outlives the reset. Three are not:

| Group                            | Count | Where it lives        | Safe if `main` is reset?     |
| -------------------------------- | ----- | --------------------- | ---------------------------- |
| `origin/preserve/dot349-handoff` | 20    | pushed                | yes                          |
| `origin/dot-343-bare-lifecycle`  | 8     | pushed                | yes                          |
| **stranded**                     | **3** | **local `main` only** | **NO — reset destroys them** |

The three stranded commits, each reachable from `main` and from nothing else:

- `a3278e00` — backlog: hand off inherited docs failures after retro fixes
- `c25b94c4` — backlog: release the DOT-343 wrap-up claim; capture `.lore.md`
  re-distillation
- `9ec504aa` — backlog: close DOT-348 — ADHD skills merged via PR #188

If you are about to reset, **re-run the classification** rather than trusting
this table; commits land on `main` between the measurement and the reset:

```sh
# Commits ahead of origin/main that no remote branch contains.
for c in $(git rev-list origin/main..main); do
  [ -z "$(git branch -r --contains "$c" | head -1)" ] &&
    git log -1 --format='STRANDED %h %s' "$c"
done
```

An empty result is the precondition for a safe reset. A non-empty result means
those commits need a branch (or a PR) before anything destructive happens.

## Branches that must outlive the reset

`agent/retro-git-topic-local` and `handoff/local-main-2026-11-19` hold the same
commits as the pushed branches above, but they are **local-only** — pushing the
commits is what makes them survive, not the local branch names. Do not delete a
branch that appears in the classification output without checking it is pushed.

## What was lost in the divergence

Local `main` never had `4901581b` ("changelog: collect PR #178", a bot commit).
It predates the cherry-pick and had already dropped PR #178's CHANGELOG entry.
That is why the cherry-pick branched from `origin/main` instead of rebasing:
branching included the missing commit by construction. **If you reset local
`main`, reset it to `origin/main`, not to a rebase of the existing local main,
or the changelog entry disappears again.**

## Reconciling

A `git reset --hard origin/main` is only safe **after** the classification above
returns no stranded commits. As measured on 2026-11-20 it returns three, so the
precondition does not currently hold — resetting now would destroy them.

Sequence, in order:

1. Run the stranded-commit loop above. If it prints anything, get those commits
   onto a branch (a PR is the usual way) and re-run until it prints nothing.
1. Confirm no session has uncommitted work in this checkout.
1. Reset.

That is a destructive operation on shared local state — **it belongs to the
author, not to an agent**, and it should not happen while any session has
uncommitted work in this checkout.

Related: DOT-386 covers the broader problem of sessions orphaned by the
`~/code/templates` → `~/code/personal/templates` move.
