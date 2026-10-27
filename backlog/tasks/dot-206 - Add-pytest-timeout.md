---
id: DOT-206
title: Add `pytest-timeout`
status: To Do
created_date: 2026-10-27 02:59
labels:
- planned
- group:refactor-b-factor-the-ai-llm-tooling-out-of-this-repo
updated_date: 2026-10-27 22:22
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add `pytest-timeout`. Formalizes the ad hoc `timeout N` wrapping AGENTS.md
  already documents as a lesson (a cold model load can exceed a short
  timeout and cascade into every subsequent run failing) — a per-test
  timeout marker on anything that shells out to a model makes the failure
  mode a named, bounded one instead of an open-ended hang. `pytest-cov`,
  `pytest-mock`, `pytest-env` researched and not adopted the same pass:
  `pytest-mock` is a convenience wrapper this repo's consistent
  `monkeypatch` usage doesn't need; `pytest-env` sets static config-file
  values and can't supply the *dynamic*, per-test `tmp_path`-derived paths
  the `$HOME`-sandbox fixture (above) requires. `pytest-rerunfailures`
  researched and explicitly rejected as a default: auto-rerun-until-green
  is the same shape as this repo's dominant failure mode (tests passing
  while testing nothing) — a test that passes on retry is evidence to
  investigate, not noise to suppress. If ever adopted, scope it to named
  environmental flakes only.
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
