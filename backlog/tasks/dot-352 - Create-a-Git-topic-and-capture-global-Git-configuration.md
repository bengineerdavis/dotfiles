---
id: DOT-352
title: Create a Git topic and capture global Git configuration
status: Done
created_date: 2026-11-12 02:54
assignee:
- OpenCode
labels:
- git
- configuration
priority: medium
orchestration:
  status_key: inprogress
  version: 5
  lease_owner: OpenCode git-topic session
  lease_expires_at: '2026-11-16T05:51:57.249327Z'
updated_date: 2026-11-19 21:28
documentation:
- https://github.com/bengineerdavis/dotfiles/pull/178
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Git's global configuration is chezmoi-managed, but no Git topic exists and its referenced commit-message template is missing.

Ship:

- Transfer Git package ownership from Homebrew and apt core prerequisites to a new app-tier Git topic on Darwin and Debian, keeping its package installation in the fleet prerequisites phase.
- Keep global Git settings, global excludes, and a commented commit-message template in chezmoi, with identity resolved from the existing name and email prompts.
- Update DOT-134 so its remaining git-ai and shell-integration scope does not claim Git configuration is unmanaged.
- Add tests for topic lifecycle wiring, package ownership and safe teardown, and the global commit-message template.

Constraints:

- chezmoi owns dotfiles; Ansible owns package presence.
- Do not add git-ai, change shell startup, or install telemetry.
- Do not apply the configuration or run the Ansible topic against the live machine.
- Use the canonical topical scaffold and prove each new test fails against a deliberately broken copy.

Agreed with the maintainer 2026-11-11: the Git topic owns both the package and configuration and remains part of fleet prerequisites.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Git package installation moves from Homebrew and apt core prerequisites into the Git topic's prerequisites phase, with OS-specific guards and system-role upgrades preserved.
- [x] #2 The Git topic declares Darwin and Debian support and has lifecycle wiring tests, including remove only under explicit removal.
- [x] #3 chezmoi manages the existing global Git config, global excludes, and a commit-message template whose guidance is entirely commented.
- [x] #4 Rendered Git identity accepts the existing chezmoi identity data rather than a hard-coded machine-specific identity.
- [x] #5 DOT-134 describes only the remaining git-ai and shell-integration work and no longer says Git configuration is unmanaged.
- [x] #6 Git teardown is opt-in, skips while another topic requires Git, and skips when the dependency index is unavailable; both safe-removal directions have tests.
- [x] #7 The topic and template tests pass, and each new test has been observed failing against a deliberately broken copy.
- [x] #8 uv run --frozen pytest tests/chezmoi tests/topics -q completes with only the 12 pre-existing OpenCode template failures.
- [x] #9 skillet validate . exits 0 with no errors.
- [x] #10 General dependency-aware scheduling orders each existing tier with declared providers before consumers, keeps stable relative order for independent topics, and fails with topic names on cycles.
- [x] #11 uv run --frozen pytest tests/topic_resolution -q passes; the scheduler's ordering and cycle tests have each been observed failing against deliberately broken copies.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
Package transfer approved by the maintainer 2026-11-11. topical new git --os Darwin --os Debian --manager homebrew_formula --manager apt --repo <checkout>/home --into <checkout>/home/dotfiles generated the canonical scaffold. The default --repo <checkout> invocation failed because the tool expects the legacy dotfiles/ location rather than the current home/dotfiles layout; no files were created by that failed invocation. The emitted install/remove manager blocks both targeted Darwin and Debian; the topic must guard Homebrew to Darwin and apt to Debian before use.
Maintainer chose general dependency-aware scheduling rather than a Git-only app-tier exception on 2026-11-15. Existing tier precedence stays unchanged; ordering is by declared providers within each tier, alphabetical for ties. The existing topic-resolution role is the single scheduling interface.
Verification on the final task tree, macOS: 29 focused tests passed (topic_resolution, Git config and topic, with Hypothesis); full tests+tools run 1661 passed, 14 failed, 6 skipped. The 12 OpenCode and 2 Lore failures also occur against the unchanged base. ansible-playbook syntax-check passes for apps/git/playbook.yaml and the parent playbook. ruff check and format --check pass on touched Python tests; skillet validate . exits 0; git diff --check exits 0.

