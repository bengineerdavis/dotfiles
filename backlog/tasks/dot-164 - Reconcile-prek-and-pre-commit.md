---
id: DOT-164
title: Reconcile `prek` and `pre-commit`
status: Done
created_date: 2026-10-27 02:58
labels:
- planned
updated_date: 2026-11-08
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Reconcile `prek` and `pre-commit`. Both are installed and both read
  `.pre-commit-config.yaml`. Pick one as the documented runner so hooks cannot
  pass under one and fail under the other, and say which in AGENTS.md § Commands.

**Superseded 2026-11-08 by DOT-59** (author ruling): folded here — DOT-59 does
the migration to native `prek.toml` and retires pipx pre-commit, which is this
item's "pick one runner" outcome. Kept as the record; no separate work remains.
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
