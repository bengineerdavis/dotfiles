---
id: DOT-308
title: Extend the loreai molecule scenario to verify the X-Lore-Provider header on
  a Debian guest
status: To Do
created_date: 2026-11-08 17:01
labels:
- testing
- loreai
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
PR #134 landed the X-Lore-Provider: openrouter header in lore-plugin.jsonc (DOT-242.1). The header is chezmoi-rendered, not Ansible-installed, so neither loreai molecule scenario (debian vagrant, debian-lima) currently exercises it. This task extends debian-lima to render ~/.config/opencode through chezmoi on a real disposable Debian guest and assert the header lands under provider.openrouter.options.headers.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
1. The `debian-lima` scenario's prepare installs chezmoi and syncs the chezmoi source into the guest.
2. The converge (or a dedicated step) runs `chezmoi --source /repo apply ~/.config/opencode` and renders the real config on the guest.
3. Verify asserts `X-Lore-Provider: openrouter` under `provider.openrouter.options.headers` in the deployed `opencode.jsonc` (or via `opencode debug config`).
4. The scenario still passes end to end (`test` verb green) on this box, and the header assertion is proven to fail when the header is removed (mutation recorded).
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
Sync mechanism settled by sandbox comparison 2026-11-08: rsync the chezmoi source into the guest (loreai-scoped), NOT a lima mount. The lima adapter's default 9p `virtfs` mount silently no-ops on the Debian cloud guest (`/proc/filesystems` has no 9p support; `/repo` is created but empty) — a green-but-wrong failure the repo's silent-skip rules forbid. Empirically proven end-to-end in a throwaway VM: rsync of the repo root → `/repo` (`.chezmoiroot` = `home`), `chezmoi --source /repo apply ~/.config/opencode` renders `X-Lore-Provider: openrouter` at line 219 under `provider.openrouter.options.headers`.

Depends on PR #134 (already merged) for the header source; this task verifies it in a real guest.
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->
