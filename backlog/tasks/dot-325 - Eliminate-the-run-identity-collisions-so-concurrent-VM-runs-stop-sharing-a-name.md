---
id: DOT-325
title: Eliminate the run-identity collisions so concurrent VM runs stop sharing a name
status: To Do
created_date: 2026-11-08 17:20
labels:
- design
- testing
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
DOT-303 and DOT-309 left two naming ambiguities open, and both are the same
underlying problem: **a run has no unique identity**. This task fixes that
rather than documenting around it.

### Ambiguity 1 — every run is called `lima-mol`

`home/dotfiles/apps/lima/molecule/debian/molecule.yml:10` fixes the platform
name at `lima-mol`, for every run, on every checkout, forever. It is
deliberate: line 9 records that the Lima SSH socket path must stay under
`UNIX_PATH_MAX=104`, and `"lima-mol" keeps the full sha1 hash within budget`.

Consequences, measured or observed:

- Two concurrent runs collide on one instance name. The second does not get
  its own VM; `create` is not idempotent against a running instance of the
  same name, so it fails rather than adopting it.
- A leftover cannot be attributed to a run. DOT-309's report says
  "N other /tmp/lima-* root(s) present; not mine to remove" precisely because
  it cannot tell whose they are.
- **This became sharper with PR #143**, which allows `limactl delete` in the
  worktree tier. Two sessions running VM tests concurrently could now have one
  delete the other's live VM. PR #143 keeps `delete` at *ask* in the autonomous
  tier, which limits but does not remove the hazard — the worktree tier allows
  it outright.

The budget is real, not a guess: the socket path is `hash + name + suffix`, so
a longer name spends a fixed allowance. But the headroom is also real —
`lima-mol` is 8 characters, and the sha1 is 40. `lima-mol-a1b2c3` is 15 and
still fits, which is why DOT-309's notes suggested a 6-hex run id.

### Ambiguity 2 — the `/tmp` root is a hash of a moved path

DOT-309's Linux reaper ages `/tmp/lima-*` by glob, which works without
attribution. But the `/tmp` name is `sha1(ephemeral dir path)`, so:

- Moving the ephemeral dir changes the hash and orphans anything under the old
  one. DOT-303's relocation from the in-source location changed it from
  `fc5b5f0f60b5` to a per-checkout value, which is why the task carries a
  one-time sweep.
- The name encodes a path, not a run. Two runs in the same checkout and
  scenario produce the *same* `/tmp` name, so the directory is shared state
  between sequential runs and clobbered by concurrent ones.

A run-id-derived name would fix both: stable against moving directories, and
distinct per run.

### What this task is not

Not a reaper. DOT-309 decided reporting over reaping for leftovers, and PR
#143's permission model still asks before `delete` in the autonomous tier.
This is about giving a run a name that identifies it, so whatever does the
reporting or reaping can act on the right thing.

### Constraints to respect

- **The 104-character socket budget.** Verify the arithmetic rather than
  trusting the note; the failure is a `bind: file name too long` at
  VM-start time, which reads like a Lima bug.
- **`destroy` must still find what `create` made.** The name is derived, so
  anything that recreates it must derive the same value — a run id stored
  only in the shell will not survive the destroy that runs in a subprocess.
- **A macOS solution must not be assumed.** DOT-323 decides what a Mac does;
  do not pre-empt it here.
- **`.molecule` state is per checkout now**, so the ephemeral dir already
  disambiguates checkouts. The remaining collision is across *runs*.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The socket-path arithmetic is measured, not asserted: the longest candidate name is shown to keep the full socket path under `UNIX_PATH_MAX=104`, with the computation recorded
- [ ] #2 A run carries an identifier that distinguishes it from a concurrent run in the same checkout and scenario
- [ ] #3 The identifier survives from `create` to `destroy` — a destroy in a separate process resolves the same value, proven by a test rather than by inspection
- [ ] #4 The `/tmp` root name is derived from the run identity, not from a filesystem path that a later relocation can change
- [ ] #5 Two concurrent runs in one checkout neither share an instance nor delete each other's, demonstrated by a test or by a recorded manual proof
- [ ] #6 The leftover report can name whose artifact it found, or says plainly that it still cannot and why
- [ ] #7 The rejected naming schemes are recorded with the reason each failed, so the choice is not re-litigated
- [ ] #8 `tests/run_molecule` stays green, and every new guard is proven by a mutation that fails the right test
<!-- AC:END -->

## Implementation Notes
<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
Read: PR #148 (the four-part cleanup answer), DOT-303, DOT-309, and
`docs/research/topic-vm-tests/CLEANUP-GUARANTEES.md` § Where artifacts
accumulate.

The measured facts this task builds on, so they are not re-derived:

- `sha1('<…>/molecule/debian/.molecule')` = `fc5b5f0f60b59a87423c25989c8969b3a474d2fb`,
  and that directory was still on disk from an aborted run holding a disk
  image — the derivation is confirmed, not inferred.
- Relocating the ephemeral dir changes the hash, so the name tracked the
  *path*, not the run.
- `home/dotfiles/apps/lima/molecule/debian/molecule.yml:9-10` and `:26` are
  where the platform name lives; `tests/run_molecule` pins the wrapper's env
  handling and is the natural place for the new assertions.

Techniques worth reusing from PR #148: run the wrapper against a restricted
PATH to reproduce a platform you cannot test directly, and assert a derived
value by recomputing it in the test rather than hardcoding the expected
string.

Watch out for the collision that bit PR #148 twice: backlog ids are allocated
per checkout, and a parallel branch can take the number you chose. Allocate
above the highest id visible in *every* worktree, not just `origin/main`.

Related: DOT-307 (worktree state is invisible to backlog-py — adjacent
identity problem in the tooling); DOT-256 (fail-closed destructive cleanup,
which is the rule any reaper must follow); PR #143 (the permission tier that
makes a mis-targeted delete possible).
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 A run has a name that identifies it, and neither a concurrent run nor a relocated directory can make two runs share one
<!-- DOD:END -->
