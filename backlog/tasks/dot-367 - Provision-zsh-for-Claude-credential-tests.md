---
id: DOT-367
title: Provision zsh for Claude credential tests
status: In Progress
created_date: 2026-11-16 05:36
updated_date: 2026-11-19 22:31
orchestration:
  status_key: todo
  version: 2
assignee:
- ci-credential-session
references:
- https://github.com/bengineerdavis/dotfiles/pull/185
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Ubuntu CI fails six Claude credential tests because their real-shell harness assumes a macOS zsh path. The official runner image has no zsh package.

Ship:

- Resolve zsh on the test PATH instead of assuming its macOS location.
- Install zsh as an explicit CI prerequisite.
- Keep the existing real-zsh and fake-Claude invocation seam unchanged.

Constraints:

- Do not skip the tests on Ubuntu, replace zsh with bash, or access provider credentials.
- Test the helper at its public invoke seam with an isolated PATH.
- Do not edit deployed configuration or run chezmoi apply.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 A PATH containing only /usr/bin supplies a usable zsh to the invocation helper.
- [x] #2 The existing Claude profile tests still pass on macOS with their real zsh fragment and fake CLI.
- [x] #3 A deliberate /bin/zsh restoration fails the new PATH-resolution test.
- [x] #4 Focused pytest and ruff checks pass.
- [x] #5 CI installs zsh before the pytest step.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->
Final checks after type guard: 17 focused tests passed, ruff and formatting passed, pyrefly 0 errors, three mutation tests went red on intended assertions. Repair commit 2a9b9c7 has all applicable prek hooks passing. Ubuntu apt execution remains CI verification; no local apt or live-home mutation performed.
Wrap-up handoff (2026-11-19):

Repo: /Users/ben.davis/.local/share/chezmoi
Branch: agent/claude_credential_path
Worktree: /Users/ben.davis/.local/share/chezmoi/.worktrees/claude-credential-path
PR: #185 https://github.com/bengineerdavis/dotfiles/pull/185
Pushed head: 9b1dd984307683dc8272a401c67b19b1f6e36e3f
Implementation commits: d73b20208736c013f42525cc89daa05276003694 and 024014dc477f6e1ceb1b26832bea580401e5766a; subsequent commits merge the remote main-sync updates.

Owned implementation files: .github/workflows/tests.yml; tests/claude_credentials/claude_credentials_harness.py; tests/claude_credentials/test_harness.py; tests/scripts/test_ci_workflow.py; tests/merge_gates/test_real_managed.py; tests/chezmoi/test_gitconfig_tools.py; changelog.d/20261116_claude_credential_zsh.md. This task record is also updated here. Untracked .review-artifacts/ is session-local; it is not committed.

Checks actually run:
- Focused pytest: 30 passed.
- Ruff check and format on touched test files: passed.
- uv tool run --from pyrefly==1.3.2 pyrefly check: 0 errors.
- Full suite uv run --frozen pytest tests tools -q: 3 failed, 1738 passed, 6 skipped, 9 deselected in 527.29s. All three are DOT-305 lore-anchor failures; no CI-prerequisite failure remains.
- Isolated unconfigured-chezmoi probe: 3 passed, 7 skipped. A real configured machine still exercises the live-policy suite.
- Source-existence guard and checksum guard mutations failed the named tests.
- CI run 44621622426 is queued at 9b1dd984; its result is Not verified.
- Fresh roborev review job 164 is queued; its verdict is Not verified.

Remaining before merge:
1. Read job 164 and resolve actionable findings. Do not reintroduce the host-PATH fallback.
2. Verify the checksum-pinned archive install and the Tests check in CI run 44621622426.
3. DOT-314 owns the known-failure baseline update; do not edit it here or take over agent/retro-ci-guard. Current main baseline lacks the DOT-305 lore anchors, so CI may still report unexpected failures despite the repaired prerequisites.
4. Merge only with review findings resolved, required checks green, no conflicts, and the branch current with main. The repository quiz gate is unresolved: the earlier "A or C" answer was not a clean pass because A is the host-PATH fallback removed by this work.

