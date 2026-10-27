---
id: TASK-52
title: Evaluate interchangeable components for agent work
status: To Do
created_date: 2026-10-27 02:55
labels:
- now
priority: high
references:
- .claude/HANDOFF-modular-agent-runtime.md
updated_date: 2026-10-27 22:18
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Agent-work components must be independently replaceable: task queues, orchestration, workspace creation, sandbox runtimes, and environment setup — session/UI tooling optionally. Verify each tool's actual role instead of assuming all are queue managers.

State 2026-10-27: initial comparison complete; native macOS probes done (SRT 0.0.77's false-success exit and mise 2026.9.12's host-network failure both reproduced; filesystem restrictions worked); Debian and end-to-end swaps unrun. The missing evidence is a low-configuration container walkthrough. No research agent is running — resume from the handoff.

Compare: Sandcastle (mattpocock/sandcastle) non-root containers, anthropics/sandbox-runtime, maintained bubblewrap/Seatbelt consumers on macOS and Debian, workmux's container workflow, and a native-wrapper baseline. Worktrunk and mise are the baseline, not mandatory dependencies; include a workspace alternative that does not require Git worktrees.

Author clarifications 2026-09-24: non-root containers are first-class candidates when applying them requires very low configuration; native execution is a workload capability, not a universal requirement; task storage, dispatch, workspace allocation, sandboxing and environment setup stay independently swappable.

Feeds the existing sandboxing and coordination items. Report: .claude/RESEARCH-modular-agent-runtime.md (committed on main). Pickup: .claude/HANDOFF-modular-agent-runtime.md.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Evidenced report identifies the replaceable boundary for each component: queue, orchestration, workspace allocation, sandbox runtime, environment setup
- [ ] #2 Ownership and lifecycle contracts recorded per component (who creates, who reaps, what survives a session death)
- [ ] #3 Compatible combinations ranked; rejected options and platform gaps recorded
- [ ] #4 Container-setup effort measured on a real backend (the missing evidence) and reviewed with the author
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
