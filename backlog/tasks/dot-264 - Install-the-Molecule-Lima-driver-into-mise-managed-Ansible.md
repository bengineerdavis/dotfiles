---
id: DOT-264
title: Install the Molecule Lima driver into mise-managed Ansible
status: To Do
created_date: 2026-10-29 00:26
labels:
- testing
- molecule
- mise
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add molecule-lima as an injected uv dependency of the pipx:ansible entry in dotfiles/apps/mise/files/config.toml, using the existing uvx_args --with mechanism. Keep Molecule/driver entry points available in the single Ansible tool venv; do not create a second Ansible or driver install channel. This is the author-requested follow-up from DOT-263 and does not change the rootless delegated scenario currently in progress.

Measured 2026-10-28: molecule-lima 0.0.3 was loadable under the locked test-vm environment when supplied via uv --with, but its own rootless scenario failed because its create playbook requires socket_vmnet networking and mounts. Installation must not imply this adapter has passed the rootless contract. Retain the current delegated Lima scenario until the driver meets it.

Acceptance:
- pipx:ansible uvx_args includes --with molecule-lima and preserves ansible-core/CLI exposure.
- The config parse and a focused test prove the dependency remains declared; prove the test fails against a missing-driver mutation.
- Existing drift guards prevent the dependency disappearing silently when mise sees an already-installed Ansible version. Reuse the llm plugin verification/rebuild pattern rather than assume editing uvx_args updates the venv.
- No live mise install, chezmoi apply, or replacement of the delegated scenario without separate authorization.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The mise Ansible uv installer declares molecule-lima in its existing tool venv, with no second Ansible channel.
- [ ] #2 A focused test verifies declaration and drift handling and has mutation evidence.
- [ ] #3 The rootless delegated scenario remains intact and the unmet molecule-lima adapter limitations are documented.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
Author requested twice during DOT-263 on 2026-10-28, explicitly asking to remember it without interrupting the current process. Recorded as a separate work item because it touches the shared mise catalogue and Ansible lifecycle.
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->
