---
id: TASK-243
title: Add a gateway service to apps/loreai (launchd + systemd user)
status: Done
created_date: 2026-10-27 22:13
labels:
- loreai
priority: high
updated_date: 2026-10-28 20:18
orchestration:
  status_key: inprogress
  version: 3
  lease_owner: opencode
  lease_expires_at: '2026-10-28T18:21:44.960513Z'
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
Merged 2026-10-28 by PR #88 (192fb98). Full merged-base suite: 1162 passed, 6 skipped, 8 deselected. macOS service/config apply was verified earlier; Debian Molecule evidence remains outstanding under the author's temporary exception recorded in DOT-254. The upstream OpenCode V1 plugin incompatibility remains in DOT-244 and BYK/loreai#2021.
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
<!-- RUN_HISTORY_ENTRY:BEGIN -->
```yaml
event_id: run-418b888324074b5eb86655f00aec4581
type: release_task
actor: opencode-loreai-service
timestamp: '2026-10-28T16:21:44.582160Z'
result: succeeded
task_id: TASK-243
from_status: inprogress
to_status: todo
```
Release stale claim after checking active claims; reclaim for the maintainer-requested OpenCode config deployment.
<!-- RUN_HISTORY_ENTRY:END -->
<!-- RUN_HISTORY_ENTRY:BEGIN -->
```yaml
event_id: run-286770b4630942689528f129cb4f9878
type: claim_task
actor: opencode
timestamp: '2026-10-28T16:21:44.960579Z'
result: succeeded
task_id: TASK-243
from_status: todo
to_status: inprogress
metadata:
  lease_ttl_seconds: '7200'
```
Apply only the captured OpenCode JSONC config from main, per maintainer instruction.
<!-- RUN_HISTORY_ENTRY:END -->
<!-- RUN_HISTORY_ENTRY:BEGIN -->
```yaml
event_id: run-4b115c031c374a3b807b33f31f3672ba
type: record_run
actor: opencode
timestamp: '2026-10-28T17:54:52.386000Z'
result: pr-updated
task_id: TASK-243
to_status: inprogress
metadata:
  state_update: '{"status_key":"inprogress"}'
```
PR #88 pushed at fc4eb57. Added isolated real OpenCode/Lore E2E, full setup parity, service-test refactor, and OpenCode package/config capture. Focused: 38 passed; isolated E2E passed; apply idempotent; doctor 6/6. Full suite: 1159 passed, 3 unrelated failures (DOT-258/DOT-259). Recovery import after the agent's unscoped Lore clear remains running; exact restoration is not claimed.
<!-- RUN_HISTORY_ENTRY:END -->
<!-- RUN_HISTORY_ENTRY:BEGIN -->
```yaml
event_id: run-d9494ff6882c48f09b513b261eab2432
type: record_run
actor: opencode
timestamp: '2026-10-28T20:18:48.249524Z'
result: merged
idempotency_key: loreai-gateway-service-merge-192fb98
task_id: TASK-243
verification:
- 'uv run --frozen pytest tests tools -q: 1162 passed, 6 skipped, 8 deselected'
```
PR #88 merged as 192fb98. Gateway service and chezmoi-owned OpenCode capture are on main.
<!-- RUN_HISTORY_ENTRY:END -->
<!-- SECTION:RUN_HISTORY:END -->
