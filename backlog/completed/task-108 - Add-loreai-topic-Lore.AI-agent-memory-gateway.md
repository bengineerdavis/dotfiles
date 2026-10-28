---
id: DOT-108
title: Add loreai topic (Lore.AI agent-memory gateway)
status: Done
created_date: 2026-10-27 02:56
labels:
- now
priority: high
<<<<<<<< HEAD:backlog/tasks/dot-108 - Add-loreai-topic-Lore.AI-agent-memory-gateway.md
updated_date: 2026-10-27 22:21
|||||||| parent of ad920b0 (Complete TASK-108: loreai topic shipped and provisioned):backlog/tasks/task-108 - Add-loreai-topic-Lore.AI-agent-memory-gateway.md
========
updated_date: 2026-10-28 00:04
>>>>>>>> ad920b0 (Complete TASK-108: loreai topic shipped and provisioned):backlog/completed/task-108 - Add-loreai-topic-Lore.AI-agent-memory-gateway.md
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
Done: PR #70 merged 2026-10-23 (6642983) — quiz answered by the author, two maximum-reasoning roborev rounds triaged to zero open findings; follow-up PR #72 (adopt the roborev MCP block into .chezmoidata/opencode.yaml) also merged. First install recorded 2026-10-22 by the topic session (provision ok=39 failed=0, gateway smoke passed — full record in git history under archive/tasks-md). Provisioned on pop-os 2026-10-27: ok=36 changed=5 failed=0, lore --version 0.40.0, ~/.config/loreai/env.zsh written (telemetry on, inference openrouter, worker model openrouter/z-ai/glm-5.3-flash), lore setup status shows codex routed at the gateway with claude-code entries present; opencode is wired via the chezmoi plugin fragment (deployed in opencode.jsonc). Per-machine answers are the subject of decision-1 / TASK-242, which supersedes the per-machine storage question going forward.
<!-- SECTION:FINAL_SUMMARY:END -->
## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->
