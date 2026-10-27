---
id: TASK-52
title: Evaluate interchangeable components for agent work
status: To Do
created_date: 2026-10-27 02:55
labels:
- now
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Evaluate interchangeable components for agent work.**
  [handoff ready, unclaimed; initial comparison complete, container setup
  assessment pending; 2026-09-24] The author approved the expanded brief. Task queues,
  orchestration, workspace creation, sandbox runtimes,
  and environment setup must be independently replaceable or removable.
  Include Backlog.md, workmux, herdr, and other relevant options; verify each
  tool's actual role instead of assuming all are queue managers. Compare
  Sandcastle (`mattpocock/sandcastle`), `anthropics/sandbox-runtime`, and
  maintained bubblewrap/Seatbelt consumers on macOS and Debian. Worktrunk and
  mise are the baseline, not mandatory dependencies; include a workspace
  alternative that does not require Git worktrees. Use local repositories,
  prior research and queued decisions alongside upstream docs, source and
  practitioner reports. This feeds the existing sandboxing and coordination
  items. Done when an evidenced report identifies replaceable boundaries,
  ownership and lifecycle contracts, ranks compatible combinations, records
  rejected options and platform gaps, and is reviewed with the author.

  Author clarification, 2026-09-24: non-root containers, including Sandcastle's
  approach, are first-class candidates when applying them requires very little
  configuration. Native execution is a workload capability, not a universal
  selection requirement. Compare host prerequisites, fresh-project setup,
  required files/settings/commands, reusable images or templates, credential
  wiring, and ongoing configuration maintenance. Preserve independent task,
  workspace and runtime choices. Next evidence needed: a low-configuration
  Sandcastle/container walkthrough against the native-wrapper baseline.

  Report: `.claude/RESEARCH-modular-agent-runtime.md` (committed on `main`
  2026-10-03). The research agent mapped local prior work, verified
  queue/runtime interfaces, and ran macOS synthetic probes. Coordinator review
  reproduced SRT 0.0.77's false-success signal exit and mise 2026.9.12's failed
  host-network exception, alongside successful filesystem restrictions.
  Queue and workspace substitutions are interface-supported proposals;
  Debian and end-to-end swaps remain unrun. Decide next: serialized versus
  autonomous claims, worker commit authority, required network/IPC controls,
  and resume/retention ownership. The completed research unit is archived in
  `TASKS-RESOLVED.md`; implementation remains a separate decision.

  **Pickup:** `.claude/HANDOFF-modular-agent-runtime.md`, committed on `main`.
  The initial research and coordinator review
  are complete; no research agent remains running. The author clarified that
  low-configuration non-root containers are primary options. Next: compare
  Sandcastle's shipped container setup, workmux's container workflow and a
  native wrapper. The handoff and sibling report are committed under
  `.claude/` on `main`.
  They retain the latest requirements and evidence where this queue's older
  research text differs.
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
