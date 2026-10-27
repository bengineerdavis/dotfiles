---
id: TASK-104
title: Give `codex` an authenticated provider — Darwin only for now
status: To Do
created_date: 2026-10-27 02:56
labels:
- now
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Give `codex` an authenticated provider — Darwin only for now.**
  `apps/mise` installs `npm:@openai/codex`, but no topic provisions
  `~/.codex/config.toml`, so the binary has no backend and every model call
  dies with "Not logged in"/401 (no codex subscription). Scoped to the Mac for
  now; the Linux box waits. Done when an `apps/codex` topic (adopting the mise
  entry, `topic_os: [Darwin]`) ships a chezmoi-managed config.toml with a
  `model_providers` block on the already-provisioned OpenRouter key, a model
  call succeeds on the Mac without a subscription, and the teardown removes
  the config it created.
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
