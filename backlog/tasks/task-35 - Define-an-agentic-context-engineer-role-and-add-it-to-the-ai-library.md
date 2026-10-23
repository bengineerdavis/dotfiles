---
id: TASK-35
title: Define an `agentic-context-engineer` role and add it to the ai library
status: To Do
created_date: 2026-10-23 16:49
labels:
- migration
ordinal: 33
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A role, not a skill: it is invoked deliberately for open design questions,
  wants its own context, and returns a considered answer — where a skill changes
  how the current work is done. Distribute it as a `[[subagents]]` entry rather
  than hand-placing a file in `~/.claude/agents`, so it installs the same way the
  skills do and survives a rebuild (dotagents projects subagents to
  `~/.claude/agents/*.md` at user scope; confirmed 2026-09-12). The role must
  **compose** the existing method skills — `review-best-practices`,
  `interaction-questioning`, `no-ai-slop` — and add only framing and judgement on
  top; a persona that restates method it could have loaded is the failure mode
  here. Done when `/agentic-context-engineer` answers an open question with a
  recommendation and its rejected alternatives, and the definition installs from
  `ai-prompt-library` on a fresh machine. [me]

Legacy: TASKS.md § Now item 33 of 49, migrated to backlog 2026-10-23 (branch agent/backlog-migration).
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
