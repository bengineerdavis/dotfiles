---
id: DOT-254
title: Declare the Molecule Vagrant toolchain in mise and bootstrap
status: To Do
created_date: 2026-10-28 05:37
labels:
- testing
- mise
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The Molecule scenarios require Vagrant plus a working libvirt provider, but those dependencies are not declared through the repo's mise/bootstrap path. The Lore Debian scenario is syntax-checked but cannot run on this machine because Vagrant is absent.

Ship:

- Declare Vagrant and the required VM-provider packages in the repo's mise configuration and bootstrap flow, with per-OS handling.
- Document provider setup and any privileged host prerequisites separately from unprivileged mise tools.
- Prove the declared toolchain can create a Molecule VM and run the Lore Debian scenario.
- Record that macOS VM coverage needs a separate mechanism; do not treat Vagrant installation as macOS scenario support.

Constraints:

- Follow TOPIC-RECIPES.md tool-entry ownership and the cross-session lease for dotfiles/apps/mise/files/config.toml.
- Do not install Vagrant or system packages ad hoc while implementing the task; mise/Ansible owns the install.
- Do not change upstream repositories or the existing Vagrant/libvirt driver architecture without asking the maintainer.

Agreed with the maintainer 2026-10-27: Vagrant belongs in the project's declared bootstrap and package requirements.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The mise/bootstrap configuration declares Vagrant and the appropriate provider dependencies for each supported OS.
- [ ] #2 A fresh or isolated host reports a working vagrant --version and libvirt provider after the documented bootstrap.
- [ ] #3 MOLECULE_SCENARIO=debian scripts/run-molecule.sh loreai test completes on that host.
- [ ] #4 The docs distinguish unprivileged tools, privileged provider setup, and the separate macOS VM gap.
- [ ] #5 Any mise change is made under the covering orchestration lease and verified by git show --stat HEAD.
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
