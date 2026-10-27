---
id: DOT-140
title: Bring the portable half of `~/.claude/` under chezmoi
status: To Do
created_date: 2026-10-27 02:57
labels:
- planned
updated_date: 2026-10-27 22:22
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Bring the portable half of `~/.claude/` under chezmoi.** Deferred from the
  claude-code topic (`c988fef`), which owns the binaries and deliberately left
  config alone. Nothing there is versioned today, so user-global settings do not
  survive a machine. The work is the split, not the plumbing: `settings.json`,
  `CLAUDE.md`, `agents/` and `commands/` are portable, while `history.jsonl`,
  `projects/`, `session-env/`, `daemon/`, `backups/`, `file-history/` and
  `~/.claude.json` are machine-local and must never be committed — the last of
  those holds credentials. chezmoi owns the files once split, per the layering
  rule in `AGENTS.md`; the topic does not template them. Two hazards worth
  knowing before starting: the VS Code extension, the JetBrains plugin and the
  desktop app all write `~/.claude/`, so the directory is not Claude Code's
  alone; and `apps/opencode` already owns `~/.agents/skills` via dotagents,
  which Claude auto-loads, so nothing here may write skills. Done when the
  portable files deploy from the chezmoi source on a fresh machine, `chezmoi
  status` is clean afterwards, and no machine-local state or credential has
  entered git.
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
