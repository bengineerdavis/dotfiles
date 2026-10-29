---
id: DOT-220
title: Make docs repo-only by relocating them out of the payload
status: To Do
created_date: 2026-10-27 02:59
labels:
- planned
- group:refactor-b-factor-the-ai-llm-tooling-out-of-this-repo
updated_date: 2026-10-29 03:21
orchestration:
  status_key: inprogress
  lease_owner: opencode-payload-migration
  lease_expires_at: '2026-10-29T04:21:34.591464Z'
  version: 1
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Make docs repo-only by relocating them out of the payload.** [decision
  2026-10-03: docs are excluded from provisioned files; ROADMAP "Docs
  excluded from provisioned files"] `git mv dotfiles/docs/*` into root
  `docs/`, reconciling the two ARCHITECTURE.md and two USAGE.md copies —
  the maintained `dotfiles/docs/` content wins where the copies differ,
  root `docs/` becomes the one docs tree — and update every citation
  (~39 topic files cite `dotfiles/docs/TOPICS.md`; AGENTS.md, spec.md,
  CONTRIBUTING.md, ROADMAP-topic-cli). Root `docs/ARCHITECTURE.md`,
  `docs/USAGE.md` and `RESOURCES.md` drop out of `chezmoi managed` here or
  at the payload move, whichever lands first. Done when: nothing remains
  under `dotfiles/docs/`; `chezmoi managed` lists no docs path; doc-link/
  doc-integrity tests and skillet green; AGENTS.md § What this repo is
  points at root `docs/`. Lands before the payload move so that move
  carries no docs; the move item inherits a smaller tree. [unclaimed]
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
2026-10-28 author approved sequential migration after preserving DOT-265. This session will use branch agent/docs-relocate and worktree .worktrees/docs-relocate, then proceed to DOT-222. The maintained dotfiles/docs content wins on conflicting copies; root docs becomes the only maintained tree. Preserve the Vagrant and Lima branches for later rebase; do not merge or discard them here.
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
event_id: run-3af8f8f5308a40cc83619202aad4202b
type: claim_task
actor: opencode-payload-migration
timestamp: '2026-10-29T03:21:34.591533Z'
result: succeeded
task_id: DOT-220
from_status: todo
to_status: inprogress
metadata:
  lease_ttl_seconds: '3600'
```
<!-- RUN_HISTORY_ENTRY:END -->
<!-- RUN_HISTORY_ENTRY:BEGIN -->
```yaml
event_id: run-4c2abac5a3c34d3689f200a8a513ca52
type: record_run
actor: opencode-payload-migration
timestamp: '2026-10-29T03:36:20.098244Z'
result: succeeded
task_id: DOT-220
files:
- docs/README.md
- AGENTS.md
verification:
- 'uv run --frozen --with pytest-xdist pytest tests tools -q -n auto --dist worksteal:
  1163 passed, 6 skipped'
```
Consolidated maintained documentation into root docs, updated live references, repository-only deployment contract; 1163 tests passed, skillet valid, commit 28c9d16 on agent/docs-relocate pushed.
<!-- RUN_HISTORY_ENTRY:END -->
<!-- SECTION:RUN_HISTORY:END -->
