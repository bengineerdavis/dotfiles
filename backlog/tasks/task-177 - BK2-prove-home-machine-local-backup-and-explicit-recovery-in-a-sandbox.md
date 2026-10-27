---
id: TASK-177
title: BK2 — prove home-machine local backup and explicit recovery in a sandbox
status: To Do
created_date: 2026-10-27 02:58
labels:
- planned
- group:gita-and-machine-file-backup-approved-2026-09-23
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**BK2 — prove home-machine local backup and explicit recovery in a sandbox.**
  After G2, implement BK1's borg 1.4.x/borgmatic design with a local repo,
  timer, runtime keyring passphrase, capture allowlist, staleness warning,
  monthly `borgmatic extract` test restore and restore runbook. Use synthetic
  machine files until the full BK2–BK4 real-data gate passes. Owner and
  bounded retention are fixed before any archive exists; never prune the
  newest archive. Keep one repository per machine per destination.
  Capture an explicit path allowlist starting with
  `~/.local/state/machine/`, never "home minus excludes". The home capture
  contains `machine.yaml` and `private.yaml`; work-derived configuration
  belongs only in work 1Password, machine-written records are rebuilt, and
  customer data is never on the list. Apply the agent-read denial for the
  backup store, matching the machine-state denial in G2; this is a
  policy-path change needing PR review.
  Missing or empty source files mean no archive is created and nothing is
  pruned: deletion must not become a version or rotate out good copies.
  Verify the handoff's proposed borgmatic `before_backup` exit-75 soft
  failure actually skips both create and prune; that mechanism is unproven,
  and a failure of the claim requires another guard, not weaker behaviour.
  Never restore automatically: report the latest archive and exact restore
  command. Test that a run never restores automatically and an explicit
  restore works. Test fresh silence versus the accepted 12-hour stale
  warning, and that a planted customer-data path never reaches an archive
  while listed paths always do. The allowlist and missing-source guards
  must both decline when required and proceed when permitted.
  The handoff's Linux evidence on 2026-09-23 was systemd 249 without
  `systemd-creds`, with `secret-tool` present and linger off. Use GNOME
  keyring for scheduled passphrases; logged-in runs are expected to find it
  unlocked, but prove that with an actual timer run. On lookup failure,
  report the problem and let the staleness warning fire.
  Done when sandbox deletion makes the next run skip both archive creation
  and pruning, an explicitly requested restore brings the files back, and
  each rule above has a test seen to fail when deliberately broken,
  including the customer-data test in both directions. Record the timer
  evidence and runbook; BK3 follows with independent off-machine recovery.
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
