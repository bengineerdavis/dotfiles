---
id: TASK-179
title: BK4 — prove work-Mac machine-file recovery using work 1Password only
status: To Do
created_date: 2026-10-27 02:58
labels:
- planned
- group:gita-and-machine-file-backup-approved-2026-09-23
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**BK4 — prove work-Mac machine-file recovery using work 1Password only.**
  After BK3, work in a session on the Mac. Keep that machine's files in
  work 1Password, with save-on-change during runs the user starts and a
  stale-copy warning. A 1Password service account is an option only if
  BK1 confirms the org permits it. Verify actual 1Password unlock/save
  behaviour on that machine; the handoff has not checked it.
  No borg runs on the work Mac, and no personal backup tool runs on or
  uploads from the company-managed device. Work-derived configuration,
  including `work.yaml`, lives only in the work secrets manager. Customer
  data never enters the capture list or leaves the Mac; its backup belongs
  to the employer. Machine-written state is rebuilt, never backed up.
  Restore machine files explicitly from work 1Password; work-repo recovery
  through discovery is G7's later work. Carry the agent-read denial for machine
  files and the backup store, and BK1's ownership/retention contract.
  Done when save-on-change, stale-copy warning and the restore drill pass
  on the Mac using synthetic files. Only then is the shared real-data gate
  satisfied: seed Linux after its inventory and the Mac in its own session,
  then proceed to G3 in the binding order.
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
