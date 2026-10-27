---
id: TASK-130
title: 'Research agent sandboxing for projects and user tasks on this machine — deep
  research, debated with '
status: To Do
created_date: 2026-10-27 02:57
labels:
- planned
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Research agent sandboxing for projects and user tasks on this machine —
  deep research, debated with a council of advisors, delivered as a two-phase
  project with a spec binding them.** The permission tiers in
  `docs/PERMISSIONS.md` gate what tools agents may run but do not isolate
  what a permitted tool can touch — sandboxing is the layer they cannot
  provide. **Phase 1 — requirements.** Write the spec: what is being
  sandboxed (agents working in project directories, agent-driven user tasks
  on the machine), against which threats (egress, writes outside declared
  scope, credential access, machine-config mutation), under which constraints
  (macOS and Debian targets, one machine-management repo, the existing
  `bin/policy` boundary model, agents never applying chezmoi). Debated with
  the council before the author approves it. **Phase 2 — apply.** Update the
  spec with what the research taught and land the background knowledge where
  it is consumed: `bin/policy` boundary keys, the agent permission layers,
  and topic/machine configuration — as queued tasks citing the spec, never
  implemented silently. Initial leads, author-provided 2026-09-14, fetched
  and verified that day: wincent's "Coding Agent Sandboxes — Comprehensive
  List", a taxonomy from OS primitives to policy layers
  (https://gist.github.com/wincent/2752d8d97727577050c043e4ff9e386e);
  "Sandboxing AI coding agents with Lima", VM-grade isolation with
  near-native UX, naming egress and forwarded secrets as the unsolved gaps
  (https://bogoyavlensky.com/blog/sandboxing-ai-coding-agents-with-lima/);
  and `nono`, least-privilege per-agent and per-tool sandboxes with a
  credential proxy and L7 filtering, Apache-2.0, from the Sigstore team
  (https://github.com/nolabs-ai/nono). The council debate pairs with the
  panel-of-judges item below — settle that first or borrow its method.
  Lead from the second research capture (2026-09-14,
  `~/code/personal/llocallabs-capture/`): Omnigent —
  **[verified]** Apache-2.0 and active — claims bubblewrap (Linux) /
  Seatbelt (macOS) sandboxing with cost tracking across agent CLIs.
  **A lead, not a selection** — the capture's other options were routed by
  subject and verification: nono and Lima remain the primary leads
  (capture #1); Caliber generates config rather than sandboxing (its own
  evaluation task); AgentMD is a claimed-frozen spec; OpenCtx is archived
  in favour of MCP; ctx-open is unlicensed and stale (reference only);
  Backlog.md and `handoff` are session-state tools (routed to the
  session-management research); Podman-on-macOS is a constraint input, not
  a candidate. Verification so far is first-order only — existence,
  licence, activity; Omnigent's enforcement claims and its claimed
  Databricks backing are UNVERIFIED and come from the same AI-generated
  source that produced the Caliber npm-scope discrepancy.
  **Post-advisor demotion:** the routing test was applied asymmetrically —
  Omnigent's own description is orchestration-first with sandboxing as one
  feature, so it fails the same subject test that excluded Caliber. Treat
  it as contextual reference for the debate, not a peer lead, and note the
  lead-admission bar silently moved from author-provided to capture-sourced:
  capture-sourced leads need deeper verification before entering the
  council debate. The Podman-on-macOS constraints (hidden Linux VM, nested-virtualization
  limits, network rules applied inside the machine rather than the host)
  still stand as phase-1 requirements for the macOS target. Lead from the
  author 2026-09-15, verified same day: `opencodebox`
  (https://github.com/fityannugroho/opencodebox) — MIT, a bash wrapper
  running opencode inside a bubblewrap sandbox with namespace isolation,
  read-only system mounts, per-project read-write binds, a seccomp filter
  for recent socket CVEs, and refusal to run from sensitive dirs.
  **Linux-only** (bubblewrap needs Linux namespaces), so it is a Debian-side
  candidate, not a macOS answer — and a concrete reference for the
  per-project bind-mount shape on that target. Small and new (3 stars, 34
  commits): first-order verification only, like the other capture-sourced
  leads. Done
  when the phase-1 spec exists, the council debate is recorded, the author
  has approved the requirements, and phase 2's changes are queued rather
  than imagined. [me]
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
