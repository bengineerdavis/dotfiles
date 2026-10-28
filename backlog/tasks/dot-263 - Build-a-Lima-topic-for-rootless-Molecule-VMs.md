---
id: DOT-263
title: Build a Lima topic for rootless Molecule VMs
status: To Do
created_date: 2026-10-28 23:56
labels:
- testing
- molecule
- chore
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add an apps/lima topic that provides rootless Lima/QEMU VM support for Molecule on macOS and Linux, using prebuilt upstream binaries and the existing Molecule Lima adapter where it meets the repo contract. This is the author-selected alternative to the Vagrant/macOS cask path; keep it separate from the broader DOT-255 matrix and DOT-261 user-space Vagrant research.

Measured 2026-10-28: Lima 2.2.1 Darwin-arm64 tarball extracted into ~/.local with its GitHub release SHA256 verified. Existing user-owned QEMU 11.1.2 advertises hvf. A Debian 12 ARM64 guest booted with vmType=qemu, HVF, user-mode networking and no mounts; SSH, systemd, user manager, and systemd-detect-virt=qemu all passed. No sudo, Vagrant, or system package installation was needed. The guest must be destroyed after the probe.

Requirements:
- Topic owns Lima installation and its lifecycle, while chezmoi owns configuration and Ansible owns any separately approved privileged host state. Do not use sudo for Lima itself.
- Resolve Lima and QEMU release assets and checksums per host OS/architecture; support macOS and Linux without machine-specific literals.
- Prefer the existing molecule-lima adapter over new delegated lifecycle code, but audit its current behavior against Molecule 26 and the repo seams before adopting it. It currently has open questions around instance_config, usernames, default vm_type, mounts, and destroy failure handling.
- Use vmType=qemu for host parity; HVF on macOS and KVM on Linux are explicit capabilities. Do not call a container run a VM pass or imply macOS guest support on Linux.
- Share per-topic converge/idempotence/verify behavior and provide clean destroy, with no deletion of pre-existing Rancher Desktop or other Lima instances.
- Per-machine opt-in, documentation, changelog, tests, and opt-in removal of only topic-owned state. Preserve shared Lima/QEMU packages and user VM data unless separately approved.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The topic installs Lima rootlessly from verified prebuilt assets and reports working limactl/QEMU capabilities on supported hosts.
- [ ] #2 A real Linux VM passes the approved Molecule lifecycle seam through Lima, with SSH, guest OS/architecture, systemd, and teardown verified.
- [ ] #3 The topic reuses the existing Lima adapter or records why it is unfit; no duplicate lifecycle framework is added without author approval.
- [ ] #4 The scenario uses the same topic behavior on macOS and Linux, reports provider/architecture results explicitly, and preserves unsupported macOS-on-Linux coverage as open.
- [ ] #5 Topic removal is idempotent and does not delete pre-existing Lima instances, Rancher Desktop state, shared QEMU, or user VM data.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
Requested by the author 2026-10-28 as a chore after the Lima rootless handoff. Existing adapter: github.com/filatof/molecule-lima, MIT, latest source inspected 2025-11-16. Evaluate it before implementation. Related DOT-254, DOT-255, DOT-261, DOT-262.
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->
