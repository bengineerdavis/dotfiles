---
id: DOT-367
title: Provision zsh for Claude credential tests
status: To Do
created_date: 2026-11-16 05:36
updated_date: 2026-11-16 06:05
orchestration:
  status_key: inprogress
  lease_owner: opencode-claude-credential-path
  lease_expires_at: '2026-11-16T07:36:53.062095Z'
  version: 1
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
- [ ] #1 A PATH containing only /usr/bin supplies a usable zsh to the invocation helper.
- [ ] #2 The existing Claude profile tests still pass on macOS with their real zsh fragment and fake CLI.
- [x] #3 A deliberate /bin/zsh restoration fails the new PATH-resolution test.
- [ ] #4 Focused pytest and ruff checks pass.
- [ ] #5 CI installs zsh before the pytest step.
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
<!-- SECTION:RUN_HISTORY:END -->
