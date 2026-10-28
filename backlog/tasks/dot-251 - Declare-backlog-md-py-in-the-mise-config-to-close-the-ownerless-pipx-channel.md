---
id: DOT-251
title: Declare backlog-md-py in the mise config to close the ownerless pipx channel
status: In Progress
created_date: 2026-10-28 02:54
labels:
- tool-ownership
ordinal: 1
orchestration:
  status_key: todo
  version: 2
updated_date: 2026-10-28 02:55
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
backlog-py runs on this machine from ~/.local/share/mise/installs/pipx-backlog-md-py/2.2.0 — an install no topic declares, created during the 2026-10-27 cutover outside the mise config. TOPIC-RECIPES' tool-entry-ownership rule: every tool install has an owning entry. docs/BACKLOG-CUTOVER.md already designs the fix ('pipx:backlog-md-py through mise'); this executes it. Fix: add "pipx:backlog-md-py" = "latest" to the pipx section of dotfiles/apps/mise/files/config.toml, matching the pipx:pre-commit / pipx:git-filter-repo convention. mise's pipx backend will adopt the existing install (same layout) rather than reinstall. Legacy: the backlog cutover left the tool running ownerless.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
2026-10-28: landed as PR #94 (pipx-section entry + provenance comment). TOML parse verified, single key asserted. COLLISION flagged in the PR: a leaseless uncommitted duplicate declaration sits in the main checkout's working tree — discard it at merge time or the file breaks. Apply after merge is author-tier.
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->

## Run History
<!-- SECTION:RUN_HISTORY:BEGIN -->
<!-- RUN_HISTORY_ENTRY:BEGIN -->
```yaml
event_id: run-fb2161ac1ef9490291e5ec541bf955fa
type: claim_task
actor: opencode-coordinator
timestamp: '2026-10-28T02:54:51.653991Z'
result: succeeded
task_id: DOT-251
from_status: todo
to_status: inprogress
metadata:
  lease_ttl_seconds: '3600'
```
Add the owning mise entry per TOPIC-RECIPES tool-entry-ownership; the cutover doc already designs this line
<!-- RUN_HISTORY_ENTRY:END -->
<!-- RUN_HISTORY_ENTRY:BEGIN -->
```yaml
event_id: run-fb000f7df65d4127884139b50c0ea050
type: release_task
actor: opencode-coordinator
timestamp: '2026-10-28T02:55:52.600684Z'
result: succeeded
task_id: DOT-251
from_status: inprogress
to_status: todo
```
<!-- RUN_HISTORY_ENTRY:END -->
<!-- SECTION:RUN_HISTORY:END -->
