---
id: DOT-107
title: 'Topic: install topical (the A9 generator) as a first-class tool'
status: To Do
created_date: 2026-10-27 02:56
labels:
- now
priority: high
updated_date: 2026-10-27 22:21
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Topic: install topical (the A9 generator) as a first-class tool.**
  [agent: topical-install / OpenCode — worktree `.worktrees/topical-install`,
  branch `agent/topical-install`] Thin `apps/topical` topic: install the
  topical CLI as a **uv tool** from the git remote (author's distribution
  decision, 2026-10-21: a Python CLI tool via pip — uvx/uv tool on this
  machine; PyPI later, the bare name is taken there by a dormant package).
  The topic owns presence (`uv tool install`), currency (`uv tool upgrade`
  — no system role reaches uv tools) and teardown (`uv tool uninstall`).
  `topic_requires: [uv]`. Scaffolded by `topical new` itself (dogfooding
  the no-manager path). Done when the topic is syntax-clean, `--check
  --tags provision` is green against the machine's real state, and the
  author has applied it — the install is machine state, so the live apply
  is the author's step after merge.
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
