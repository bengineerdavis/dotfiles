---
id: DOT-174
title: G5 — schedule sync and warn only when stored state is stale or blocked
status: To Do
created_date: 2026-10-27 02:58
labels:
- planned
- group:gita-and-machine-file-backup-approved-2026-09-23
updated_date: 2026-10-27 22:22
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**G5 — schedule sync and warn only when stored state is stale or blocked.**
  After G4, add a systemd user timer on Linux with `Persistent=true` for
  catch-up, and a launchd agent on macOS. Default to three runs a day,
  every eight hours, overridable per machine. Use the ollama timer/plist
  templates as precedent. The unit invokes
  `~/dotfiles/run-role.sh gita upgrade`; its playbook lookup is CWD-relative,
  so set `WorkingDirectory` to the resolved `~/dotfiles` directory, or the
  launchd equivalent, and supply the absolute resolved `~/.local/bin/mise`
  path because a service PATH will not contain it. Resolve target paths at
  deploy time. Timer-triggered discovery is report-only (G7), with no
  surprise discovered clones.
  Add the warning as topic shell wiring under `files/zsh/*.zsh`. It reads
  stored timestamps only: no git, network or `stat`. Print one line when
  the last good run is older than 12 hours, any repo has not fetched in
  12 hours, or a repo has been blocked longer than 12 hours; otherwise be
  silent. On Linux, report `loginctl enable-linger` as the fix for running
  while logged out; never enable it silently.
  At G5's start, confirm the author's distinction between classifying a
  new clone from gh metadata and forbidden self-healing relocation under
  `docs/LAYOUT.md`. The handoff places that confirmation here; G7 consumes it.
  Done when units pass their validators, the warning fires at 13 hours and
  stays silent at one hour with both directions mutation-proven, and
  removal leaves none of the scheduling or warning wiring behind. Verify
  Mac runtime behaviour in a Mac session. G7 follows this item serially.
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
