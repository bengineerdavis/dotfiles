---
id: TASK-53
title: Review the automatic restart topics on `feat/topic-restart-stale`
status: To Do
created_date: 2026-10-27 02:55
labels:
- now
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
**Review the automatic restart topics on `feat/topic-restart-stale`.**
  [PR #5 open; resolving with the author in-session] User approved automatic restarts for stale services
  and GUI apps, plus topic-owned installation of the 1Password GUI. Review the
  shared role and both callers, reproduce any defects with tests, and prepare
  the change for human review under the deployed-file merge gate. Done when
  focused tests and topic validation pass, with deployment limits and remaining
  failures recorded. Worktree: `.worktrees/wt-restart` inside the main chezmoi
  source; no live restart or cask adoption during review.
  Review completed 2026-09-23 at `79f6f0f`: quit and reopen target the same
  bundle, and process-probe errors no longer count as a stopped app. Four
  regression cases failed before the fix; removing the exit-error guard killed
  both probe-error tests. Focused suite: 53 passed. Non-model repo suite:
  695 passed, 7 skipped, 7 deselected with all seven documented dependencies.
  Parent/topic syntax checks, 1Password metadata and `skillet validate .` pass.
  Scoped ansible-lint: 44 findings versus 42 on main (three path-role imports
  added, one lowercase task name removed). Debian live restarts, actual cask
  adoption and GUI Automation permission remain unverified. Per-GPU Ollama
  units remain outside the check. 1Password installs through brew but updates
  through its own updater; a disabled self-updater still needs an update path.
  Published [PR #5](https://github.com/bengineerdavis/dotfiles/pull/5) from
  `review/topic-restart-stale`, based on `origin/main`, with only the four
  restart commits. The author requested that it be resolved in-session after
  creation. The remote-base non-model suite is 690 passed, 1 failed, 7 skipped,
  7 deselected: the failure is the unchanged `git filter-repo` permissions
  expectation, already corrected by local-main commit `1e7899b`. No CI checks
  are configured on this PR. Complete the repo's author design check before
  merging; deployment is still separate.
  Worktree relocation complete [agent: OpenCode restart-review]: Git registers
  the new path at the same HEAD. Both existing local files had identical
  content hashes before and immediately after the move; the handoff paths
  were then updated. `git check-ignore` confirms the Git exclusion, and
  `chezmoi managed` lists 1,015 entries with none under `.worktrees/`.
  Split 2026-09-24 at the author's direction, because PR #5 bundled two
  topics under one title: the role plus its first caller, ollama, is branch
  `restart_stale_role_ollama` (worktree of the same name); the 1Password
  desktop app is `onepassword_desktop_app`, stacked on it. PR #5 is closed
  with pointers. The author's design review continues on the role PR from
  the PEP 8 question; see `.worktrees/restart_stale_style/.claude/HANDOFF-restart-review.md`.
  Landed since: #11 (`af02574`, role and ollama) and #15 (`2a1d009`, the
  1Password desktop app, re-landed after #12 merged into #11's branch). The
  code is on main; the only open part is the author's design walkthrough,
  paused at the PEP 8 question. Resolve this item when the author closes or
  drops that walkthrough.
  Author, 2026-09-28: continue, with a scoped style cleanup first. Both now
  run in worktree `restart_stale_style`; the old `wt-restart` worktree and
  branch `review/topic-restart-stale` are retired.
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
