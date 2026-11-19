---
id: DOT-383
title: Give macOS real test coverage, since no VM scenario proves the branch the parent
  actually runs
status: To Do
created_date: 2026-11-19 09:02
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->

Every VM scenario in this repo targets Linux. There is no macOS scenario in
any topic — every `molecule.yml` under `home/dotfiles` was checked. So the
platform branch the parent machine actually runs is proved by nothing, while
the Linux branch gets a real QEMU guest.

**Measured asymmetry, 2026-11-19 (`apps/loreai`):**

- **8** `Darwin`-gated tasks in `tasks/` (launchd agent install, `launchctl
  print`, Darwin unit paths) — code that cannot execute on Linux at all.
- **6** `Debian`-gated tasks in the mirror position.
- **0** macOS molecule scenarios repo-wide.

A Debian guest therefore proves the *smaller* branch. The launchd install and
its `launchctl` probe are exercised only by manually running the role on the
Mac, and nothing records that as the intended proof.

This is not a new observation — **DOT-101 explicitly scoped it out**:
"macOS is out of scope for VM testing (no macOS boxes exist); this confirms
the Debian leg, and the plan says so plainly." That was correct in its
context. The author now wants macOS coverage, so the decision needs revisiting
rather than inheriting.

**Feasibility, measured on this machine:**

- Apple Silicon (M4 Max), macOS 26.7.3, `Virtualization.framework` present.
- `tart` — macOS and Linux VMs on Apple Silicon — is available through mise
  as `aqua:openai/tart` (`openai/tart`, actively maintained). This is the
  viable macOS-guest path; `limactl` 2.2.1 and QEMU are present but Lima
  targets Linux guests here.
- Apple's licence permits macOS guests on Apple hardware; a guest counts
  against the two-VM allowance.
- No Xcode installed — not required for `tart`, which consumes a restore
  image.

The author's framing also clarifies what the runner is for: `run-role.sh` is
not a VM-only tool. It runs a topic's playbook against `-i localhost,` and is
equally usable inside a guest or on the machine itself. So the harness should
reuse that runner rather than build a parallel path — the difference between
guest and parent is *where it runs*, not what it runs.

Ship:

- **A macOS test path**, chosen with its reason recorded: a `tart`-based
  scenario, a `Virtualization.framework` custom harness, or a documented
  decision that running `run-role.sh` on the parent is the accepted proof for
  the Darwin branch. Each is legitimate; whichever is chosen must be written
  down, not left implicit
- **Coverage for the 8 `Darwin`-gated tasks in `apps/loreai`** — at minimum
  the launchd agent install and the loaded-state probe — reachable by a
  command, not by memory
- **The same runner interface in guest and parent.** `run-role.sh` should be
  the way a topic is exercised in both; the harness supplies the environment,
  not a different entry point
- **A stated limit** on what a macOS guest can and cannot prove: a guest is a
  clean install, not the parent's real home, real launchd session, or
  accumulated state. Say which failures it catches and which it cannot
- **An update to DOT-101's scope line**, so the "macOS is out of scope"
  ruling is superseded explicitly rather than silently contradicted
- **A recorded image and licence position**, since macOS guests have terms a
  Linux image does not

Constraints:

- **Do not make macOS a hard dependency of the ordinary test run.** Linux
  scenarios stay the fast default; macOS is opted into, because it needs
  Apple hardware and a multi-GB restore image.
- **No new harness if `run-role.sh` plus a VM provider suffices.** The failure
  mode here is building a second orchestration layer that drifts from the
  first.
- Do not duplicate DOT-255 (fleet matrix) or DOT-101 (VM harness plan). DOT-255
  already requires that "a machine inventory entry must not silently imply a
  working macOS VM provider" — this task supplies the macOS answer that
  constraint anticipates.
- macOS coverage must be honest about host requirements: Apple Silicon only,
  Apple licensing, and no claim of CI usability until it is proven there.
- Findings and the recommendation go to the author for review before
  implementation, since this reverses a documented scope decision.

Scoped loose per the author's request. The investigation settles which macOS
VM path is worth taking and how many topics get a macOS scenario first.

Decision 2026-11-19: macOS needs real test coverage. A Linux guest proving the
6-task Debian branch while the parent runs the 8-task Darwin branch is not
coverage of the topic.

<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->

- [ ] #1 A macOS test path is chosen and its reason recorded: tart scenario, Virtualization.framework harness, or a documented acceptance that running run-role.sh on the parent is the Darwin-branch proof
- [ ] #2 The 8 Darwin-gated tasks in apps/loreai are reachable by a command, covering at minimum the launchd agent install and the loaded-state probe
- [ ] #3 run-role.sh is the entry point in both guest and parent; the harness supplies the environment rather than introducing a second runner
- [ ] #4 The record states what a macOS guest cannot prove: real home state, the parent's launchd session, accumulated configuration
- [ ] #5 DOT-101's "macOS is out of scope" line is updated so the superseded ruling is explicit
- [ ] #6 The macOS image used and the licensing position are recorded, including that it requires Apple Silicon
- [ ] #7 The ordinary test run does not require macOS: Linux scenarios stay the fast default and macOS is opted into
- [ ] #8 No second orchestration layer is built where run-role.sh plus a VM provider suffices
- [ ] #9 macOS coverage is not claimed usable in CI until it has actually run there
- [ ] #10 The recommendation is surfaced to the author for review before implementation, since it reverses a documented scope decision
- [ ] #11 The board lists DOT-383 with the full description and every criterion: uvx --from backlog-md-py backlog-py board
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
