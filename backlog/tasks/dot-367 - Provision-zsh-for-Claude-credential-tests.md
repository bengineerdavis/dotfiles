---
id: DOT-367
title: Provision zsh for Claude credential tests
status: To Do
created_date: 2026-11-16 05:36
updated_date: 2026-11-17 18:14
orchestration:
  status_key: todo
  version: 2
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Ubuntu CI fails six Claude credential tests because their real-shell harness assumes a macOS zsh path. The official runner image has no zsh package.

Ship:

- Resolve zsh on the test PATH instead of assuming its macOS location.
- Install zsh as an explicit CI prerequisite.
- Keep the existing real-zsh and fake-Claude invocation seam unchanged.

Constraints:

- Do not skip the tests on Ubuntu, replace zsh with bash, or access provider credentials.
- Test the helper at its public invoke seam with an isolated PATH.
- Do not edit deployed configuration or run chezmoi apply.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 A PATH containing only /usr/bin supplies a usable zsh to the invocation helper.
- [x] #2 The existing Claude profile tests still pass on macOS with their real zsh fragment and fake CLI.
- [x] #3 A deliberate /bin/zsh restoration fails the new PATH-resolution test.
- [x] #4 Focused pytest and ruff checks pass.
- [x] #5 CI installs zsh before the pytest step.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
Final checks after type guard: 17 focused tests passed, ruff and formatting passed, pyrefly 0 errors, three mutation tests went red on intended assertions. Repair commit 2a9b9c7 has all applicable prek hooks passing. Ubuntu apt execution remains CI verification; no local apt or live-home mutation performed.
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented and locally verified the CI zsh prerequisite and PATH-based shell lookup. Ubuntu execution awaits the pushed CI run; the separate OpenCode fixture defect is DOT-369.
<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->

## Run History
<!-- SECTION:RUN_HISTORY:BEGIN -->
<!-- RUN_HISTORY_ENTRY:BEGIN -->
```yaml
event_id: run-42ebac19f54b4e21809afb2094752603
type: claim_task
actor: opencode-claude-credential-path
timestamp: '2026-11-16T05:36:53.062181Z'
result: succeeded
task_id: DOT-367
from_status: todo
to_status: inprogress
metadata:
  lease_ttl_seconds: '7200'
```
Resolve the six Ubuntu CI failures at the existing real-shell test seam.
<!-- RUN_HISTORY_ENTRY:END -->
<!-- RUN_HISTORY_ENTRY:BEGIN -->
```yaml
event_id: run-2cfeb53e7602459c99d7e14f07b54924
type: release_task
actor: opencode-claude-credential-path
timestamp: '2026-11-17T16:57:20.882923Z'
result: succeeded
task_id: DOT-367
from_status: inprogress
to_status: todo
```
Focused tests and both mutations proven; hand the verified change to review while CI proves Ubuntu.
<!-- RUN_HISTORY_ENTRY:END -->
<!-- SECTION:RUN_HISTORY:END -->
