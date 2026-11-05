---
id: DOT-287
title: Make Lore plugin state truthful in OpenCode and the loreai topic
status: To Do
created_date: 2026-10-30 15:05
labels:
- loreai
- opencode
priority: high
updated_date: 2026-11-01 16:49
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Author report 2026-10-30: the OpenCode UI no longer shows Lore as a plugin even after running the loreai role. Read-only live verification: opencode api get /api/plugin returned data=[]; both deployed opencode configs had zero @loreai/opencode entries; npm had @loreai/opencode@0.40.0 installed. Gateway health was ok but the exact current session was not found in a project-scoped session listing. The current role comments delegate registration to chezmoi and only warn when the plugin is absent, so a green role is not proof that Lore runs. Earlier logs also show OpenCode v2 rejecting 0.40.0 as an old function-shaped plugin export. Restore a supported V2-compatible registration/loading path if available, or make the unavailability explicit and fail closed rather than describing the gateway route as plugin success. Do not enable the known-incompatible package or change live config without review. Preserve recording-route checks separately from plugin-load checks and never use memory knowledge updates as evidence of recording.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The public topic result distinguishes installed, registered, active/failed/unknown plugin state and cannot claim success when the plugin API has no active row
- [ ] #2 A healthy gateway is not treated as proof that the current session is recorded; session verification is separate and truthful about attribution/limits
- [ ] #3 The supported V2 plugin path is established from upstream evidence or its absence is reported as an explicit blocked state with the upstream reference
- [ ] #4 Synthetic tests cover absent registration, failed loading, active loading, and unavailable API, with mutation evidence; no live service restart or config apply is performed
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
2026-11-01 local baseline, read-only: deployed opencode.jsonc has compaction.auto=false and no Lore plugin entry; /api/plugin has no active @loreai/opencode row. The exact current session was absent from `lore data list sessions --project /Users/ben.davis/.local/share/chezmoi --limit 250 --json` (15 rows). Gateway health is ok, version 0.40.0, local ONNX embeddings available, worker.ok=true and degradedSessions=0; .lore.md is refreshed. Therefore gateway memory/distillation activity exists but does not prove this session is recorded or that Lore performs its visible context reduction. Do not describe the interactive token decrease as Lore plugin compaction. Author priority: first make local OpenCode usable with as much Lore functionality as the supported V2 integration provides; otherwise retain the working gateway and state limitations explicitly. Review DOT-282's isolated fork/VM evidence before any live integration.
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->
