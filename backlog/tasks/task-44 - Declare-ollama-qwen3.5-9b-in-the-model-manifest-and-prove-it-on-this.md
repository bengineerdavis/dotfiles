---
id: TASK-44
title: Declare ollama/qwen3.5:9b in the model manifest and prove it on this
status: To Do
created_date: 2026-10-23 16:50
labels:
- migration
ordinal: 42
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
machine.** [author decision 2026-10-06, unclaimed] The opencode v2
  migration pins the trivial-task roles (title, summary, compaction) to
  `ollama/qwen3.5:9b` (see `dotfiles/docs/research/opencode-v2/PLAN.md`
  § Author rulings). House rules this task satisfies: a role pick is
  declared where it can be installed (apps/ollama manifest), and a model
  earns its place by measurement (quick eval on this box — titles,
  summaries, short-compaction cases are enough for this role, not the
  full suite). Includes the author-run `ollama pull qwen3.5:9b` (~6.6GB;
  check `ollama ps` for resident models first). Done when the tag is in
  the manifest, the eval numbers are recorded with their conditions, and
  the roles reference a model that is actually pullable on every machine
  the manifest targets.

Legacy: TASKS.md § Now item 42 of 49, migrated to backlog 2026-10-23 (branch agent/backlog-migration).
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
