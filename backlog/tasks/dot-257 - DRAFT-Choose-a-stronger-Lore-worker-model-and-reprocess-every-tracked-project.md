---
id: DOT-257
title: 'DRAFT: Choose a stronger Lore worker model and reprocess every tracked project'
status: To Do
created_date: 2026-10-28 17:16
labels:
- loreai
- models
- design
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The maintainer wants a more capable Lore background worker model than the current low-cost choice, optimizing for the quality/cost Pareto frontier rather than minimum price. This is a follow-up design/implementation task, separate from the gateway-service PR.

Use Lore's documented model roles and evaluation path:
- Distillation, curation, and query expansion share the worker model. Curation is the quality-critical structured-write workload.
- Local-inference guidance says small models can distill, but full curation parity needs 32B+ at Q4 or better. A local candidate below that floor must not silently replace the hosted worker.
- The documented override is LORE_WORKER_MODEL, with LORE_WORKER_API_KEY/LORE_WORKER_UPSTREAM for a separate worker provider. Use the supported config mechanism; do not confuse this with OpenCode's small_model/title agent.
- The topic's candidate list is a set of starting candidates, not measured endorsements. Re-evaluate with representative distillation/curation/query-expansion cases and the existing model-benchmark approach, recording exact IDs, structured-output validity, duplicate/unsupported-knowledge rates, latency, context limits, and measured cost. Do not invent ratings or rely on parameter count alone.
- Decide explicitly whether the OpenCode small_model/title role should remain separate. It is not part of the Lore worker-model decision.

Reprocessing scope: all projects tracked by Lore, not only the current checkout. Before changing any production artifacts, back up the database and public exports, and verify a restore path. Determine whether Lore's supported import/recovery path can reprocess already-recorded sessions or only imports not previously seen. Do not use Cancelled. as a migration step. If reprocessing existing sessions is unsupported, stop and route the required upstream capability/request to BYK/loreai rather than implementing a migration in this dotfiles repo.

Design a bounded, resumable migration with a dry run and per-project progress. Stage it: backup, model evaluation, one canary project, comparison of old/new knowledge artifacts, explicit acceptance, then the remaining projects. Respect API budgets, local model memory, and the per-machine execution budget. A model/config version marker and explicit reprocessing policy should make future upgrades repeatable without reprocessing every session on every topic run. Preserve unrelated projects and current sessions during the migration. The task needs maintainer approval for model/provider, cost ceiling, migration mechanism, and when background execution may run.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A documented evaluation selects a worker model on measured curation quality and cost, including Lore's 32B+ Q4 local floor and exact supported model IDs.
- [ ] #2 The OpenCode small-model/title role remains a separately decided setting, not silently coupled to the Lore worker model.
- [ ] #3 A dry run enumerates every tracked project, estimates work/cost, and proves which existing sessions can be reprocessed through supported Lore interfaces.
- [ ] #4 Database and public knowledge exports are backed up and a restore is verified before any production migration.
- [ ] #5 A canary migration compares old and new artifacts and requires explicit acceptance before fleet-wide processing.
- [ ] #6 Reprocessing is bounded, resumable, observable per project, and preserves unrelated data and in-flight sessions.
- [ ] #7 A versioned reprocessing policy prevents repeated fleet-wide work on every topic run and defines how future model/config upgrades trigger migration.
- [ ] #8 Unsupported Lore migration behavior is reported upstream rather than replaced by a bespoke dotfiles implementation.
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
