---
id: DOT-240
title: Decide and scope the capture trigger for symlinked chezmoi-managed files
status: To Do
created_date: 2026-10-27 20:17
updated_date: 2026-10-27 22:22
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Changes to symlinked managed files (the mise global config is the common case) are working-tree changes in the chezmoi source, but nothing notices, reviews or opens a PR for them. The author wants a trigger that detects a change, reviews it, and prepares a PR. Options: (1) scheduled capture: a user timer runs git status in the source, branches capture/<date>, commits watched paths, runs checks, opens a draft PR; (2) filesystem watcher (fswatch/watchman); (3) capture before every chezmoi apply. Open decisions: file scope (all managed vs an allowlist, since some managed files may hold secrets), review depth (deterministic checks vs roborev vs an agent, which brings the egress policy in), and build home (a topical command plus timer, a bin/ script, or ai-prompt-library). Per AGENTS.md the build itself needs an author decision before it starts.
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
- [ ] #1 A design is recorded naming the file scope, the review depth and the build home, or the author declines the trigger. No implementation before that record.
<!-- DOD:END -->
