---
id: TASK-178
title: BK3 — prove lost-home-machine recovery from the independent borg host
status: To Do
created_date: 2026-10-27 02:58
labels:
- planned
- group:gita-and-machine-file-backup-approved-2026-09-23
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**BK3 — prove lost-home-machine recovery from the independent borg host.**
  After BK2, add BK1's append-only SSH host repository, separate from the
  local repository and unique to this machine and destination. Write it
  with its own `borg create`; never sync/copy the live local repo to make
  the host copy. Append-only access prevents a buggy or compromised client
  from deleting past backups. Occasional prune/compact needs a separate
  delete-capable key and must preserve the newest archive under BK1's
  bounded retention. Carry BK2's allowlist, missing/empty-source guard and
  agent-read denial to the backup store; records and customer data remain
  excluded, and work-derived configuration stays only in work 1Password.
  Put independent exported borg keys and passphrases in Bitwarden as the
  recovery copy, not solely in the scheduled runtime keyring. Write the
  recovery runbook: sign in to Bitwarden from a clean device, using an
  offline 2FA recovery code if the phone was lost with the machine; fetch
  the key and passphrase; run `borgmatic config bootstrap`; extract; verify;
  then start a new repository for future backups. Do not resume writing
  the old repository from the fresh client: that risks counter reuse.
  Recovery remains explicit, never automatic; report the latest archive
  and exact command. Done when an empty-HOME drill with only Bitwarden and
  host access recovers the synthetic machine files and starts a new repo
  afterwards, with the runbook and independent key copy verified. Keep
  actual recovery material out of committed documentation. BK4 follows;
  real machine-file data still waits for that final restore drill.
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
