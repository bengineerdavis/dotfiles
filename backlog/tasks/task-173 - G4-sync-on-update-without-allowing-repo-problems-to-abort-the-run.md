---
id: TASK-173
title: G4 — sync on update without allowing repo problems to abort the run
status: To Do
created_date: 2026-10-27 02:58
labels:
- planned
- group:gita-and-machine-file-backup-approved-2026-09-23
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**G4 — sync on update without allowing repo problems to abort the run.**
  After G3, implement sync on `--tags upgrade`, using G1's decision about
  calling gita or git. Fetch every repo, including dirty ones: fetch never
  touches the working tree. Then fast-forward only clean repos with
  `git merge --ff-only`. Report per-repo verdicts: fast-forwarded; skipped
  for dirty state, conflicts, detached HEAD, no upstream or a mid-operation
  state; or failed fetch. Failed fetch means UNKNOWN, never "up to date".
  Repo problems are reported and the run exits 0. Only the topic's own
  checks fail the run, such as a missing provider or malformed catalogue or
  machine file. Record the deviation from `TOPIC-RECIPES.md`'s "fail once
  at the end" in the topic README: the parent playbook's topic loop has no
  rescue, so raising here skips later app topics.
  Each run writes separate machine-written records of per-repo last-fetch
  and blocked-since timestamps, feeding reports and G5's warning. Preserve
  the stored last-good-run timestamp needed by that warning; an exit-0
  report of repo problems is not evidence that a failed fetch succeeded.
  Done when a planted dirty repo is fetched, skipped and reported while a
  clean repo fast-forwards, and a failed fetch cannot pass as "up to date",
  proven by deliberate mutation. This hands the sync path and timestamps
  to G5; G4, G5 and G7 run serially on the shared upgrade path.
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
