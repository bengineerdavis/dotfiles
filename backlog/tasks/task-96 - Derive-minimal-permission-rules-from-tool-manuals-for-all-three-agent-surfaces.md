---
id: TASK-96
title: Derive minimal permission rules from tool manuals for all three agent surfaces
status: To Do
created_date: 2026-10-27 02:56
labels:
- now
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Derive minimal permission rules from tool manuals for all three agent
  surfaces.** Queued by the author 2026-09-23: a subagent reviews the full
  help menus and manuals for every tool the repo's agents invoke — git,
  chezmoi, uv, pytest, mise, and the rest — classifies each subcommand and
  flag as safe (allow), irreversible (ask), or dangerous (deny), and writes
  the result into the three permission configs: `opencode.jsonc` (opencode),
  `.claude/settings.json` (Claude Code), and Cursor's `cli.json`. The goal
  is fewer approval prompts without weakening the deny tier. Known gaps to
  close: `env *` is an arbitrary-exec wrapper in the allow tier;
  `sed -i`/`awk system()`/`rg --pre` can execute code; `git checkout .`/
  `git restore .` destroy uncommitted work; `git -C` bypasses
  subcommand-level rules. Done when all three configs carry rules derived
  from the tools' own documentation, the deny tier still blocks
  `chezmoi apply`, force-push, and credential paths, and a deliberately
  dangerous command has been seen to prompt. [agent: sub]
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
