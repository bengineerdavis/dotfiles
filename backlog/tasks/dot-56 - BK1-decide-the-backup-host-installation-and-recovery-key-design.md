---
id: DOT-56
title: BK1 — decide the backup host, installation and recovery-key design
status: To Do
created_date: 2026-10-27 02:55
labels:
- now
priority: high
updated_date: 2026-10-27 22:21
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**BK1 — decide the backup host, installation and recovery-key design.**
  After G0, alongside G1 and the second-machine inventory, research an
  append-only borg host over SSH, borg/borgmatic installation on both OSes,
  and the support grade of available Galaxy roles. Borg 1.4.x with
  borgmatic is already chosen: pin 1.4.x, not borg 2 beta. The handoff's
  upstream check on 2026-09-23 found stable borg 1.4.5, released 2026-07-18,
  and borg 2 beta's warning against production backup repositories. A
  commented `pipx:borgbackup` entry and stale inactive borg shim do not
  establish an installation owner; the installation mechanism is this item.
  Carry the borg FAQ rules checked that day: one repository per machine
  per destination; redundancy is a second independent repository with its
  own `borg create`, never copying/syncing a live repository or putting it
  in a cloud-sync folder. Using a repository and its copy risks data loss
  and AES-counter reuse. After machine loss, restore from the old repo,
  then start a new one for future backups. The host copy is append-only;
  occasional prune/compact uses a separate key with delete rights.
  Keep an independent `borg key export` recovery copy and passphrases in
  the secrets manager: Bitwarden for personal machines, 1Password for work.
  Scheduled runtime passphrases come from the OS keychain: macOS Keychain
  or GNOME keyring via `secret-tool` on the home Linux target, not its
  unavailable `systemd-creds`. Borgmatic supplies config-driven repositories,
  retention/checks and `config bootstrap` recovery. The handoff records
  once-per-run `encryption_passcommand` in 1.9.9+, external credentials
  including 1Password CLI/systemd credentials in 1.9.10+, and no built-in
  Bitwarden hook; a passcommand works while that vault is unlocked.
  Set owner = the backup topic and choose bounded retention that keeps the
  newest archive and never prunes it, before any archive exists. Live
  machine-file retention remains until the machine is decommissioned.
  Decide key organisation in Bitwarden and check whether the work org
  permits a 1Password service account. The work Mac uses work 1Password
  only, with no borg; the both-OS installation research does not override
  that rule. Done when the design, evidence and author's decisions are
  recorded. G2 receives the ownership/retention contract; BK2–BK4 receive
  the chosen host, install and credential design.
  Research report prepared at
  `dotfiles/docs/research/backup-host-selection.md`; no target
  install, account or backup was exercised. Awaiting author decisions on the
  remote host, retention/cadence, recovery-key access and whether a personal
  macOS install path is needed; work 1Password automation remains subject to
  work-owner approval. Spending ceiling: recommend on merits; no purchase
  authorized. [agent: gita-plan / OpenCode]
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
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