Resume commands:
cd /Users/ben.davis/.local/share/chezmoi/.worktrees/claude-credential-path
git fetch origin main agent/claude_credential_path
git status --short --branch
git merge --no-edit origin/agent/claude_credential_path
git merge --no-edit origin/main
roborev job wait --job 164
gh pr checks 185

Retro: DOT-393 / PR #196 https://github.com/bengineerdavis/dotfiles/pull/196.
Foreign shared main checkout: mid-merge with uncommitted and staged changes belonging to other sessions. Do not commit, restore, reset, or clean it. A foreign DOT-392 collision was avoided by moving this session retro to DOT-393. No process or database cleanup was performed.
Wrap-up final update (2026-11-19 13:56 -0800):

Latest pushed head: 8db630f9906efaf5fb52049c9b3e87679a574d05.
Roborev job 164: PASS; no high or medium findings. Its low missing-gitconfig-skip-test finding is fixed by 8db630f9. Direct guard test: 4 passed normally, intended failure on the stderr-match mutation, 4 passed after restore. Full focused suite: 31 passed; ruff and format passed.

Job 164 did not inspect 8db630f9; a fresh review of that commit is Not verified. Latest CI result is Not verified. Previous CI run 44622666803 was still IN_PROGRESS when checked; do not treat it as green. PR #185 remains open and must not merge until its required tests check passes, current code is reviewed, the branch is current with main, and the repository quiz gate is satisfied.

Resume:
cd /Users/ben.davis/.local/share/chezmoi/.worktrees/claude-credential-path
git fetch origin main agent/claude_credential_path
git status --short --branch
git merge --no-edit origin/agent/claude_credential_path
git merge --no-edit origin/main
gh pr checks 185

Retro remains DOT-393 / PR #196. DOT-314 owns the baseline, DOT-305 owns lore corruption, DOT-386 owns wrong-project sessions. Shared main checkout remains mid-merge with foreign changes; leave it untouched.
Latest CI evidence (run 44623835378, 2026-11-19): 1 failed, 1639 passed, 109 skipped, 9 deselected in 298.12s. The checksum-pinned chezmoi install succeeded. The sole failure is tests/docs/test_lore_md_rules_survive.py::test_rule_survives_redistillation[uv --frozen], absent from the known-failure baseline owned by DOT-314. Merge authorization was given, but the required check remains red; do not merge until DOT-314 baseline resolution or the lore repair makes it green. PR #185 remains open at 158fde10. PR #196 (retro) remains open at 6157c5f with its own red CI from the missing prerequisites. No worktree or branch cleanup is permitted before confirmed merges.
<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented and locally verified the CI zsh prerequisite and PATH-based shell lookup. Ubuntu execution awaits the pushed CI run; the separate OpenCode fixture defect is DOT-369.
<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->

## Run History
<!-- SECTION:RUN_HISTORY:BEGIN -->
<!-- RUN_HISTORY_ENTRY:BEGIN -->
```yaml
event_id: run-42ebac19f54b4e21809afb2094752603
type: claim_task
actor: opencode-claude-credential-path
timestamp: '2026-11-16T05:36:53.062181Z'
result: succeeded
task_id: DOT-367
from_status: todo
to_status: inprogress
metadata:
  lease_ttl_seconds: '7200'
```
Resolve the six Ubuntu CI failures at the existing real-shell test seam.
<!-- RUN_HISTORY_ENTRY:END -->
<!-- RUN_HISTORY_ENTRY:BEGIN -->
```yaml
event_id: run-2cfeb53e7602459c99d7e14f07b54924
type: release_task
actor: opencode-claude-credential-path
timestamp: '2026-11-17T16:57:20.882923Z'
result: succeeded
task_id: DOT-367
from_status: inprogress
to_status: todo
```
Focused tests and both mutations proven; hand the verified change to review while CI proves Ubuntu.
<!-- RUN_HISTORY_ENTRY:END -->
<!-- SECTION:RUN_HISTORY:END -->
