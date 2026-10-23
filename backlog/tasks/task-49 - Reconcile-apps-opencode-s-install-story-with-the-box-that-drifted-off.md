---
id: TASK-49
title: Reconcile apps/opencode's install story with the box that drifted off
status: To Do
created_date: 2026-10-23 16:50
labels:
- migration
ordinal: 47
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
it.** [author ruling 2026-10-19: brew tap stays canonical; agent:
  orch_sub_oc2rec] Measured state 2026-10-19: this box runs opencode
  v2.0.32 through a mise `http:opencode` entry, while the topic (merged
  via #46) installs `anomalyco/tap/opencode-v2` via brew — and brew
  holds the drifted leftovers: v1 formulae 1.18.32 AND 1.19.3 plus
  opencode-v2 2.0.32. The config migration and session migration
  already happened on this box (deployed opencode.jsonc carries the v2
  `permissions` array; sqlite has 223 session_v2 rows), so this is
  install-route reconciliation only, not a config migration. Locate
  where the `http:opencode` mise entry lives (committed repo config vs
  local uncommitted drift — the tool-entry-ownership recipe applies; an
  uncommitted local entry is author-removed, a committed one is removed
  by this work with the claim protocol). Check whether install.yaml's
  v1-removal converges a two-version v1 install (1.18.32 + 1.19.3 under
  one formula name); fix if not. README/CHANGELOG known_issues: the
  drift incident, named per the tool-entry-ownership lesson. Molecule
  run re-validates the brew route on a clean box. Author-run machine
  steps to be listed exactly: remove stale brew v1 versions, remove the
  mise entry if local, reshim, re-resolve. Done when the molecule
  scenario is green, the scoped tests pass, the drift is named in the
  topic docs, and the author's cleanup commands are written.

Legacy: TASKS.md § Now item 47 of 49, migrated to backlog 2026-10-23 (branch agent/backlog-migration).
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
