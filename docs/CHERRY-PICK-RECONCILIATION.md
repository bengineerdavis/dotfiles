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

## The other 8 commits on local `main` are NOT duplicates

They were excluded from the cherry-pick because they belong to other sessions.
Local `main` is 8+ commits ahead of origin in *their* work, not just mine:

| Commits                                        | Branch holding them                                            |
| ---------------------------------------------- | -------------------------------------------------------------- |
| `74fc1daf`, `85b8f99b`                         | `origin/dot-343-bare-lifecycle`                                |
| `765f04a3`, `92ba48c2`, `5c306422`, `b3fb10ac` | `agent/retro-git-topic-local`, `origin/dot-343-bare-lifecycle` |

They are recoverable by branch name if local `main` is reset. **Do not delete
those branches** as part of reconciling `main`.

## What was lost in the divergence

Local `main` never had `4901581b` ("changelog: collect PR #178", a bot commit).
It predates the cherry-pick and had already dropped PR #178's CHANGELOG entry.
That is why the cherry-pick branched from `origin/main` instead of rebasing:
branching included the missing commit by construction. **If you reset local
`main`, reset it to `origin/main`, not to a rebase of the existing local main,
or the changelog entry disappears again.**

## Reconciling

The safe move is `git reset --hard origin/main` after confirming the 8
other-session commits are on their branches (they are, above). That is a
destructive operation on shared local state — **it belongs to the author, not
to an agent**, and it should not happen while any session has uncommitted work
in this checkout.

Related: DOT-386 covers the broader problem of sessions orphaned by the
`~/code/templates` → `~/code/personal/templates` move.
