---
id: DOT-297
title: Report the Lore v2 SQLite import gap upstream
status: To Do
created_date: 2026-11-07 17:21
labels:
- loreai
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Lore 0.40.0's OpenCode importer reads the v1 tables only (project, session, message). OpenCode 2.x writes session_v2 and session_message, so 948 sessions are invisible to Lore - including 630 recorded in git worktrees, which is exactly the set /docs/import worktrees--monorepos promises to capture.

Measured 2026-11-07: session_v2 and session_message appear 0 times in the 0.40.0 binary; the upstream importer (packages/core/src/import/providers/opencode.ts on main, 301 lines) hardcodes FROM session / FROM message; the importer last changed 2026-07-15, before the v2 schema; no branch or release adds v2 support. lore import --dry-run reports 24 sessions ending 2026-10-19 while the DB holds 1031 v2 sessions including today's.

Blocked: nothing else unblocks the unify-the-knowledge goal. Direction agreed 2026-11-06: report upstream AND write the reader locally, but do NOT send the fork for maintainer review until the author is ready.
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
