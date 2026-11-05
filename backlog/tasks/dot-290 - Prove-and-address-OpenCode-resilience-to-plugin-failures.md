---
id: DOT-290
title: Prove and address OpenCode resilience to plugin failures
status: To Do
created_date: 2026-11-01 16:43
labels:
- opencode
- design
- upstream
priority: high
assignee:
- opencode-resilience-worker
updated_date: 2026-11-01 16:46
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Author clarification 2026-11-01: Lore is intended to become required memory infrastructure. The larger immediate friction is the possibility that OpenCode cannot work when a plugin fails. Investigate this as a host limitation, not a reason to make Lore optional. First empirically distinguish load failure, hook failure, provider-routing failure, and total host-agent failure in isolated OpenCode state; the existing evidence proves V1 export rejection, not necessarily total agent failure. Review current OpenCode V2 plugin loader and supported recovery behavior. If a host change is needed, route it to a fork and PR against the author's OpenCode fork for review; do not contact upstream without separate authorization. Keep DOT-282 scoped to restoring required Lore integration. No live host configuration changes or destructive tests.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 An isolated reproduction names the failure paths that prevent normal agent use and those that merely disable plugin features.
- [ ] #2 The design records a supported recovery/failure-containment path without permanently bypassing required Lore memory integration.
- [ ] #3 Any required host fix has an authorized fork home and independently reviewable acceptance tests; no upstream submission occurs without approval.
- [ ] #4 Existing plugin-management commands and current upstream issues/PRs are checked and cited before a duplicate feature is proposed.
- [ ] #5 If no conflicting active work exists, a fork branch implements a minimal failure-recovery mechanism with session-scoped and explicit persistent-disable choices, fail-closed defaults, and regression tests.
- [ ] #6 A substantive PR targeting the author's OpenCode fork reports evidence, limitations, and remaining upstream questions; nothing is merged or submitted upstream automatically.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
Author-authorized execution 2026-11-01: use a local fork of the current OpenCode V2 tooling, with one isolated worktree/branch. Before implementing, challenge the failure presumption empirically and inventory existing plugin commands/config and upstream issues/PRs. Desired feature request, if not already present or actively implemented: when a plugin fails, explain the failure and let the user interactively disable it for the current session or persistently via CLI/global configuration. Do not silently disable required memory infrastructure; distinguish load-time, initialization, hook, and provider-routing failures. If active upstream work covers the need, report and use that instead. Otherwise create/find the appropriate issue in the author's fork and build a reviewable proof/fix on a fork branch, with tests and a PR for author review. No live host config, no upstream submission, and no merge. Lore V2 restoration remains DOT-282's separate scope.
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->
