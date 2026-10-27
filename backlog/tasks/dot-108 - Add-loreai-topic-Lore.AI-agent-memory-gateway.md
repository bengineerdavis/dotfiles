---
id: DOT-108
title: Add loreai topic (Lore.AI agent-memory gateway)
status: To Do
created_date: 2026-10-27 02:56
labels:
- now
priority: high
updated_date: 2026-10-27 22:21
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Add loreai topic (Lore.AI agent-memory gateway).** Author-directed
  2026-10-21. New `apps/loreai/`: checksum-verified standalone binary
  install from BYK/loreai releases (the `apps/ori` pattern — topic owns
  its upgrade), per-agent `lore setup` extensions behind detection
  (claude-code, codex, pi, hermes; opencode via a chezmoi-included
  plugin fragment, because chezmoi owns that config), first-install
  prompts (telemetry, worker-model inference) saved per machine under
  `~/.config/loreai/`, `lore import` report-only. Done when the PR is
  open with syntax-check and `--check` evidence and the author has
  answered the merge quiz. [agent: this session] (branch
  `agent/loreai_topic`, worktree `.worktrees/loreai-topic`).
  **PR #70 open 2026-10-21** — quiz answered 2026-10-21; awaiting
  author review and merge.
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
