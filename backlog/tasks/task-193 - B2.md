---
id: TASK-193
title: B2
status: To Do
created_date: 2026-10-27 02:58
labels:
- planned
- group:refactor-b-factor-the-ai-llm-tooling-out-of-this-repo
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
B2. Write the move manifest — every affected file classified as leaves, stays,
  or is deleted. Done when the list exists and later items cite it instead of
  re-deciding per file.
  **The llocallabs cluster and its timing dependencies (recorded 2026-09-14,
  corrected by the advisor pass 2026-09-15).** Six queued items cite each
  other. The gate structure has TWO independent roots, not one linear order:
  the manifest needs the anchor repo to exist (a manifest naming a
  nonexistent home is a guess) AND B1's install-method answer, which is
  deliberately still open. (2) The three research projects queued in § Now
  and § Planned (sandboxing, session-management handoff, RAG/graphs) are
  first-class llocallabs candidates — but which branch fires, start-there
  or start-here, is the AUTHOR'S call, made and recorded in the session
  that starts the work; without that arbiter two machines can pick opposite
  branches and both be following this file. (3) gita is a consumer, not a
  gate: its per-machine inventory must include the collection once it
  exists, but it waits on nothing here. (4) The strategy/policy agent
  consumes the research projects and cannot be stood up ahead of them.
  (6) The R&D factory is gated on the anchor repo and is the umbrella the
  research methods feed — it belongs to the collection from day one.
  Prerequisite the cluster silently assumed, now named: the capture store
  (`~/code/personal/llocallabs-capture/`) is unversioned,
  single-machine, and mixes private with shareable notes — before any
  cluster item starts on the second machine it must be versioned or synced
  AND separated (see the capture-store contract task in § Planned). Until
  the manifest lands, nothing in the cluster moves, and no item in it
  should be worked on the assumption it stays here forever.
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
