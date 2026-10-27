---
id: TASK-241
title: 'Report upstream: @loreai/opencode 0.40.0 fails to load on opencode 2.x (V1
  plugin API)'
status: To Do
created_date: 2026-10-27 22:13
labels:
- loreai
- upstream
priority: high
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
