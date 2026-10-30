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
  version: 3
  lease_owner: opencode-loreai-lima
  lease_expires_at: '2026-10-30T03:48:05.763409Z'
updated_date: 2026-10-29 02:42
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
2026-10-28: real Debian 12 ARM64 Lima guest passed LoreAI converge, zero-change idempotence, active+enabled systemd user service, local GET /ui with dashboard content, two removals, planted memory preservation, stopped service, and scoped VM teardown. No host credentials, LLM inference, or host service changes. Lima regression and LoreAI explicit-prepare sequential runs also green. Bounded independent parallel probe: both full lifecycles rc=0, elapsed 97s on this 14-core/36GiB host; one run, no general worker-count or speedup claim. New contract tests separate adapter, runtime, preservation and lifecycle ordering; parsed argv/uri replaces fragile command-string matching. QEMU resolver initially failed because literal qemu is not a binary; actual-system probe mapping fixed and both resolution legs pass.
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
<!-- RUN_HISTORY_ENTRY:BEGIN -->
```yaml
event_id: run-8eb6842ff4d74be49710489a06d900f4
type: release_task
actor: opencode-loreai-lima
timestamp: '2026-10-30T02:48:05.338129Z'
result: succeeded
task_id: DOT-265
from_status: inprogress
to_status: todo
```
Renew the stale verification lease for the rebased home-payload scenario
<!-- RUN_HISTORY_ENTRY:END -->
<!-- RUN_HISTORY_ENTRY:BEGIN -->
```yaml
event_id: run-9ad9a45d75ef46939874a805535d175a
type: claim_task
actor: opencode-loreai-lima
timestamp: '2026-10-30T02:48:05.763471Z'
result: succeeded
task_id: DOT-265
from_status: todo
to_status: inprogress
metadata:
  lease_ttl_seconds: '3600'
```
Verify the home-payload scenario and record test-residue safeguards
<!-- RUN_HISTORY_ENTRY:END -->
<!-- SECTION:RUN_HISTORY:END -->
