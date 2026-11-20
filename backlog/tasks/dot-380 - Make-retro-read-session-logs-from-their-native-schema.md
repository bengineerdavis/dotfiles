---
id: DOT-380
title: Make retro read session logs from their native schema
status: To Do
created_date: 2026-11-19 21:28
updated_date: 2026-11-19 21:28
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The retro workflow can waste effort parsing a multi-megabyte session export using an assumed message shape. OpenCode exposes session metadata and per-session schemas through its native CLI and API.

Ship:

- Propose a retro instruction that inspects the session log schema and a small sample before extracting evidence.
- Propose native session filtering by checkout and session id for coordination findings.

Constraints:

- The retro skill belongs to mattpocock-skills, not the dotfiles deployed payload.
- The maintainer does not want the retro skill edited in this round; this task records its future external-repository work only.
- Verify any implementation against the installed OpenCode CLI help and API schema.

Agreed with the maintainer 2026-11-18: record the external skill improvement but do not edit it now.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The proposed instructions require inspecting native session metadata or a small log sample before parsing the full export.
- [ ] #2 The proposed instructions scope coordination evidence by exact checkout and session id.
- [ ] #3 The owning repository and the review path are recorded before any implementation begins.
- [ ] #4 The installed OpenCode CLI help or API schema is cited as evidence for the proposed commands.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
Handoff from the Git-topic session retro: no implementation started and no external repository was modified. The proposed command surface was probed with opencode session list --format json and the OpenCode OpenAPI document. Filter returned session records by their exact directory; use /api/session/active only to distinguish currently running sessions from idle ones. Do not infer file ownership from session activity alone.
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->
