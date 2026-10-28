---
id: DOT-94
title: Decide when `scriv collect` runs
status: Done
created_date: 2026-10-27 02:56
labels:
- now
priority: high
updated_date: 2026-10-28 20:08
orchestration:
  status_key: inprogress
  lease_owner: opencode
  lease_expires_at: '2026-10-28T19:38:57.339842Z'
  version: 1
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Decide when `scriv collect` runs. The changelog exists and fragments
  accumulate, but nothing says what a "release" is for a dotfiles repo that does
  not release. Candidates: on a cadence, at each machine rebuild, or never —
  leaving everything under Unreleased, which is legitimate and costs nothing.
  Until this is settled the changelog grows one section and is still readable.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
Author ruling 2026-10-28: every merged PR is the changelog collection point for now; this does not introduce semantic versions, tags, or GitHub Releases. Use the existing scope: imperative statement commit convention, not Conventional Commits. Dedicated branch/worktree changelog-merge. Use a merged-PR GitHub Actions collector with least-privilege contents:write, pinned actions, PR-scoped dated headings, serialized runs, and only fragments introduced by that PR. Bootstrap the historical fragment backlog separately in the same PR. Human review required for the new main-write automation; rebase other active PR branches after it merges.
Completed 2026-10-28 by PR #97 (merge 04630eb). Root/chezmoi-source changelog collector merged; 35 historical fragments collected separately; per-topic changelogs remain independent. Live workflow run 40759134598 succeeded and correctly no-opped because PR #97 introduced no new fragments. Local selected-fragment rehearsal preserved unrelated fragments and existing entries; empty scriv collection exits 2 and is guarded by the workflow. 73 focused tests, actionlint and skillet validation passed. No version tags or GitHub Releases created.
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
event_id: run-2597fbfe5e2a499d89f85e14e0907fd4
type: claim_task
actor: opencode
timestamp: '2026-10-28T18:38:57.339909Z'
result: succeeded
task_id: DOT-94
from_status: todo
to_status: inprogress
metadata:
  lease_ttl_seconds: '3600'
```
Author decision 2026-10-28: each PR merge is the changelog collection point; no semantic-version/GitHub releases. Own dedicated changelog-merge worktree/branch.
<!-- RUN_HISTORY_ENTRY:END -->
<!-- RUN_HISTORY_ENTRY:BEGIN -->
```yaml
event_id: run-63e7c99de1214e7d8843aaf4cf8fea73
type: record_run
actor: opencode
timestamp: '2026-10-28T18:53:24.659331Z'
result: in-progress
task_id: DOT-94
```
Implementing merged-PR scriv collection in the dedicated changelog-merge worktree. Design uses only default-branch workflow, pinned actions, PR-file fragment selection, dated PR titles, and serialized main writes. Author then redirected priority to PR #88 after this small workflow is finished.
<!-- RUN_HISTORY_ENTRY:END -->
<!-- SECTION:RUN_HISTORY:END -->
