---
id: DOT-259
title: 'DRAFT: Reconcile the chezmoi-apply OpenCode permission tier with the main-only
  rule'
status: To Do
created_date: 2026-10-28 17:47
labels:
- permissions
- policy
priority: high
orchestration:
  status_key: inprogress
  lease_owner: opencode-chezmoi-tier
  lease_expires_at: '2026-10-28T20:08:43.643170Z'
  version: 1
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The full suite on 2026-10-28 fails tests/permissions/test_opencode_tiers.py twice for 'chezmoi apply ~/dotfiles': the top-level and autonomous permission blocks return ask where the test expects deny. This is a pre-existing policy mismatch outside the Lore gateway branch. Do not weaken the test or broaden permissions to make a PR green. Reconcile the policy resolver and AGENTS.md main-only rule in a dedicated policy-reviewed change, including the check-only relationship documented in docs/PERMISSIONS.md and tests/permissions/README.md. Consider symlinked-config interactions rather than assuming deny text alone implements the intended protection.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The effective top-level and autonomous OpenCode tiers for chezmoi apply match the documented main-only rule.
- [ ] #2 The permission test and documentation agree about the intended check-only/apply behavior.
- [ ] #3 The policy change receives the required human review and does not weaken an unrelated guard.
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
event_id: run-181819c5278a491483fd3c7d7003b60f
type: claim_task
actor: opencode-chezmoi-tier
timestamp: '2026-10-28T18:08:43.643234Z'
result: succeeded
task_id: DOT-259
from_status: todo
to_status: inprogress
metadata:
  lease_ttl_seconds: '7200'
```
Separate policy reconciliation branch .worktrees/chezmoi-apply-tier.
<!-- RUN_HISTORY_ENTRY:END -->
<!-- SECTION:RUN_HISTORY:END -->
