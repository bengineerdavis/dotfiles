---
id: DOT-348
title: Install the ADHD skills globally through dotagents
status: Done
created_date: 2026-11-10 20:55
assignee:
  - opencode-dotagents-adhd
orchestration:
  status_key: todo
  version: 2
updated_date: 2026-11-19 20:56
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

Author rulings 2026-11-15: exclude Copilot for i-have-adhd only, retaining it globally; OpenCode skill-only. DOT-349 owns the native OpenCode setup hook and slash command.

MERGED 2026-11-19: PR #188 (merge commit f867d548). Both ADHD sources + hardened plugin-targets.yaml live on origin/main. roborev jobs 142/143 all findings resolved and closed. Branch agent/dot-348 + worktrees retired. DOT-348 marked Done in local commit 9ec504a.

RECONCILED 2026-11-20: the DOT-343 session completed its shared-main merge (4c4289f5 and 9d0f3aae) and pushed main. Local main is in sync with origin/main, with no unmerged paths. The closure commit 9ec504a remains in history. The task handoff and retro were preserved and are committed separately.

LIVE INSTALL (not verified): no chezmoi apply or dotagents role run was performed by this session. The author can review drift with chezmoi status and czd, then run 'bash home/dotfiles/executable_run-role.sh dotagents' from main. Verify ~/.agents/skills/adhd and the OpenCode i-have-adhd skill link afterward. Always-on injection stays opt-in.

DOT-349 (native OpenCode adapter: .opencode setup hook + /i-have-adhd command + teardown) remains the queued follow-up — separate task, separate session.

Retrospective: changelog.d/20261119_130000_retro_dot348_adhd_skills.md. The final wrap-up records are committed on main; other sessions' dirty files remain untouched.

<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

Merged via PR #188 (merge commit f867d548) on 2026-11-19. Both ADHD sources live on origin/main; plugin-targets.yaml hardened per roborev jobs 142/143 (all findings resolved, reviews closed). Branch agent/dot-348 and worktrees retired. Live install still pending: author runs chezmoi apply from main, then bash home/dotfiles/executable_run-role.sh dotagents. DOT-349 (native OpenCode adapter) remains the queued follow-up.

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

<!-- RUN_HISTORY_ENTRY:BEGIN -->

```yaml
event_id: run-8eb30be3d62d406e8d8c1747aa00ff63
type: record_run
actor: opencode-dotagents-adhd
timestamp: '2026-11-17T17:25:05.340223Z'
result: succeeded
task_id: DOT-348
files:
- home/dotfiles/apps/dotagents/defaults/main.yaml
- home/dotfiles/apps/dotagents/tasks/plugin-targets.yaml
- home/dotfiles/apps/dotagents/tasks/install.yaml
- home/dotfiles/apps/dotagents/tasks/remove.yaml
- home/dotfiles/apps/dotagents/README.md
- home/dotfiles/apps/dotagents/CHANGELOG.md
- docs/TOPICS.md
- tests/topics/test_dotagents_sources.py
verification:
- Focused 87 passed; CI shape 7 passed 2 skipped; full-suite parity 14 identical failures
  at base 748ddc9d and branch, zero regressions
```

Committed the disclosed implementation as cdf7bc6e and made the two ansible-dependent tests CI-safe.

<!-- RUN_HISTORY_ENTRY:END -->

<!-- RUN_HISTORY_ENTRY:BEGIN -->

```yaml
event_id: run-4bc80a8e1e8b476db37677549c8d528b
type: record_run
actor: opencode-dotagents-adhd
timestamp: '2026-11-17T18:28:30.025470Z'
result: succeeded
task_id: DOT-348
verification:
- 9 passed with real ansible-playbook 2.21.6; 7 passed 2 skipped in the CI shape with
  no ansible; full-suite parity 14 identical failures at base 748ddc9d and branch
```

Re-verified all nine focused tests against the machine's restored ansible (core 2.21.6), not only a shim.

<!-- RUN_HISTORY_ENTRY:END -->

<!-- RUN_HISTORY_ENTRY:BEGIN -->

```yaml
event_id: run-d6c5c71128b04a53bacb5a9d669d7a09
type: record_run
actor: opencode-dotagents-adhd
timestamp: '2026-11-18T03:04:28.647424Z'
result: succeeded
task_id: DOT-348
verification:
- 14 focused tests pass with real ansible 2.21.6; CI shape 10 passed 4 skipped; ruff
  clean; pyrefly 0 errors; trees confirmed identical before reset
```

Branch agent/dot-348 pushed and in sync at 9e4c7585; no PR yet. A concurrent session shared this branch; reset to the identical remote tree to avoid a force-push.

<!-- RUN_HISTORY_ENTRY:END -->

<!-- RUN_HISTORY_ENTRY:BEGIN -->

```yaml
event_id: run-d0b15ca7f3df49c2a6ee78d889b41deb
type: record_run
actor: opencode-dotagents-adhd
timestamp: '2026-11-18T03:17:13.736793Z'
result: succeeded
task_id: DOT-348
verification:
- 'gh pr view 184: state OPEN, mergeable MERGEABLE, mergeStateStatus UNSTABLE (CI
  running)'
```

Opened PR #184 for agent/dot-348 at 9e4c7585; mergeable, CI pending. Merge stays with the author after the design quiz.

<!-- RUN_HISTORY_ENTRY:END -->

<!-- SECTION:RUN_HISTORY:END -->
