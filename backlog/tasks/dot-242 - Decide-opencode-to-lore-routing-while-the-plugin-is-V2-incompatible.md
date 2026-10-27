---
id: DOT-242
title: Decide opencode-to-lore routing while the plugin is V2-incompatible
status: To Do
created_date: 2026-10-27 22:13
labels:
- loreai
priority: medium
updated_date: 2026-10-27 22:22
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Options surfaced from the 2026-10-27 diagnosis: (a) write a local V2-native shim plugin (small build - needs author approval per the build-ladder; proper home is upstream), (b) wait for the upstream V2 port (opencode unrouted until then), (c) chezmoi-config partial: compaction.auto=false + provider baseURL repoint (no per-project attribution, so still no .lore.md for opencode). Separately: claude-code needs a per-project .claude/settings.local.json with ANTHROPIC_CUSTOM_HEADERS carrying 'X-Lore-Project: <abs path>' for attribution (the gateway log's own prescription); codex needs an equivalent per-project header mechanism (verify codex supports per-provider http_headers). The per-project header file is the template-repo stamping the author intuited.
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
