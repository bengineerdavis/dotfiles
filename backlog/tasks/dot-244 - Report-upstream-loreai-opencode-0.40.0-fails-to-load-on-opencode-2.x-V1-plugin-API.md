---
id: DOT-244
title: 'Report upstream: @loreai/opencode 0.40.0 fails to load on opencode 2.x (V1
  plugin API)'
status: To Do
created_date: 2026-10-27 22:13
labels:
- loreai
- upstream
priority: high
updated_date: 2026-10-27 22:22
orchestration:
  status_key: todo
  version: 1
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Verified on this machine 2026-10-27 (opencode v2.1.2): the plugin fails schema validation - 'Plugin must export a default definition with an id and an effect or setup function (SchemaError: Expected object at [default])'. The plugin's default export is the V1-style async function (LorePlugin). opencode V2 requires Plugin.define({id, setup(ctx)}) and the V1 hook-return style never executes ('V1 plugin implementations do not run in V2' - opencode.ai/v2/docs/build/plugins/migrate-v1). Effect: opencode sessions never route through the gateway, auto-compaction is never disabled, and no .lore.md is ever generated. File an issue at BYK/loreai requesting a V2 port (or dual server/setup export per the migration guide's compatibility section).
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
event_id: run-9d2eb7dc3cd34c9790281a616d96bbe9
type: claim_task
actor: opencode-coordinator
timestamp: '2026-11-01T16:32:25.447789Z'
result: succeeded
task_id: DOT-244
from_status: todo
to_status: inprogress
metadata:
  lease_ttl_seconds: '3600'
```
<!-- RUN_HISTORY_ENTRY:END -->
<!-- SECTION:RUN_HISTORY:END -->

Recovery reconciliation 2026-11-04: removed the expired lease. No upstream report was filed by that claim; reporting remains separate from the V2 port and resilience investigation.
