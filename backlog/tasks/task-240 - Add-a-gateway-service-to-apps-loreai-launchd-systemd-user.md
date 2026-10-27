---
id: TASK-240
title: Add a gateway service to apps/loreai (launchd + systemd user)
status: To Do
created_date: 2026-10-27 22:13
labels:
- loreai
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Root-cause followup from the .lore.md investigation (2026-10-27): the topic persistently routes claude-code and codex at 127.0.0.1:3207 but installs nothing to keep the gateway alive, so routing silently breaks on every reboot/logout (gateway was dead 2026-10-23..27). Lore's docs: 'leave the gateway running via lore start (or a system service)' and 'run the gateway under a system service manager (systemd, launchd, etc.)'. Add a per-user service to the topic (launchd agent on Darwin, systemd user unit on Debian - mirror the apps/backlog pattern), sourcing ~/.config/loreai/env.zsh for LORE_WORKER_MODEL/key env, and update tasks/remove.yaml to tear it down. Service must land on port 3207 (claude/codex configs point there explicitly).
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
