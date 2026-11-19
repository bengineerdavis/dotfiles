---
id: DOT-384
title: Make a chezmoi apply reversible at the OS level before running one on the real
  machine
status: To Do
parent_task_id: DOT-385
created_date: 2026-11-19 09:02
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->

Testing in a VM reduces the blast radius of a bad apply, but it does not remove
it: eventually a topic runs on the real machine. The author's ask is that when
that happens, the change can be rolled back to the state before the last
`chezmoi apply` — at the OS level, not by re-running the role and hoping.

No such mechanism exists today. Measured 2026-11-19 on this machine:

- `/` is APFS, so **local snapshots are available** — `tmutil listlocalsnapshots
  /` runs and the volume already carries an OS-update snapshot
  (`com.apple.os.update-…`). The primitive exists; nothing uses it.
- **Time Machine has no destinations configured** (`tmutil: No destinations
  configured`). So snapshots are not currently being taken on a schedule, and
  there is no safety net underneath a manual one.
- No script, topic task, or doc references snapshotting or rollback around a
  `chezmoi apply`. `docs/LAYOUT.md` mentions rollback only as a phase-ordering
  principle, not a mechanism.

`chezmoi` itself is a one-way applicator: it does not snapshot the destination,
so an apply that removes a file or installs a bad service unit is not
self-reverting. Roles have `remove.yaml`, but removal is *not* rollback — it
runs the topic's teardown, which is not the inverse of an arbitrary partial
apply, and it cannot restore home-directory state the apply overwrote.

The relevant failure this guards against is concrete and recent: a topic apply
that deploys a broken unit, replaces a config a later tool depended on, or
half-completes between two tasks. Recovery today means reconstructing intent
from memory, or restoring from a backup that is older than the change.

**Rollback is not backup, and the repo already has a backup design.**

DOT-56 (BK1) chose borg 1.4.x with borgmatic; DOT-177 (BK2) proves local
recovery and DOT-178 (BK3) proves off-host append-only recovery. DOT-167 owns
the broader state-backup path. Those answer *"the machine is gone or a file is
lost — restore it"*, measured in hours, from another device.

This task answers a narrower question: *"the apply I just ran was wrong —
put the machine back the way it was five minutes ago."* That is local, fast,
and pre-apply. Conflating them produces a design that is too slow to be a
rollback and too weak to be a backup.

They can share a substrate. A pre-apply `borg create` archive is a legitimate
rollback primitive — borg deduplicates, so successive pre-apply archives are
cheap — and it works on any filesystem, which matters because the Linux
answer cannot assume btrfs. The alternative is a filesystem snapshot
(btrfs/ZFS/LVM), which is instant but only exists where the volume supports
it. The task must pick per platform and say which property each provides.

Ship:

- **A snapshot-before-apply mechanism** with a defined restore path, proven
  end to end: take a snapshot, make a deliberate breaking change, restore, and
  confirm the machine returned to the prior state
- **A stated recovery bound**: exactly how much state the snapshot restores
  (whole volume, `/Users`, or config paths), and what it does not cover — a
  snapshot is not a substitute for the off-machine backup in DOT-167
- **A pre-apply gate or hook** so the snapshot is taken by the act of
  applying, not by remembering to ask for one. A manual-only path is the
  failure mode this is meant to prevent
- **A Linux mechanism, not a footnote.** `pop-os` is a real fleet member
  (`machines.yml`), so the Linux answer is required, not optional. The
  candidates differ in kind and must be chosen against the filesystem actually
  in use there: btrfs/ZFS snapshots (instant, only if the volume is btrfs or
  ZFS), LVM snapshots (instant, needs LVM), or a pre-apply `borg create`
  archive (works on any filesystem, slower, deduplicated). Measure pop-os's
  filesystem before choosing; do not assume ext4 or btrfs
- **The relationship to the BK backup series settled explicitly.** DOT-56
  (BK1) already chose borg 1.4.x with borgmatic, and DOT-177/DOT-178 (BK2/BK3)
  prove local and off-host recovery. Those are *backup*: off-machine,
  append-only, retention-bounded, hours to restore. Rollback is a different
  property — local, fast, pre-apply, minutes. They must not be conflated, but
  they can share a substrate: a pre-apply `borg create` is a legitimate
  rollback primitive because borg archives are deduplicated snapshots. State
  which of the two each mechanism provides, and whether one tool serves both
  or the design needs two
- **Interaction with Time Machine settled**: either configure a destination so
  local snapshots are taken continuously, or record why an on-demand snapshot
  is sufficient without one

Constraints:

- Do not treat topic `remove.yaml` as rollback. It is teardown, not an inverse;
  a role that overwrites a file cannot restore what was there. Any design that
  assumes removal is enough has to say so and be rejected explicitly.
- A snapshot restores the volume, not intent. It must not be presented as a
  replacement for the backup design in DOT-167/BK1–BK4 or for review before an
  apply.
- Prove the restore, not just the snapshot. An untested restore path is the
  same class of defect as a passing check that has never been seen to fail.
- Do not run a destructive restore against the live machine as part of
  development without the author's explicit approval and a verified second
  copy of anything unrecoverable.
- Keep it usable before the first real apply: this is meant to be in place
  *before* the machine is changed, so ordering matters relative to DOT-383's
  macOS coverage work.
- No claim of rollback protection for state a snapshot cannot see (open files,
  in-flight agent sessions, external services).

Scoped loose. The investigation settles which snapshot mechanism, the restore
bound, and whether Time Machine is configured as part of it.

Decision 2026-11-19: OS-level rollback to the pre-apply state is a prerequisite
for running a topic on the real machine, not a later convenience.


**Part of DOT-385** — the umbrella for the machine-config lifecycle. Sibling tasks: DOT-382 (Linux dependencies) and DOT-383 (macOS coverage). Shared assumptions (what "proven" means, which machines are targets, and that `run-role.sh` is the only runner) are settled there, not here.

<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->

- [ ] #1 A snapshot-before-apply mechanism exists with a defined restore path, proven end to end: snapshot, deliberate breaking change, restore, confirm the prior state returned
- [ ] #2 The recovery bound is stated: which state the snapshot restores and what it does not cover
- [ ] #3 The snapshot is taken by the act of applying via a pre-apply gate or hook, not by remembering to request one
- [ ] #4 Topic remove.yaml is explicitly not treated as rollback, with the reason recorded: teardown is not an inverse of a partial apply
- [ ] #5 A Linux mechanism is chosen for pop-os, measured against its actual filesystem rather than assumed, covering btrfs/ZFS snapshots, LVM snapshots, or a pre-apply borg archive
- [ ] #6 The rollback-versus-backup boundary is stated: which property each mechanism provides, and whether one tool serves both or two are needed
- [ ] #7 The relationship to DOT-56/DOT-177/DOT-178 is recorded, so rollback does not duplicate or contradict the borg backup design
- [ ] #8 Time Machine interaction is settled: either a destination is configured for continuous local snapshots, or the record explains why an on-demand snapshot suffices without one
- [ ] #9 The restore is exercised, not just the snapshot; an untested restore path is not accepted as protection
- [ ] #10 No destructive restore is run against the live machine during development without explicit author approval and a verified second copy of unrecoverable data
- [ ] #11 The mechanism is in place before the first real apply, with ordering relative to DOT-383 recorded
- [ ] #12 The limits are stated: state a snapshot cannot see (open files, in-flight sessions, external services) is not claimed as protected
- [ ] #13 The board lists DOT-384 with the full description and every criterion: uvx --from backlog-md-py backlog-py board
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->

<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->
