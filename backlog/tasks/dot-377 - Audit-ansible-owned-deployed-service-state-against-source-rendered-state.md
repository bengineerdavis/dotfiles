---
id: DOT-377
title: Audit ansible-owned deployed service state against source-rendered state
status: To Do
created_date: 2026-11-18 03:13
updated_date: 2026-11-18 03:14
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->

<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
Why: 2026-11-18 retro finding. Today's chezmoi apply fixed every chezmoi-owned file while the ansible-owned backlog plist stayed stale (argv lost the daemon subcommand; crash-looping, 801KB help-text log) — by design invisible to every gate, because the suite tests source, and the plist is written by topic runs, not chezmoi. Ship: a periodic (not per-commit) audit that renders ansible-owned deployed service state (launchd plists, systemd units) from current source and compares against deployed; drift = a warning naming topic + file. Constraints: design decision open — where it runs (topic-run post-task? update.sh step? scheduled?) and that it must never restart a service (DOT-343 principle). Cite the incident: com.backlog-py.daemon 2026-11-17 17:04.
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->
