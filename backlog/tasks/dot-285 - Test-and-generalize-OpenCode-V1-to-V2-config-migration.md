---
id: DOT-285
title: Test and generalize OpenCode V1-to-V2 config migration
status: To Do
created_date: 2026-11-04 21:58
dependencies:
- DOT-274
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Build a verified migration matrix for users arriving from OpenCode V1, separate from DOT-274 immediate JSONC cleanup. Cover JSON-to-JSONC, JSONC-to-JSON, and V1-to-V2 settings migration; research upstream OpenCode and LoreAI migration reports before fixing expectations. The surviving global format is JSONC per author ruling 2026-11-04; reverse conversion is a diagnostic/export scenario, not permission to leave two competing global files. Include malformed JSON/JSONC, comments and trailing commas, empty or partial files, missing provider/model/plugin settings, provider baseURL overrides, credential references, project-level config, and service processes retaining old config. Test both clean installs and upgrades from real V1 state on supported platforms in isolated VMs. Require backup-before-mutation and no credential or machine-local data loss. Turn the resulting upstream-case inventory, old-state fixtures, mutation tests, failure-preservation checks, idempotence checks, and post-migration runtime checks into a reusable BDD/TDD migration pattern for new and refactored topics.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Record a source-backed V1-to-V2 and JSON/JSONC behavior matrix with upstream issue references and versions
- [ ] #2 Exercise JSON-to-JSONC and JSONC-to-JSON conversion in isolated fixtures without leaving competing active global configs
- [ ] #3 Cover malformed, commented, empty, partial, and missing-field configs; plugin and provider migration; credential preservation; and stale service reload behavior
- [ ] #4 Run real V1-to-V2 upgrade scenarios in disposable VMs on supported platforms, with failure-preservation and idempotence checks
- [ ] #5 Document and test a reusable topic migration-testing recipe, with a second topic demonstrating the pattern
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
