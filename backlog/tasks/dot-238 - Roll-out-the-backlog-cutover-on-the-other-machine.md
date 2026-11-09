---
id: DOT-238
title: Roll out the backlog cutover on the other machine
status: Done
created_date: 2026-10-27 19:48
labels:
- cutover
priority: high
updated_date: 2026-11-09 15:58
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The Debian machine needs the full rollout from docs/BACKLOG-CUTOVER.md: pull main; apply apps/backlog (mise installs pipx:backlog-md-py, systemd user unit for the daemon — operator decides loginctl enable-linger); daemon smoke; chezmoi apply for the opencode MCP registration; codex/claude manual MCP steps; then convert any local branches per the cutover rules.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->

<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Pruned as a stale artifact (2026-11-09): the cutover rollout was completed on the other machine and absorbed into routine operation. No outstanding rollout work remains.
Pruned as a stale artifact (2026-11-09): the cutover rollout was completed on the other machine and absorbed into routine operation. No outstanding rollout work remains.
<!-- SECTION:FINAL_SUMMARY:END -->
## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->
