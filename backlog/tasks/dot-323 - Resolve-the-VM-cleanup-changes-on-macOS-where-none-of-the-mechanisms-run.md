---
id: DOT-323
title: Resolve the VM cleanup changes on macOS, where none of the mechanisms run
status: To Do
created_date: 2026-11-08 17:10
labels:
- bug
- testing
- cross-platform
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
DOT-303 and DOT-309 changed how VM test runs clean up after themselves
(PR #148). Every mechanism they add is Linux-only or GNU-tooled, and macOS has
none of it. This task decides what a Mac should do instead.

**What shipped, and what macOS does not have.**

| Part | Mechanism | On macOS |
|---|---|---|
| 1 | state out of the source (`XDG_STATE_HOME`) | works — POSIX paths |
| 2 | `timeout` bounding the run | `timeout` absent; brew provides `gtimeout` |
| 3 | `systemd-tmpfiles` ages `/tmp/lima-*` | **absent** — no systemd |
| 4 | leftover report at wrapper start | works, but `sha1sum` was GNU-only |

Two of the four broke outright on a Mac and were fixed before merge in
commit `ba2be76` on that branch:

- `sha1sum` is GNU; a Mac has `shasum` and `openssl`. The wrapper now probes
  all three.
- macOS ships bash 3.2, where expanding an EMPTY array under `set -u` is
  fatal. The `login` path did exactly that; the unbounded path is now its
  own branch.
- A Mac has no `timeout`; `gtimeout` comes from brew. Both are probed, and
  the run fails closed naming the fix.

**What is still unsolved for a Mac.** Part 3 has no equivalent. The wrapper
reports a leftover, and `timeout` bounds the run, but nothing ages out a
`/tmp/lima-*` root left by a killed run. `home/.chezmoiignore:26` already
excludes `tmp.conf` from non-Linux targets, so a Mac silently gets no reaper.

Part 3 is also the part whose semantics we measured rather than assumed, so
the replacement must be measured the same way: the Linux rule works because
the age basis includes ctime — a running VM keeps its timestamps fresh while
a dead one ages. A `launchd` periodic job or a reaper inside the wrapper
would need to prove the same property, or prove a different one deliberately.

**A prior decision blocks this.** `docs/research/topic-vm-tests/PLAN.md:141`
says "macOS is out of scope for VM testing" — no macOS Vagrant boxes exist,
recorded 2026-10-06, and line 531 repeats it for the Darwin leg. So this may
resolve as "document that a Mac does not run VM tests", not as "build a
Mac reaper". That call is the first thing to make, and it is the author's.

**Ruled out already, so they are not re-litigated.** Each was verified
against the artifact, not recalled:

- `molecule reset` — `command/reset.py:51` is `# pragma: no cover`; the driver
  hook at `driver/base.py:394-400` is an empty body. Only docker and podman
  implement it, so it is a no-op for the Vagrant and delegated-Lima drivers
  this repo uses.
- `limactl prune` — prunes unreferenced objects; an orphan still refers to its
  own disk, so prune keeps it.
- Upgrading molecule — upstream `main` is still `except ScenarioFailureError`
  at `command/base.py:377` with no signal handling.
- A hand-rolled reaper on Linux — duplicates the deployed `systemd-tmpfiles`
  machinery.

**Do not break the Mac while fixing the Mac.** `home/dotfiles/apps/gnu-tools`
puts GNU coreutils on PATH (`libexec/gnubin`), and `apps/homebrew` installs
`coreutils`, but **nothing declares `gnu-tools` as a dependency** — it is
opt-in. So the wrapper cannot assume `timeout` or `sha1sum` exists, which is
why the probes are load-bearing rather than defensive.

Context: PR #148 carries the implementation and its evidence.
`docs/research/topic-vm-tests/CLEANUP-GUARANTEES.md` has the measured
mechanism, and `prototype-cleanup-model.html` (same directory) models which
failure modes leak which artifacts.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The prior "macOS is out of scope for VM testing" decision in `docs/research/topic-vm-tests/PLAN.md` is either reaffirmed or reversed on the record, with the date and the author's ruling
- [ ] #2 If reaffirmed: the wrapper says plainly on a Mac that no aging reaper exists there, and the Lima README states the gap rather than leaving it implicit
- [ ] #3 If reversed: a Mac mechanism for aging out `/tmp/lima-*` is chosen against the same requirement DOT-309 used — a run that dies for any reason must leave nothing that persists silently — and its rejected alternatives are recorded with evidence
- [ ] #4 Whichever branch is taken, `scripts/run-molecule.sh` is exercised on a Mac, or the task states explicitly that it was not and why
- [ ] #5 The four parts are enumerated in one table showing what works on each of the two platforms, so the next reader does not re-derive it
- [ ] #6 No part regresses on Linux: `tests/run_molecule` stays green, including the probes added in `ba2be76`
<!-- AC:END -->

## Implementation Notes
<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
Read first: PR #148, DOT-303, DOT-309, and
`docs/research/topic-vm-tests/PLAN.md` § Destroy safety and § Decision 4.

The three probes in `scripts/run-molecule.sh` (SHA-1, `timeout`/`gtimeout`,
and the empty-array branch) exist because a Mac failed each one. Their tests
in `tests/run_molecule/test_run_molecule.py` run the wrapper against a PATH
holding only `shasum`, which reproduces the Mac failure on Linux — reuse that
technique rather than adding a Mac-only test that cannot run here.

`~/.local/state` is the XDG default macOS does not set; the wrapper falls
back to `$HOME/.local/state`, so part 1 needs no change. Check that assumption
rather than trusting this note.
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 A reader can say what a Mac does for each of the four cleanup parts without reading the code
<!-- DOD:END -->
