---
id: DOT-348
title: Install the ADHD skills globally through dotagents
status: To Do
created_date: 2026-11-10 20:55
assignee:
- opencode-dotagents-adhd
orchestration:
  status_key: todo
  version: 2
updated_date: 2026-11-16 04:36
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Neither requested skill is installed or declared, although dotagents 3.4.0 is the machine's global skill manager. The author approved installing both upstream sources directly and recording verified integration corrections with the topic.

Ship:

- Add UditAkhourii/adhd and ayghri/i-have-adhd to dotagents_sources with reviewable trust and licence evidence.
- Record verified plugin discovery, OpenCode projection, and native-adapter limits in the dotagents topic docs, including correction of the stale opencode-only claim.
- Extend docs/TOPICS.md so verified topic-specific corrections and current upstream references stay with each topic for future maintainers and topic skills.

Constraints:

- Do not fork either upstream project for the core skill install.
- Do not install i-have-adhd's OpenCode command, plugin hook, or always-on flag in this task; those belong to the queued follow-up.
- Deployed-tree changes require a branch, PR, and human review. Do not run chezmoi apply or mutate the live agent configuration.
- Leave other sessions' queue and worktree changes untouched.

Decision record: Approved by the author 2026-11-10: upstream dotagents sources now; native OpenCode adapter and upstream documentation work queued separately.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Both approved upstream sources are declared in dotagents_sources with verified licence and trust rationale.
- [x] #2 The dotagents topic docs distinguish verified behavior from untested projections and no longer claim plugin sources are opencode-only.
- [x] #3 docs/TOPICS.md requires topic-specific corrections and authoritative references to live with the topic.
- [x] #4 New or changed tests have been seen to fail against the unfixed tree, with Mutation and Failing-test trailers on the implementation commit.
- [x] #5 Focused tests, documentation integrity checks, and skillet validation pass on the implementation branch.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Implemented: both source approvals, one predeclared target block, matching gated teardown, topic corrections, and the general topic-knowledge convention. The projection test uses real role defaults and proves valid TOML, foreign-declaration preservation, idempotency, empty-list safety, and targeted removal. No live configuration changed.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
Author rulings 2026-11-15: exclude Copilot for i-have-adhd only, retaining it globally; keep OpenCode skill-only in A. DOT-349 owns the native OpenCode setup hook and slash command.

Isolated dotagents 3.4.0 verification: both sources classify as plugins. UditAkhourii/adhd installs its canonical skill and OpenCode link. i-have-adhd rejects Copilot because hooks/hooks.json is unsupported there. A predeclared targets list excludes only Copilot.

The first combined test exposed a real ordering defect: add appends a declaration if the target block is absent. Predeclaring targeted plugins fixes this. Two actual dotagents refresh cycles preserve targets without a duplicate. The second projection is idempotent. OpenCode gets the canonical skill without the deferred .opencode setup hook or command.

Focused checks: 87 passed across the source, tag, and guard suites. Documentation links, ruff, formatting, skillet validation, and Ansible syntax pass. The broader docs run found two existing lore-preservation failures; neither anchor is present at the branch base or current main. Live installation is not done and requires merge and author-approved application.
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
event_id: run-368ef661bac0405f824f1de815ef97bb
type: claim_task
actor: opencode-dotagents-adhd
timestamp: '2026-11-12T22:10:09.706869Z'
result: succeeded
task_id: DOT-348
from_status: todo
to_status: inprogress
metadata:
  lease_ttl_seconds: '3600'
```
Worktree .worktrees/dot-348 on branch agent/dot-348; author approved A on 2026-11-10 and directed durable topic-doc corrections.
<!-- RUN_HISTORY_ENTRY:END -->
<!-- RUN_HISTORY_ENTRY:BEGIN -->
```yaml
event_id: run-4b388111827e432da8e21ab2573761dc
type: release_task
actor: opencode-dotagents-adhd
timestamp: '2026-11-16T04:36:32.086062Z'
result: succeeded
task_id: DOT-348
from_status: inprogress
to_status: todo
```
Implementation and isolated verification are ready for PR review. Releasing this session's stale lease; task remains open for merge and author-approved application.
<!-- RUN_HISTORY_ENTRY:END -->
<!-- SECTION:RUN_HISTORY:END -->
