---
id: DOT-176
title: G7 — discover repositories through gh with explicit per-machine modes
status: To Do
created_date: 2026-10-27 02:58
labels:
- planned
- group:gita-and-machine-file-backup-approved-2026-09-23
updated_date: 2026-10-27 22:22
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**G7 — discover repositories through gh with explicit per-machine modes.**
  After G5, implement G1's selected discovery approach. Personal sources
  live in the committed catalogue; private sources, including work orgs,
  live only in that machine's local file. A source's per-machine mode is
  `add`, `report` (default), or `off`. These modes apply to user-run update;
  timer runs report only, never adding discovered clones. Tag discovery
  tasks `[install, upgrade]` so update's upgrade-only invocation finds them.
  Missing gh, logged-out access, rate limiting or truncation means UNKNOWN,
  never an empty result: add nothing and unregister nothing, while explicit
  repos still sync. The handoff verified on 2026-09-23 that `gh repo list`
  defaults to `--limit 30`; always set a limit and treat a full page as
  truncated. Add at most ten repos per run. Skip archived repos by default.
  Classify forks into `forks/`, templates into `templates/`, and other new
  clones into the source's declared type, carrying the author confirmation
  requested at G5's start. Existing clones are not relocated automatically.
  Record which gh account listed the source; private repos invisible to
  another account make the report partial, not evidence of absence.
  Write discovered entries to a separate machine-written record, never
  back into hand-edited YAML or its comments, and never back that record up.
  Removing a discovered repo means adding it to the source's exclude list;
  otherwise the next update rediscovers it. Keep the opt-in unregister and
  never-delete-clones rules from G3.
  Done when `report` and `add` work end to end and a gh failure cannot read
  as "no repos", proven by mutation. This item runs serially after G4 and
  G5 because all three edit the gita upgrade path.
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
