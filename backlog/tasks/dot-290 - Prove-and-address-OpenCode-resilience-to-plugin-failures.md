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
orchestration:
  status_key: todo
  version: 3
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

AC #4 inventory 2026-11-01 (before any fork work):
- Host on this machine: opencode v2.2.2 (brew). Native plugin CLI: `opencode plugin list|add|check|update|remove` (add installs from npm/git and appends to global config; remove removes from global config). No `disable`/`enable` subcommand; no documented per-plugin skip flag.
- Live containment state: `~/.config/opencode/opencode.jsonc` has the Lore plugin commented out (`"plugin": ["// @loreai/opencode"]`) — the only current recovery path is hand-editing config (no CLI support), which is exactly the gap DOT-290 targets.
- Former worker proposed ~/code/forks/loreai, worktree .worktrees/dot-290-plugin-resilience and branch agent/dot-290-plugin-resilience. Reconciliation found the actual worktree still named dot-284-plugin-resilience, on agent/dot-284-plugin-resilience, empty at 3b48e546. The fork's plugin package targets @opencode-ai/plugin >=1.1.0; internal helpers are kept out of its entry module because the legacy loader invokes every exported function as a plugin.
- Upstream issues found (2026-11-01 websearch; verify against the current org — results showed both sst/opencode and anomalyco/opencode):
  - anomalyco/opencode#26645 — "feat: add plugin availability/health check mechanism": clear errors when a plugin fails to load (missing deps, version mismatch, invalid path). Directly overlaps AC #1/#2 — review before proposing a duplicate.
  - anomalyco/opencode#24847 — "OpenCode silently enters a broken UI state when a plugin fails"; workaround: hand-remove plugin entries from the config array. Same gap, confirmed by other users.
  - anomalyco/opencode#33455 — "Plugins from config plugin array silently not loaded since v1.17.0": silent-skip failure mode (opposite of a hard failure but part of the same observability problem).
  - sst/opencode#3392 — "[bug] Add scoped npm package as plugin shows error": adding a scoped npm plugin prevents opencode from starting at all (total host failure mode).
- Next: AC #1/#5 isolated reproduction — four failure modes (schema/load-time rejection, initialization throw, hook dispatch error, provider-routing failure) each in an isolated OpenCode state dir, recording which stop agent use.
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
event_id: run-18ab45588c8e46029bb3a45481f946e8
type: claim_task
actor: opencode-resilience-worker
timestamp: '2026-11-01T16:46:33.708100Z'
result: succeeded
task_id: DOT-290
from_status: todo
to_status: inprogress
metadata:
  lease_ttl_seconds: '3600'
```
<!-- RUN_HISTORY_ENTRY:END -->
<!-- RUN_HISTORY_ENTRY:BEGIN -->
```yaml
event_id: run-82c111a7f768446f91d9ebf1c3351a49
type: release_task
actor: opencode-resilience-worker
timestamp: '2026-11-01T19:04:55.863984Z'
result: succeeded
task_id: DOT-290
from_status: inprogress
to_status: todo
```
Lease expired 17:46Z; re-claimed under a machine-qualified actor
<!-- RUN_HISTORY_ENTRY:END -->
<!-- RUN_HISTORY_ENTRY:BEGIN -->
```yaml
event_id: run-62c99a2ab6cd4bada413878e252faca9
type: claim_task
actor: ben@the-mac
timestamp: '2026-11-01T19:04:56.455358Z'
result: succeeded
task_id: DOT-290
from_status: todo
to_status: inprogress
metadata:
  lease_ttl_seconds: '3600'
```
Continue DOT-290: fork branch, isolated plugin-failure reproduction, fork PR for author review
<!-- RUN_HISTORY_ENTRY:END -->
<!-- SECTION:RUN_HISTORY:END -->

Recovery reconciliation 2026-11-04: the named fork worktree and branch are empty at 3b48e546; no implementation was committed. The former claim expired, so this record is unclaimed evidence, not an active-work declaration.
