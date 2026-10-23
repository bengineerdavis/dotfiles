---
id: TASK-15
title: Extract the incoming-changes review into a reusable agent capability,
status: To Do
created_date: 2026-10-23 16:49
labels:
- migration
ordinal: 13
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
with a specification.** High priority, queued by the author 2026-09-15,
  from this session's review pattern: on `git fetch`, before any merge, the
  agent verifies the incoming claims against this machine (`chezmoi status`,
  `ollama list`, path existence), classifies findings as blocking /
  question / nit with file-and-line evidence, and recommends resolutions.
  Routing: with no blocking findings, pass the changes in (fast-forward
  merge); with any, hand the merge to a human via **meld** — `git
  mergetool` or merge-with-conflicts opened in meld — and report the
  finding list for them to resolve. The specification (SHALL/MUST + BDD
  scenarios, house spec style) must fix: the trigger point (post-fetch,
  pre-merge); the verification classes; the conflict taxonomy and what
  counts as blocking versus advisory; the human-handoff via meld and how a
  run resumes after the human resolves; idempotency on repeated runs; and
  the pass-through policy — which gates turn a question into a block.
  Destination per the AGENTS.md ladder (likely a skill/spec in
  ai-prompt-library or llocallabs); any machine-side wiring here is
  provisioning. Done when the spec is written and validated, and the
  capability runs end-to-end against both a deliberately conflicting merge
  (hands to meld) and a clean one (passes through).

Legacy: TASKS.md § Now item 13 of 49, migrated to backlog 2026-10-23 (branch agent/backlog-migration).
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
