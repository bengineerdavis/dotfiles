---
id: DOT-235
title: Update the external_directory pinning test for the agent temp-root allow
status: Done
created_date: 2026-10-27 19:45
labels:
- trunk-red
ordinal: 0
orchestration:
  status_key: inprogress
  lease_owner: opencode-coordinator
  lease_expires_at: '2026-10-27T20:45:22.192325Z'
  version: 1
updated_date: 2026-10-27 22:21
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Commit 23909ea (opencode: allow the agent temp roots outside the project) added the $HOME/.cache/tmp/* allow to the template but never updated its pinning test — test_external_directory_deny_first_allows_last_literal_home asserts exactly 5 external_directory entries and has been red on main since the template change landed. Fix: expect 6 (deny + five allows), name the temp-root allow in the docstring, keep the deny-first ordering assertions. Mutation proof: removing the allow from the template must turn the updated test red. Legacy: observed post-cutover 2026-10-27, full suite 1 failed / 1148 passed.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
Fixed in 3938117: expectation 6, docstring names the temp-root allow, mutation-proven (allow removal turns the test red). Full suite 1149 passed.
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
event_id: run-64c7d1c1a6f842418436aa284d7fd90a
type: claim_task
actor: opencode-coordinator
timestamp: '2026-10-27T19:45:22.192421Z'
result: succeeded
task_id: TASK-235
from_status: todo
to_status: inprogress
metadata:
  lease_ttl_seconds: '3600'
```
Trunk-red fix: the pinning test has been red since 23909ea landed without its companion
<!-- RUN_HISTORY_ENTRY:END -->
<!-- SECTION:RUN_HISTORY:END -->
