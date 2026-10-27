---
id: TASK-133
title: Verify and evaluate Caliber (`caliber-ai-org/ai-setup`) as an agent-config
  generator
status: To Do
created_date: 2026-10-27 02:57
labels:
- planned
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Verify and evaluate Caliber (`caliber-ai-org/ai-setup`) as an
  agent-config generator.** Lead from the author's research capture,
  2026-09-14, raw paste preserved at
  `~/code/personal/llocallabs-capture/2026-09-14-caliber-ai-setup.md`: a
  MIT-licensed CLI that scans a codebase locally and generates agent config
  files (AGENTS.md, .cursor/rules, CLAUDE.md), claiming a generic mode,
  BYO-key deep generation, and opencode/dotagents compatibility. The
  capture is an AI-generated summary — **UNVERIFIED**, and the
  load-bearing claims are exactly what `review-best-practices` exists to
  check: the local-vs-API split, the npm scope (`@rely-ai/caliber` in the
  paste vs `caliber-ai-org` on GitHub — one is wrong), the claimed
  `.skill.md` export for dotagents, and — decisive for this repo — whether
  it overwrites or respects an existing hand-maintained AGENTS.md, which
  would disqualify it here while leaving llocallabs's scaffold as a
  legitimate consumer. Second capture, same day: the npm scope is explained
  as the **for-profit entity behind the tool** (`@rely-ai`, enterprise
  portal at trycaliber.ai with a sales desk) — so the scope mismatch is an
  open-core-trajectory question to track, not just a typo; `caliber
  refresh` drift protection via pre-commit hooks and MCP recommendations
  are further claims to check. **[verified 2026-09-14 via `gh api`: MIT,
  not archived, but last push 2026-07-26 — ~7 weeks stale by the 30–45-day
  maintainership criterion.]** Coupling: the general copier template queued
  below generates the same class of files, so this evaluation answers for
  both. Done when the claims are checked against the actual repo, a
  use/don't-use decision is recorded with the author, and any adoption is
  queued as tasks. [me]
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
