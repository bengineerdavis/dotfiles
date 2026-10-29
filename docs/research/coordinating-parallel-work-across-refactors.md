# Coordinating parallel work across a refactor

How to land a structural change on `main` while other sessions hold branches
against it, without each stale session re-solving the same breakage its own way.

Written 2026-10-04, the day before the payload move that first used it. The
author decided the workflow live, with research and a red-team pass behind it.
This document is the record of that research and the protocol it produced.

## The problem, in one paragraph

The chezmoi payload is moving from the repo root into `home/` (see `ROADMAP.md`,
"Move the deployed tree under `.chezmoiroot`"). Every open branch predates the
move. When each one syncs, it finds moved paths, moved docs, and re-pointed
fixtures. The fear is not the conflicts — it is divergence: six sessions each
inventing their own resolution, so `main` ends up with six different answers to
the same question. An announcement on the board does not prevent this; a
session mid-task never re-reads the board, and a branch in an external worktree
cannot hear it at all. This repo has proof: the 2026-08-21 history rewrite was
announced in `TASKS.md` with instructions, and no record exists that anyone
ever confirmed the reset happened.

## The research

| Pattern | Source | Verdict |
|---|---|---|
| Trunk-based development — short-lived branches, merge often | [trunkbaseddevelopment.com](https://trunkbaseddevelopment.com/) (Hammant), retrieved 2026-10-04 | **Already this repo's practice.** Branch lifetimes here are hours (four merges to main on 2026-10-03 alone). Confirms the cadence instinct as codified, not new |
| Branch by abstraction — introduce a seam so parallel work continues during the change | [martinfowler.com/bliki/BranchByAbstraction.html](https://martinfowler.com/bliki/BranchByAbstraction.html) (Fowler), retrieved 2026-10-04 | **Adopted** as the seam device. Consumers go through one indirection; the change is one call-site, not N divergent patches |
| Parallel change (expand/contract) — support old and new interface during the migrate phase | [martinfowler.com/bliki/ParallelChange.html](https://martinfowler.com/bliki/ParallelChange.html) (Sato), retrieved 2026-10-04 | **Rejected for this shift.** chezmoi cannot dual-read two source roots, so there is no cheap expand phase. The census plus an atomic flip replaces the migrate window — viable only because one human plus agents makes the window minutes, not months |
| Stacked diffs / PR trains | graphite.dev guides, retrieved 2026-10-04 | **Weak citation** — the guide page returned navigation only. The principle stands from the repo's own stacking rules (§ Branches and integration) |

The repo's own evidence did more work than the external sources:

- Branch lifetimes are hours, with two exceptions (a 53h external worktree and
  a worktree-less remote branch) — the census exists for exactly those
  exceptions.
- `TASKS.md` § Claimed has sat empty despite active sessions — a recorded
  fact. Board announcements are not delivery.
- PR #17's incident: a path constant computed from `Path(__file__)` silently
  resolved the wrong tree from a worktree. A seam that is not worktree-correct
  manufactures the silent-wrongness the protocol exists to prevent.
- Observed update practice is merge-from-main, not rebase — the protocol works
  with that, not against it.

## The protocol

Seven devices. Each names what it is, the artifact or command, and the failure
it prevents.

**1. The runbook lands first.** Before the window opens, a fast decision item
on main carries the per-breakage canonical-fix table — every known thing the
shift breaks, and the one way to fix each. Drawn from the shift's research
inventory. This is what makes stale-session resolution mechanical instead of
creative.

**2. The census runs before the window.** Enumerate every branch not merged
into `origin/main`; record a disposition per branch in the shift item — *land
now*, *rebase-and-green*, or *abandon with deadline*. Explicit rows for
external worktrees and worktree-less branches, because those are the ones a
banner never reaches. The author confirms the table. Re-run commands:

```bash
git fetch origin
git for-each-ref --format='%(refname:short)' refs/heads refs/remotes/origin \
  --no-merged=origin/main
git merge-tree --write-tree origin/main <branch>   # exit 0 clean, 1 conflicts
```

**3. A sentinel test proves the loudness.** One test that is green on the old
layout and demonstrably red on the new, proven before the flip merges — so
"fail loud, never silently-wrong" is demonstrated, not asserted. Paired with
the post-flip check: `chezmoi status` shows exactly the expected pending set
and nothing else (a wrong `.chezmoiroot` is a silent empty source state —
status clean, apply plans mass deletion).

**4. Session-start sync.** Merge-or-rebase from main at session start, and once
more if the branch predates the shift commit. Not rebase-before-every-push: a
rebase voids the branch's test evidence, forcing a full re-run at every push,
and merge-from-main is the observed practice here. Sync at the start is what
guarantees the runbook is read.

**5. Observe, don't patch — with an expiry.** A stale session hitting a
breakage the runbook covers applies the runbook's fix. A breakage it does not
cover becomes an observation written to the board, not a local patch — the
runbook grows by one row, once, for everyone. If the mover does not respond
within ~4h (generous against this repo's hourly merge cadence), the session may
patch locally with an `Observation:` commit trailer accepting rework. Recorded
judgment that reports itself is how this repo already treats honest action;
without the expiry, "observe, don't patch" becomes "stop, don't work".

**6. The seam, scoped honestly.** Layout-agnostic indirection (a shared path
constant, dynamic resolution) protects branches created *after* it — a pre-move
branch using the seam rebases clean. Branches that predate the seam get nothing
from it; the census owns them. Built worktree-correct (resolve from the
worktree root, per the PR #17 lesson).

**7. Reconcile after.** When the shift lands, re-run the census: every
pre-shift branch is marked merged, rebased-and-green, hold-with-deadline, or
abandoned-with-note; unknown becomes a follow-up item. This is the step whose
absence made the 2026-08-21 outcome unknowable.

### For a new reader: the kitchen

We are about to move every pot to a new cabinet. Before touching anything, we
walk the kitchen with a clipboard: who is cooking, what are they holding, when
are they done? Each cook gets a label — *plate it up first* (land), *keep
cooking, here is the new map when you look up* (rebase-and-green), *this recipe
failed anyway* (abandon, with a note). The clipboard is the census; the new map
is the runbook; the post-move walk-around is the reconcile. If a cook finds a
drawer the map missed, they write it on the clipboard rather than improvising —
so one person extends the map once and every cook uses the same fix.

## Applied: the 2026-10-04 payload move

The first census, run 2026-10-04 against `origin/main` at `110cb3c`
(two PRs — #42 uv work-machine capture, #43 ollama_gpu_fallback — had merged
while the research ran). Dispositions confirmed by the author.

| Branch | Age | Worktree | vs origin/main | `merge-tree` | Disposition |
|---|---|---|---|---|---|
| `agent/chezmoiroot-plan` | <1d | live | 4↑ / 6↓ | clean | **Land now** — decisions + runbook precursor |
| `agent/queue_closeout` | <1d | live | 1↑ / 5↓ | clean | **Land now** |
| `agent/shift_left_scan` | <1d | live | 1↑ / 10↓ | conflicts (TASKS.md) | **Rebase → land now** |
| `feat/ollama-manifest-scope` (PR #41) | 53h | external `~/code/work/sentry` | 3↑ / 28↓ | clean | **Land now** — author reviewing; before the move |
| `origin/agent/repo-manager` | ~2d | none | 28↑ / 77↓ | conflicts | **Active hold** — deadline 48h after the move lands, else salvage (5 research docs) + abandon |
| `run-role-cwd-fix` | hours | the main checkout, uncommitted | at tip | n/a | **Author-held** — lands before the move |
| backups ×3 (`pre-reconcile`, `pre-unscramble`, `pre-reword`) | — | none | never merge | — | Out of scope by design |
| 6 merged remote branches | — | none | merged | — | Delete at next housekeeping |

Landing order confirmed: all four landable branches first, then the author's
in-flight work, then the move window opens.

## What running it taught us

Complete as of 2026-10-19: all four preps (hooks, seam, binned, pin) ran as
execution sessions and are collected on main; one branch per task held
throughout; the budget (3) capped dispatch and queued the fourth. What the
full run taught:

- **Every stall was a permission mechanic, never a work problem.** Compound
  commands, unallowlisted checks (`bash -n`, pyrefly), and checks against
  other checkouts all auto-reject in headless. The relay absorbed each at
  one message: the coordinator ran the check and returned the answer via
  `-s` continuation. The executor's permission refusals (push, merge,
  branches) are the lane enforcement working, not friction to remove.
- **The coordinator hits the same walls.** My own relay commands were
  auto-rejected twice for compounding; a session id grepped from a log went
  stale ("Session not found") — session ids come from `opencode session
  list`; a `cd` before `git branch -d` pointed the delete at the wrong
  HEAD. One writer per worktree applies to the collector too.
- **Intent-instead-of-work stops are normal, not failures.** Two executors
  ended turns with plans. Each recovered on a one-message continuation;
  dispatch prompts now say "end only when the commit exists".
- **Sessions survive gaps.** Twelve days passed mid-test (dispatch Oct 7,
  completion Oct 19); the worktrees held uncommitted work intact, the
  sessions resumed via `-s`, and the catch-up was one fetch plus a
  merge-tree check. The ground-shift devices (census, runbook) were what
  made resuming legible.
- **A second coordinator appeared mid-run.** Relay titles I did not write
  sat between mine in the session list. I stood down on dispatch rather
  than risk conflicting instructions, and resumed on the author's word.
  The protocol needs a rule for this: when relay ownership is unclear, the
  coordinator polls and collects but does not re-dispatch.
- **Executor judgment earned trust twice.** The binned executor declined
  `ruff format` on grounds the dispatch never mentioned (it would inject
  3.14-only syntax into a portable script) and was right; the seam executor
  designed around a conftest load-order collision the task line never
  anticipated (the sys.modules alias). Naive workers are not mindless ones.
- **pyrefly checks project state, and group-scoped deps break that.** The
  molecule tests import testinfra (opt-in `test-vm` group), so the
  pre-commit pyrefly hook failed on every machine without the group —
  fixed by excluding the molecule tree (`merge de46484`), which had to ride
  the merge commit because prek stashes unstaged changes during hooks:
  config fixes must be staged with the commit that needs them.
- **Collect means verify, not trust** (unchanged from the pilot, and it
  held: executor reports matched coordinator re-runs every time).
