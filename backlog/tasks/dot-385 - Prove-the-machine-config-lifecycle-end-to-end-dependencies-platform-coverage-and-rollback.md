---
id: DOT-385
title: 'Prove the machine-config lifecycle end to end: dependencies, platform coverage,
  and rollback'
status: To Do
created_date: 2026-11-19 17:19
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->

DOT-382, DOT-383 and DOT-384 were filed separately because they are different
failure modes, but they are one project: **can a topic be installed on a
machine, proven on the platform that machine runs, and undone if it goes
wrong?** Filed apart, each is scoped loose and none of them knows what the
others assume. This task is the umbrella that keeps them coherent.

The three, and why they are one question:

- **DOT-382 — dependencies.** What the topic needs on Linux, declared by the
  role rather than satisfied by the test harness. Includes the warrant for why
  a guest pass implies a parent pass.
- **DOT-383 — platform coverage.** macOS has no scenario at all, while the
  parent runs 8 Darwin-gated tasks against 6 Debian-gated ones. A Linux guest
  proves the smaller branch.
- **DOT-384 — rollback.** A `chezmoi apply` is one-way today. APFS snapshots
  exist and nothing uses them; `pop-os` needs a Linux answer; the borg backup
  design (DOT-56/DOT-177/DOT-178) is adjacent but is not rollback.

**The shared assumptions that need settling once, not three times:**

- **What "proven" means.** DOT-382 requires a transfer argument (why a guest
  pass implies a parent pass). DOT-383 requires the same for macOS. DOT-384
  requires a proven restore. All three are the same discipline — a check that
  has been seen to fail — and should share one vocabulary rather than three.
- **Which machine is the target.** `pop-os` is the fleet's Linux member
  (`machines.yml`); the Mac is the parent. Requirements, coverage and rollback
  must all name the same machines or they will disagree.
- **What the runner is.** `run-role.sh` takes `-i localhost,` and works in a
  guest or on the parent. DOT-383 forbids a second orchestration layer; DOT-382
  and DOT-384 must not invent one either.
- **Ordering.** DOT-384 is meant to be in place *before* the first real apply,
  which makes it a prerequisite for acting on the other two rather than a
  peer. That relationship is currently recorded in prose, not as a dependency.

**Gaps the loose scoping left open, needing research and grilling:**

- **pop-os's filesystem is unmeasured.** DOT-384's Linux answer depends on
  whether it is btrfs, ZFS, LVM, or plain ext4 — and nothing in the repo
  records it. This decides whether rollback is a snapshot or a borg archive.
- **No Linux snapshot tooling is declared anywhere.** No btrfs, ZFS, snapper,
  timeshift, or LVM reference exists in any topic or doc.
- **borg is not installed.** `pipx:borgbackup` sits commented out in the mise
  config; DOT-56 chose borg 1.4.x with borgmatic but nothing is provisioned.
  If rollback reuses borg, that install becomes a dependency of DOT-384.
- **The macOS VM path is unproven.** `tart` is in the mise registry and
  Virtualization.framework is present, but no macOS guest has been booted
  here. DOT-383 assumes it works.
- **Whether one tool serves both rollback and backup** is an open design
  question, not a detail — it decides whether the fleet carries one substrate
  or two.

Ship:

- **A single statement of what "proven" means** across the three tasks, so
  DOT-382's transfer argument, DOT-383's platform coverage and DOT-384's
  restore proof use one standard
- **The machine set named once**: the Mac as parent, `pop-os` as the Linux
  fleet member, and which of the three tasks applies to which
- **The ordering made explicit** — rollback before the first real apply, and
  what that implies for sequencing the other two
- **A research pass on the open gaps above**, with findings recorded rather
  than assumed: pop-os filesystem, available snapshot tooling, borg's install
  state, and macOS guest feasibility
- **A grilling pass on the design questions** the research cannot settle:
  one substrate or two, snapshot versus archive, and how much of the fleet
  each mechanism must cover
- **The three tasks cross-referenced** so a reader of any one finds the others
  and the shared assumptions

Constraints:

- **Do not collapse the three into one task.** They are different failure
  modes with different proofs; the umbrella coordinates, it does not merge.
- **Do not resolve the open questions by assumption.** pop-os's filesystem and
  the macOS guest path are unmeasured; measuring them is the work.
- Research and grilling are inputs to the three tasks, not a substitute for
  them. This task closes when the gaps are filled and the tasks are coherent,
  not when a document exists.
- No duplication of DOT-255 (fleet matrix) or DOT-101 (VM harness plan).
- Findings go to the author for review; this coordinates, it does not
  unilaterally re-scope the children.

Scoped loose deliberately. The author asked for research and grilling to fill
the gaps the individual tasks left open.

Decision 2026-11-19: the three tasks are one project and must be aware of each
other, with shared assumptions settled once and open gaps closed by research
and grilling rather than assumption.

<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->

- [ ] #1 One statement of what "proven" means is recorded and referenced by DOT-382, DOT-383 and DOT-384, so all three use the same standard
- [ ] #2 The machine set is named once: the Mac as parent, pop-os as the Linux fleet member, and which task applies to which
- [ ] #3 The ordering is explicit: rollback in place before the first real apply, and what that implies for sequencing the other two
- [ ] #4 pop-os's filesystem is measured and recorded, since DOT-384's Linux mechanism depends on it
- [ ] #5 Available snapshot tooling is researched and recorded: btrfs, ZFS, LVM, snapper, timeshift, and what pop-os actually supports
- [ ] #6 borg's install state is recorded, including that pipx:borgbackup is commented out, and whether DOT-384 depends on provisioning it
- [ ] #7 macOS guest feasibility is proven or recorded as unproven: tart is in the mise registry and Virtualization.framework is present, but no guest has been booted here
- [ ] #8 A grilling pass settles the design questions research cannot: one substrate or two, snapshot versus archive, and fleet coverage per mechanism
- [ ] #9 DOT-382, DOT-383 and DOT-384 cross-reference each other and this umbrella, so a reader of any one finds the others
- [ ] #10 The three tasks remain separate; the umbrella coordinates rather than merges them
- [ ] #11 Findings are surfaced to the author for review rather than re-scoping the children unilaterally
- [ ] #12 The board lists DOT-385 with the full description and every criterion: uvx --from backlog-md-py backlog-py board
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
