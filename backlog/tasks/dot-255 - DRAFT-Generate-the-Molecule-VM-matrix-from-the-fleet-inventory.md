---
id: DOT-255
title: 'DRAFT: Generate the Molecule VM matrix from the fleet inventory'
status: To Do
created_date: 2026-10-28 16:05
labels:
- testing
- molecule
- design
priority: medium
updated_date: 2026-10-28 23:35
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Extend the Molecule harness so its VM selection follows the machines this dotfiles repo supports, rather than requiring a hand-added scenario for every new host or OS upgrade.

The approved harness keeps topic scenarios under apps/<topic>/molecule/ and uses Molecule's native scenario orchestration (DOT-76, DOT-101). This task should build on that design and DOT-254's declared Vagrant/provider prerequisites, not invent a second harness.

Design the inventory-to-matrix path:

- Identify the authoritative machine/OS inventory and how each entry maps to a VM image, architecture, provider, and supported topics.
- Generate or select Molecule scenarios from that inventory for the requested topics, without changing the topic lifecycle or duplicating scenario logic per VM.
- Add newly supported machines and OS upgrades as inventory changes, with explicit overrides for exceptions and unsupported VM/provider combinations.
- Keep local developer runs bounded: default to a documented useful subset, with an explicit all-fleet mode for CI or maintainer runs.
- Keep macOS coverage distinct from Linux Vagrant/libvirt coverage; a machine inventory entry must not silently imply a working macOS VM provider.
- Make destroy/prune behavior and VM resource budgets explicit for a matrix that can grow.

