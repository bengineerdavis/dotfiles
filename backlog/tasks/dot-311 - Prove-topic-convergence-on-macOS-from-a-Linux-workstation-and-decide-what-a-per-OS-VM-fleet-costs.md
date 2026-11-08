---
id: DOT-311
title: Prove topic convergence on macOS from a Linux workstation, and decide what
  a per-OS VM fleet costs
status: To Do
created_date: 2026-11-08 20:27
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Approved plan 2026-11-08. The fleet is two machines — one Linux desktop (Pop!_OS, amd64, KVM) and one Apple Silicon Mac (arm64) — so every topic that declares `topic_os: [Darwin, Debian]` needs its converge path proven on both. Today only the Linux half is real: `limactl` 2.2.1 boots Debian 12 guests through the shared adapter at `home/dotfiles/apps/lima/molecule/shared/`, driven by `scripts/run-molecule.sh`.

The macOS half is the open question. Lima runs Linux guests on macOS, not macOS guests, so a macOS guest needs a different hypervisor — and for Apple Silicon that narrows to Virtualization.framework-based tools (UTM, Tart, Anka). DOT-76 already names the unknowns: which provider works on Apple Silicon, image size, and Apple's licensing limit of two macOS VMs per host.

Decided 2026-11-08: **Linux VM first.** Get the Debian scenario end-to-end for the topic under test, and defer the macOS guest question until the research below lands. Also deferred: CI-based macOS runners (`macos-14`/`macos-15`) — the GitHub Actions minutes budget for private repos is not settled, so CI is not a fallback we can count on yet.

Ruled out for now: a Linux VM seeded with the Mac's directory layout as a *substitute* for OS testing. The author's position is that one VM per target OS environment across the fleet is important, and a layout fixture tests data, not platform. It may still be the right check for a specific bug class (a committed config carrying one machine's paths) — that is DOT-306's problem, not this task's.

Research in flight: `docs/research/cross-os-vm-testing.md` surveys what actually runs a macOS guest, how Ansible/Molecule practitioners test macOS roles, what GitHub's macOS runners provide, and what comparable dotfiles repos do. Read it before choosing.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A Linux VM scenario for the gita topic converges, passes idempotence, and asserts registration — the definition of 'working' is a clean guest that runs chezmoi apply plus the dotfiles playbook and ends with gita ls listing repos and gita fetch succeeding
- [ ] #2 The macOS path has a recorded decision with its rejected alternatives, grounded in the research file rather than assumption
- [ ] #3 CI-based macOS runners are explicitly marked deferred with the reason (Actions minutes budget unsettled), not silently omitted
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
