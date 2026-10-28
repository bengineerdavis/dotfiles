---
id: DOT-242
title: Decide opencode-to-lore routing while the plugin is V2-incompatible
status: To Do
created_date: 2026-10-27 22:13
labels:
- loreai
priority: medium
updated_date: 2026-10-28 20:19
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
2026-10-28 measured after PR #88 merged: the chezmoi-captured provider baseURL routes OpenCode through Lore, and gateway logs show knowledge injection despite the V1 plugin's load failure. The explicit route therefore supplies recording and gateway-side recall; the broken plugin is not the whole integration. An isolated probe of lore run opencode shows it sets OPENAI_BASE_URL=http://127.0.0.1:3207/v1 plus OPENCODE_CONFIG_CONTENT for the same broken plugin. The remaining local integration gap is deterministic per-project X-Lore-Project headers: the isolated E2E proves such a header records the correct temp project, while ordinary sessions currently rely on inferred attribution. Scope follow-up work to project-scoped configuration in the agentic-project-template repo, not a local V2 shim in dotfiles. Ask the maintainer before changing that repo. Upstream plugin V2 support remains DOT-244/BYK/loreai#2021; do not claim plugin recall tools, .lore.md generation, or full plugin behavior until it loads.
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->
