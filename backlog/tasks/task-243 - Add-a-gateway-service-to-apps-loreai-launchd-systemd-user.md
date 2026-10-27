---
id: TASK-243
title: Add a gateway service to apps/loreai (launchd + systemd user)
status: To Do
created_date: 2026-10-27 22:13
labels:
- loreai
priority: high
updated_date: 2026-10-27 22:13
orchestration:
  status_key: inprogress
  lease_owner: opencode-loreai-service
  lease_expires_at: '2026-10-27T23:18:44.677470Z'
  version: 1
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

## Run History
<!-- SECTION:RUN_HISTORY:BEGIN -->
<!-- RUN_HISTORY_ENTRY:BEGIN -->
```yaml
event_id: run-9e9c8aaccef544b4a2f28d235f2e90e7
type: claim_task
actor: opencode-loreai-service
timestamp: '2026-10-27T22:18:44.677544Z'
result: succeeded
task_id: TASK-243
from_status: todo
to_status: inprogress
metadata:
  lease_ttl_seconds: '3600'
```
<!-- RUN_HISTORY_ENTRY:END -->
<!-- RUN_HISTORY_ENTRY:BEGIN -->
```yaml
event_id: run-934993b9a86b408aa5188aeee81c71a0
type: record_run
actor: opencode-loreai-service
timestamp: '2026-10-27T22:30:37.815546Z'
result: pr-opened
task_id: TASK-243
```
Gateway service implemented and verified on macOS. PR #88 open for review (service-lifecycle path, per merge gates). launchd agent ai.withlore.gateway live: doctor 5/5 PASS, adoption of hand-started gateway confirmed, respawn after lore stop confirmed, second apply idempotent. Debian unit renders verified, not applied there. remove.yaml teardown updated (service stop, units, logs, bg gateway).
<!-- RUN_HISTORY_ENTRY:END -->
<!-- SECTION:RUN_HISTORY:END -->
