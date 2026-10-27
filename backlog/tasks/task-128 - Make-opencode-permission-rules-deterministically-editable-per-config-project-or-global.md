---
id: TASK-128
title: Make opencode permission rules deterministically editable, per config (project
  or global)
status: To Do
created_date: 2026-10-27 02:57
labels:
- planned
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Make opencode permission rules deterministically editable, per config
  (project or global).** Queued 2026-09-16 as the other half of the
  permission fix. Hand-editing the JSONC is error-prone in a specific,
  demonstrated way: opencode matches the **last** rule (`evaluate` uses
  `findLast`; `fromConfig` keeps declaration order), so a trailing
  `"*": "ask"` silently shadows every allow above it and every `deny`
  carve-out anchored below it. The global config shipped that bug until
  2026-09-16 — `git`, `find`, `wc` and `echo` were declared but inert, and
  `find . -delete` fell through to `ask` instead of the intended `deny`. The
  tool must read and write JSONC without dropping comments or reordering
  keys; set or update a rule in a named config (a project `opencode.json`, or
  the global `~/.config/opencode/opencode.jsonc`, which here is a chezmoi
  templated source); normalise the ordering invariant (catch-all first,
  carve-outs after the allow they narrow); and report the merged effect of
  global + project rules for a command, since the scopes deep-merge and the
  project scope wins. **Not the right place to build this now.** It is a tool
  build (AGENTS.md ladder, so route before writing code), it belongs with
  `topical` — the CLI the ROADMAP gives the "abstracts configuration
  management and updates" job, itself scheduled A1–A7 and unlanded — and it
  depends on `apps/opencode` owning its own config (the integrations-phase
  task in § Now) and on the tooling destination (ai-prompt-library /
  llocallabs, per the move manifest). If that route is declined, say so in
  this line rather than starting a script here. Done when the destination is
  decided and a command idempotently updates a named opencode config's
  permission rules, preserves the file's comments and key order, enforces the
  ordering invariant, and is proven by a test that catches a reintroduced
  trailing catch-all. [me]
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
