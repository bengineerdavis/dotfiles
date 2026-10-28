---
id: DOT-261
title: Move Vagrant installation into a user-space topic
status: To Do
created_date: 2026-10-28 23:05
labels:
- testing
- mise
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Move the Molecule Vagrant installation from host-level bootstrap into a topic that installs and maintains Vagrant in user space. Keep this separate from DOT-254 immediate package bootstrap and DOT-255 cross-host VM matrix.

The current official macOS package requires sudo and writes /opt/vagrant plus /usr/local/bin/vagrant. Raw relocation was measured to leave bundled helpers pointing at /opt/vagrant, so do not merely copy the DMG payload and call it working. Evaluate a genuinely supported user-space install path, including installer options or another maintained upstream distribution channel; do not silently patch upstream binaries or build a bespoke installer in this dotfiles repo. If no trustworthy user-space path exists, record the upstream constraint and keep the narrowly privileged package-owned installation.

Requirements:
- Per-machine opt-in; do not install Vagrant on every machine.
- Topic owns user-space Vagrant, its user plugins, and working-condition checks, while chezmoi owns configuration files and Ansible owns any genuinely privileged host state.
- Support vagrant-qemu on macOS and vagrant-libvirt on Linux without creating competing install channels.
- Declare and verify the provider and architecture rather than accepting a Vagrant receipt as proof.
- Removal is opt-in and distinguishes topic-owned state from pre-existing packages, other projects, shared Vagrant boxes, and user VM data. Never use blanket package-manager autoremove or prune.
- Update DOT-254 and MOLECULE-HOSTS.md when the ownership moves.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The topic has an explicit supported user-space installation path, or records an upstream blocker and retains a narrowly privileged fallback.
- [ ] #2 A fresh opt-in machine passes vagrant --version and the correct provider-plugin checks without root-owned user state.
- [ ] #3 The existing Molecule scenarios use the topic-managed Vagrant on both supported host paths.
- [ ] #4 Topic removal is idempotent and preserves shared/pre-existing packages, boxes, and user VM data unless separately approved.
- [ ] #5 Documentation names the per-machine selection, installation owner, privileged fallback, and opt-in teardown.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
Requested by the author 2026-10-28 during DOT-254 review. The measured raw relocation failure is evidence against treating a relocated DMG as a supported rootless installation. Follow TOPIC-RECIPES.md ownership and the build-ladder before writing a new installer.
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->