This is a draft for design review, not authorization to implement. The PRD/roadmap and the existing harness decisions should be revisited before claiming it for execution.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The design names the authoritative machine inventory and defines deterministic inventory-to-VM/topic matrix selection.
- [ ] #2 Adding a machine or changing an OS release changes the selected VM coverage through inventory data, with tests for both cases.
- [ ] #3 Unsupported provider/OS combinations fail visibly or are explicitly excluded; no green run is reported for skipped platform coverage.
- [ ] #4 The design preserves per-topic Molecule scenarios and supports bounded local runs plus an explicit full-fleet run.
- [ ] #5 Resource, teardown, and CI behavior are specified before implementation tasks are created.
- [ ] #6 DOT-254 and the existing molecule harness decisions are reconciled rather than duplicated.
- [ ] #7 VM lifecycle seam: Molecule/provider evidence proves the requested guest OS, architecture, real VM lifecycle, and required systemd behavior; container or mocked substitutes cannot count.
- [ ] #8 Shared topic seam: identical per-topic converge/idempotence scenarios run across supported guests and assert second-run stability without provider-specific copies.
- [ ] #9 Integration seam: real guest chezmoi apply, service-manager state, gateway health/lore doctor, and OpenCode behavior are verified externally; credentialed model tests remain explicitly opt-in.
- [ ] #10 Coverage seam: a public report records every requested host/guest/architecture/provider result and fails closed on unreported or unsupported coverage; skipped platforms are not passes.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
2026-10-28 maintainer requirement: normalize Molecule tests so either fleet machine can validate both supported guest platforms locally, catching cross-OS breakage before PRs. Research correction: libvirt DOES support a local QEMU server on macOS (official libvirt docs), including hvf acceleration via Hypervisor.framework since libvirt 8.1; earlier blanket 'libvirt is Linux-only' guidance was wrong. Vagrant/libvirt is therefore a candidate common adapter for Linux guests on both hosts, not yet a proven one. Must verify Debian ARM64 box selection, HVF domain creation, Vagrant management networking/SSH, synced repo, teardown, and host-side effects before adopting. A green container run must not count as VM/service proof. Separate host hypervisor adapters from the shared per-topic Ansible scenario interface; do not build a universal Vagrant abstraction that hides unsupported guest/provider pairs. macOS guests on a Linux host remain an explicit open capability, not implied by libvirt's macOS-host support. Proposed verification seams for maintainer confirmation: (1) Molecule create/destroy + provider VM state: proves actual VM lifecycle, catches silent container substitution; (2) shared topic converge/idempotence: proves same role behavior on each guest; (3) externally observable service/health and real chezmoi/OpenCode behavior: catches config and service lifecycle breakage; (4) matrix host/guest/arch/provider result report: proves requested platform coverage and fails closed on unsupported pairs. DOT-254 must expand from 'Vagrant/libvirt installed on Linux' to a measured provider capability matrix, or be superseded by a reconciled task; do not let its current Linux-only acceptance criteria imply full fleet coverage.
2026-10-28 maintainer-approved test-design seams. These are public verification interfaces, not implementation instructions. (1) VM lifecycle: through Molecule create/destroy and the provider's VM state, assert the guest is a real VM with the requested OS/architecture and usable systemd where required; catches container substitution and lifecycle/teardown failures, but does not prove topic behavior. (2) Shared topic behavior: through the same per-topic converge/idempotence scenarios on each guest, assert role behavior and second-run stability; catches OS-specific provisioning regressions, but does not prove persistent services or real deployed configuration. (3) Externally observable integration: through real guest chezmoi apply, the actual service manager, gateway health/lore doctor, and OpenCode config/recording interfaces, assert the deployed behavior; catches deployment/service/config failures, but real-model E2E requires explicit credentials and remains opt-in. (4) Coverage reporting: through the matrix's public result report, record each requested host/guest/architecture/provider combination as passed, failed, or explicitly unsupported; catches silent platform-coverage loss. A skipped or unavailable platform must never count as a pass. Tests should observe external behavior, not reimplement provider logic or inspect private implementation state. First vertical slice is one Debian ARM64 VM lifecycle proof on the Mac, then one shared Lore scenario; do not bulk-write a provider matrix before that evidence exists. macOS-on-Linux remains an explicit open capability, not an assumed libvirt feature.
2026-10-28 measured Mac lifecycle evidence (host macOS 26.6.2/arm64): Homebrew QEMU 11.1.2 + libvirt 12.8.0; Vagrant 2.4.9 relocated rootlessly into ~/Applications/vagrant (HashiCorp SHA256 verified), vagrant-libvirt 0.12.2 user-local. virsh qemu:///session advertises aarch64 hvf. Direct QEMU with -machine virt,accel=hvf booted cloud-image/debian-12 20260923.2610.0 (libvirt/arm64 box) from a disposable qcow2 overlay; SSH over QEMU hostfwd proved ID=debian VERSION_ID=12, uname=aarch64, PID1=systemd, systemctl --user=running, systemd-detect-virt=qemu. Guest was destroyed. This proves the Mac can provide a real Debian ARM64 VM rootlessly; it is NOT a Molecule/Vagrant pass. Vagrant/libvirt 0.12.2 failed before VM creation: forwarded_port triggers a Ruby TypeError in config validation; management-network mode requires Linux 'ip' and fails on macOS even with NFS disabled. Do not shim 'ip' or patch Vagrant locally; keep Vagrant/libvirt marked unsupported on macOS until upstream adapter compatibility is proven. Next candidate adapter is vagrant-qemu using the same box's qemu/arm64 artifact, evaluated through Molecule's create/SSH/destroy seam; no custom Molecule lifecycle module without first exhausting the existing provider. Direct libvirt XML created an hvf domain, but default ARM64 serial did not produce a login console; direct QEMU with PL011 serial is the working baseline. No sudo, brew services, dnsmasq, or VM autostart used. Added host state: qemu/libvirt and their new brew dependencies (plus routine brew upgrades), user-local Vagrant/plugin, scratch VM/key artifacts. Teardown must ask before removing brew packages because pre-existing projects may share them; no blanket brew autoremove. Mise guidance: use [bootstrap.packages] for qemu/libvirt; do not run sudo mise. Vagrant's macOS pkg/cask is not rootless, so keep the verified user relocation or defer to Ansible/package ownership; privileged Linux daemon/group/network state belongs in Ansible, not mise tools.
2026-10-28 correction to the relocation plan: unpacking the signed Vagrant DMG into ~/Applications/vagrant did NOT produce a self-contained install. Its bundled curl and bsdtar still reference /opt/vagrant/embedded/lib; the successful probe needed user-local wrappers to /usr/bin/curl and /usr/bin/tar. Therefore raw relocation is not a supported general bootstrap path and the wrappers must not be generalized as one. Durable choice: find a supported rootless package channel (for example a verified Nix/mise registry package), or keep the official /opt/vagrant installation as an explicitly privileged Ansible-owned step while QEMU and the VM lifecycle remain user-owned. No claim that mere extraction elsewhere is sufficient.
2026-10-28 maintainer requirement: allow selected Molecule guest scenarios to run in parallel, initially multiple Linux guests and later macOS guests where a supported provider exists. Parallelism is an execution choice, not permission to hide coverage: publish one result per host/guest/architecture/provider and fail the requested run when any required result is failed, missing, or unsupported. Set an explicit VM concurrency/resource budget per machine; reuse compatible immutable box images without sharing mutable VM disks, state directories, Vagrant project names, forwarded ports, or Ansible ephemeral state. A failed scenario must tear down its own VM without destroying another scenario or live host state. Keep a serial fallback for debugging and for shared privileged providers that cannot safely run concurrently. The first vertical slice remains one passing Debian guest on macOS through the declared bootstrap; do not claim a full matrix before that prerequisite and real host coverage exist.
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->
