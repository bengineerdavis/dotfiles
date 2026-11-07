---
id: DOT-296
title: Make the Xcode CLI Tools prerequisite usable unattended
status: To Do
created_date: 2026-11-05 04:40
labels:
- now
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
`apps/homebrew/tasks/prerequisites.yaml` is the only thing in the repo that touches
Xcode Command Line Tools, and it does the right thing on an attended machine
(`xcode-select --print-path` to probe, `--install` when missing). Two problems
make it insufficient.

**1. `xcode-select --install` cannot complete unattended.** It opens a macOS
dialog and returns; the command itself exits 0 immediately. So:

- `changed_when: xcode_install.rc == 0` is true on every run where it fires,
  even though nothing was installed.
- Ansible moves on to `community.general.homebrew` while the dialog is still
  asking a human to press a button, so a headless or agent-driven run fails
  later, at whatever needs `cc`, with an error that names the consumer rather
  than the cause.
- There is no wait, so the task cannot distinguish "already installed",
  "installing, come back in ten minutes", and "a human declined".

**2. It is unreachable for a machine that does not run the homebrew topic.**
The prerequisite lives inside `apps/homebrew`. `apps/mise` is the topic that
actually needs a compiler on macOS (its `cargo:` backends compile Rust crates),
and `topic_requires: [homebrew]` would make mise unschedulable on Linux, which
`AGENTS.md` forbids. A topic-tier prerequisite cannot be reached by a
runtime-manager-tier topic without violating the layering rule.

Consequence, measured 2026-11-04: a fresh macOS box would run mise's `cargo:`
entries before anything installs a compiler, so the Rust work that landed in
DOT-281/DOT-282 is correct on Debian and unverified on macOS for this reason.

### Why this is not simply "add topic_requires"

`topic_requires` is plan-time validation, not ordering. Tiers run in order
`pkg-manager` → `runtime-manager` → `app`, alphabetically within a tier. Homebrew
is `pkg-manager` and mise is `runtime-manager`, so homebrew's prerequisites
already run first *when both are in the run*. Declaring the dependency would
also be wrong on Debian, where homebrew is not in the run at all — the
resolution would be TOPIC_NOT_RUN and mise would fail.

So the fix is one of:

- **Extract the prerequisite** into a topic that both platforms can include, or
- **Duplicate a minimal probe** into mise's own prerequisites guarded by
  `os_family == 'Darwin'`, accepting the duplication, or
- **Make the missing compiler a diagnosed failure** — mise's prerequisites
  probes for `cc` on Darwin and fails with the `xcode-select --install` command
  and the attended-machine caveat, rather than letting a cargo build fail later.

The third is the smallest change that makes the failure honest. The first is the
correct one if a second topic ever needs a compiler.

### What must be settled before code

- Whether a macOS host is available to test on, and how. `AGENTS.md` §
  Verification forbids reporting work as verified on a platform it has not run
  on, and the Mac is not reachable from this session.
- Whether unattended `xcode-select` installation is possible at all. Candidates
  worth checking against Apple's documentation rather than assuming:
  `softwareupdate --install` for the CLT package, the `com.apple.dt.CommandLineTools` label
  pattern, and any `--agree-to-license` equivalent. Do not invent a flag.
  Xcode itself needs `xcodebuild -license accept`; CLT may not.
- What the probe costs. `xcode-select --print-path` succeeds when the path
  exists; a stronger check is compiling a trivial C file, because a broken or
  moved CLT still reports a path.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Establish from primary sources whether CLT can be installed without a human pressing a button; record the answer either way.
- [ ] #2 The task reports `changed` truthfully — no green run that installed nothing.
- [ ] #3 A machine without a compiler fails with an error that names Xcode CLT and the command to fix it, not the consumer that needed `cc`.
- [ ] #4 The fix works for `apps/mise` without declaring a Linux-unschedulable dependency.
- [ ] #5 Whatever runs on macOS is reported as unverified if no macOS host was available, with that stated in the PR.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
Layering: `apps/homebrew` owns Homebrew, `apps/mise` owns the runtime manager.
A prerequisite both need is a layering question, not a copy-paste question — see
`docs/TOPICS.md` and `AGENTS.md` § What this repo is for the one-concern-per-layer
rule.

Cross-platform rule from `AGENTS.md`: guard the package manager in-task rather
than abstracting it, and do not declare `homebrew` in `topic_requires` on a topic
that must run on Linux.

Existing behaviour to preserve: the `'already installed' not in
xcode_install.stderr` guard in `failed_when` handles the race where a second
invocation sees the install in progress. Any rewrite keeps that.
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->
