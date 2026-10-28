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
updated_date: 2026-10-28 20:48
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
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->
