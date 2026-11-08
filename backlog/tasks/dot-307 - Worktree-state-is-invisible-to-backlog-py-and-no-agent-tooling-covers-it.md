---
id: DOT-307
title: Worktree state is invisible to backlog-py and no agent tooling covers it
status: To Do
created_date: 2026-11-08 16:54
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Measured 2026-11-07 in an isolated project (init --defaults --agent-instructions, then a worktree on a probe branch):

1. `backlog-py agents --update-instructions` writes four files (AGENTS.md, CLAUDE.md, GEMINI.md, .github/copilot-instructions.md) with a marker-delimited 'Backlog.md Workflow' section. That section mentions `worktree` **zero** times (43-line AGENTS.md, grep -ci worktree = 0). Regenerating the instructions therefore cannot fix worktree task visibility — the gap is structural, not instructional.
2. The tool's ignorance is load-bearing. With `checkActiveBranches: true` a task committed on another branch IS visible from the main checkout, but a task created **uncommitted** in a worktree is invisible from main, and `doctor` still reports 'No problems found.' That is the silent-resurrection shape DOT-246 exists to prevent, now confirmed as a live property of the tool rather than a stale-session accident.

Worktrunk already solves the adjacent half: v0.81.0 ships per-agent plugins (Claude Code, Codex, OpenCode, Pi, oh-my-pi, Gemini), activity markers in `wt list`, and — under OpenCode 2 — a `worktrunk` worktree strategy that routes worktree create/remove through `wt`. The dotfiles repo already adopts it (apps/mise config line 99, paired with the DOT-109 queue migration).

So: worktree registration and state tracking are worktrunk's job, backlog's gap is task visibility across worktrees, and nothing yet closes the second one. Decide what to do about the backlog half — an upstream feature request, a pre-commit/docs guard, or accepting it and documenting the pull-before-write rule harder.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The backlog worktree-visibility gap has a recorded decision: upstream request, local guard, or accepted-and-documented
- [ ] #2 If a guard is chosen, a test proves an uncommitted worktree task is detected rather than silently ignored
- [ ] #3 The finding is captured for the agentic-project-template feature request without duplicating that request here
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
