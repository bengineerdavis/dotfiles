---
id: DOT-265
title: Prove LoreAI on Linux through the shared Lima adapter
status: To Do
created_date: 2026-10-29 02:22
dependencies:
- DOT-263
assignee:
- opencode
labels:
- testing
- molecule
- chore
priority: high
orchestration:
  status_key: inprogress
  lease_owner: opencode-loreai-lima
  lease_expires_at: '2026-10-29T03:23:16.951382Z'
  version: 1
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Run apps/loreai in a real Debian 12 Lima VM, then reuse the exact Lima create/destroy/template seam as its second consumer. Branch agent_loreai-lima and worktree .worktrees/loreai-lima are already created; stack on the Lima topic and rebase onto main before implementation. The scenario must exercise the topic, not merely a copied shell probe. No host chezmoi apply, host service change, host credential access, LLM inference, Vagrant work, or merge into main.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A real Debian 12 Lima guest boots and SSH inventory resolves through the delegated instance_config contract.
- [ ] #2 The actual apps/loreai topic converges with telemetry and inference disabled and is idempotent.
- [ ] #3 Verification runs after converge and proves the enabled/active user gateway and local read-only HTTP behavior, not just files.
- [ ] #4 Removal preserves explicitly planted memory data, is idempotent, and destroys only scenario-owned VM/state.
- [ ] #5 The Lima scenario references the same lifecycle adapter; adapter-specific test coverage proves path resolution and both scenarios remain runnable.
- [ ] #6 The full green lifecycle and any unverified platforms are reported accurately; a skipped or destroyed guest is not a pass.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Use Molecule native path references, not a new Python driver. Start with a minimal guest prepare and local gateway HTTP verification. Preserve the existing Vagrant PR separately. Add bounded parallel scenario execution only as a later task; do not make it a prerequisite for this proof.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->

<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 Both Lima and LoreAI scenarios use one referenced lifecycle adapter and pass their intended real-VM verification; topic-owned preservation is checked; only scenario state is removed; tests are seen failing before passing; branch is ready for human review with host and Linux-host Lima coverage limitations stated.
<!-- DOD:END -->

## Run History
<!-- SECTION:RUN_HISTORY:BEGIN -->
<!-- RUN_HISTORY_ENTRY:BEGIN -->
```yaml
event_id: run-f790ceba0cd440db813309d0538b2bb5
type: claim_task
actor: opencode-loreai-lima
timestamp: '2026-10-29T02:23:16.951449Z'
result: succeeded
task_id: DOT-265
from_status: todo
to_status: inprogress
metadata:
  lease_ttl_seconds: '3600'
```
<!-- RUN_HISTORY_ENTRY:END -->
<!-- SECTION:RUN_HISTORY:END -->
