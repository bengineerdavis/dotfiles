---
id: DOT-278
title: Reduce routine Ansible upgrade output without hiding failures
status: To Do
created_date: 2026-10-30 06:25
labels:
- ansible
- ux
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Author request from the 2026-10-29 ./update.sh transcript: routine dependency-resolution probes and successful tasks produce thousands of lines, including nested command result dictionaries, while actual failures are difficult to find. Configure the existing Ansible output seam so routine upgrades show concise progress and changed results, preserve full actionable error details on failure, and render multiline strings readably. Prefer built-in callback/display settings over building a custom output tool. The existing draft-12 reuse-design task remains separate; this is the user-visible output behavior. Verification uses a synthetic play that includes successful loops, skipped tasks, changed results, and a failing task; no real-host playbook or chezmoi apply.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Routine successful dependency probes do not print their full registered result dictionaries
- [ ] #2 Skipped and successful hosts are concise by default, with an explicit verbose override available
- [ ] #3 Failures and multiline warnings remain readable and retain the information needed to act
- [ ] #4 Tests prove the old verbose output is reduced without suppressing failure diagnostics; focused and full suites pass
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
