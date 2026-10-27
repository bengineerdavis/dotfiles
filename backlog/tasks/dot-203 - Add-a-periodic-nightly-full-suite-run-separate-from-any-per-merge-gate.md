---
id: DOT-203
title: Add a periodic (nightly) full-suite run, separate from any per-merge gate
status: To Do
created_date: 2026-10-27 02:59
labels:
- planned
- group:refactor-b-factor-the-ai-llm-tooling-out-of-this-repo
updated_date: 2026-10-27 22:22
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Add a periodic (nightly) full-suite run, separate from any per-merge
  gate.** Settled with the author and a fusion council 2026-09-22, deciding
  decision 5 (minimum gate set per task class): a merge gate proves *this
  change* didn't break anything; it says nothing about whether the trunk
  was already broken, and that's a different job — one this repo has no
  mechanism for today (no CI service). Per-environment, matching existing
  precedent (`apps/ollama` installs a launchd agent, `apps/clamav` a
  systemd timer — new unit, not a new mechanism): a launchd agent on
  Darwin, a systemd timer on Debian, running the documented full-suite
  command and reporting failures somewhere the author will actually see
  them. Done when one machine has the timer installed, a deliberately
  broken test is shown to be caught by a scheduled run rather than only by
  a merge, and the report mechanism is named (not just "runs and logs to a
  file nobody reads").
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