Mutations observed sequentially and restored byte-for-byte: an uncommented commit-template line creates a real message; replacing the Git identity expression with a literal fails the identity test; a wrong Homebrew OS guard fails the package test; disabling the missing-index removal guard permits the unsafe path; removing scheduler progress fails the stable-order test; disabling the final cycle assertion makes the cycle test pass incorrectly. Exact failure node tests/topic_resolution/test_ordering.py::test_dependency_cycle_fails_with_every_remaining_topic is also asserted for the named Dependency cycle among topics: first, second message.

Not performed: no chezmoi apply, no live package install/removal, no live playbook convergence, no fresh Debian VM run, no push or merge. The removal-relenting test substitutes a temporary fail-if-called module in a copy of remove.yaml, so no package was removed. The commit-template test initializes only a temporary repository.

Review split: stable dependency scheduling in one commit; Git package ownership and global configuration capture in a following commit. The Git topic consumes the scheduling behavior, so they remain on the same task branch but can be reviewed separately.
Close-out on 2026-11-18: the earlier not-performed note described pre-merge verification. PR #178 has since merged, and the author applied only its reviewed chezmoi targets. The deployed commit-message template, global excludes, and Git topic were verified; unrelated Claude settings and the OpenCode retirement script were not applied. No Ansible convergence or live package change was performed. Queue-wrap-up on 2026-11-19: the stale remote task record did not contain the local merged close-out. This preserves the merged task outcome while leaving other sessions unpublished history on the shared main checkout untouched.
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
PR #178 merged on 2026-11-18: Git package ownership moved to the app-tier git topic on Darwin and Debian, global excludes and a commented commit-message template are chezmoi-managed, and topic scheduling orders providers before consumers within each tier. The scoped configuration deployment is verified; no Ansible convergence or package installation/removal ran. Final verification: 216 tests in tests/chezmoi and tests/topics passed, 15 tests in tests/topic_resolution passed, and skillet validate . exited 0. Mutation evidence is recorded in commits 648caeb9 and 95d10905. Debian convergence was not performed.
<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->

## Run History
<!-- SECTION:RUN_HISTORY:BEGIN -->
<!-- RUN_HISTORY_ENTRY:BEGIN -->
```yaml
event_id: run-72f203d3cd364e90b33f1551ed924c04
type: claim_task
actor: OpenCode git-topic session
timestamp: '2026-11-12T03:10:44.271261Z'
result: succeeded
task_id: DOT-352
from_status: todo
to_status: inprogress
metadata:
  lease_ttl_seconds: '3600'
```
Implement the authorized Git topic and global configuration capture.
<!-- RUN_HISTORY_ENTRY:END -->
<!-- RUN_HISTORY_ENTRY:BEGIN -->
```yaml
event_id: run-e7a55d6d2386477c853c126f35d90de1
type: release_task
actor: OpenCode git-topic session
timestamp: '2026-11-12T22:13:57.987020Z'
result: succeeded
task_id: DOT-352
from_status: inprogress
to_status: todo
```
<!-- RUN_HISTORY_ENTRY:END -->
<!-- RUN_HISTORY_ENTRY:BEGIN -->
```yaml
event_id: run-35eb3fec4b93486b926c47481f8d0980
type: claim_task
actor: OpenCode git-topic session
timestamp: '2026-11-12T22:14:08.282429Z'
result: succeeded
task_id: DOT-352
from_status: todo
to_status: inprogress
metadata:
  lease_ttl_seconds: '3600'
```
Resume the authorized implementation after releasing the expired lease.
<!-- RUN_HISTORY_ENTRY:END -->
<!-- RUN_HISTORY_ENTRY:BEGIN -->
```yaml
event_id: run-655251b6bf1947cd8300f19347af0d5d
type: release_task
actor: OpenCode git-topic session
timestamp: '2026-11-16T04:51:56.743697Z'
result: succeeded
task_id: DOT-352
from_status: inprogress
to_status: todo
```
<!-- RUN_HISTORY_ENTRY:END -->
<!-- RUN_HISTORY_ENTRY:BEGIN -->
```yaml
event_id: run-6f513576e0f5451898092936703a0e25
type: claim_task
actor: OpenCode git-topic session
timestamp: '2026-11-16T04:51:57.249797Z'
result: succeeded
task_id: DOT-352
from_status: todo
to_status: inprogress
metadata:
  lease_ttl_seconds: '3600'
```
Renew the same writer's expired lease for the approved dependency-aware scheduler and Git topic.
<!-- RUN_HISTORY_ENTRY:END -->
<!-- SECTION:RUN_HISTORY:END -->
