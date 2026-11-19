---
id: DOT-390
title: 'retro: capture findings from the DOT-343 launchd and service-role session'
status: To Do
created_date: 2026-11-19 21:30
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->

Session retro (2026-11-17 to 2026-11-19, `dot-343-launchctl-rc5` worktree): the
launchd rc 5 diagnosis and fix, the shared `roles/services` role it grew into,
and the close-out. Corrections and negative results recorded, not just
successes.

**What landed**

- PR #181 merged (`3f245f67`): the convergence fix, the shared
  `home/dotfiles/roles/services` role (8 files, first caller `apps/backlog`),
  and the `docs/TOPIC-RECIPES.md` correction that had been teaching the bug.
- PR #189 (this branch): recovery of two commits that existed only on the
  shared checkout's local `main` — `DOT-387` and
  `docs/CHERRY-PICK-RECONCILIATION.md` — plus the `AGENTS.md` reference the
  conventions gate required.

**What went wrong (corrections)**

1. **I asserted a race I never measured.** `converge.yaml` claimed `bootout`
   returns before teardown and a bootstrap racing it sees stale state. Removing
   the wait mutation-survived the suite, so I probed it: **0 failures in 25
   attempts**. The claim was my assumption dressed as a finding. Corrected in
   both the code comment and the README to say it is unverified insurance.
   Lesson: a mutation that survives is evidence about the claim, not just
   about the test — probe before writing the reason into a comment.
1. **A `git checkout <file>` destroyed my own migration.** During a mutation
   test I ran `git checkout home/dotfiles/apps/backlog/tasks/remove.yaml` to
   undo the mutation, which reverted the file to the *pre-migration* version
   and silently discarded the work. Rebuilt it by hand. Lesson: after a
   mutation, restore from a copied backup (`cp` to a temp file), never
   `git checkout` a file I have legitimately modified.
1. **A merge attempt staged 17 files I did not intend to commit.** The aborted
   `git pull` left the whole incoming changeset staged; committing would have
   swept it in as one commit. Caught by inspecting `git diff --cached`.
   Lesson: after any conflicted or aborted merge, re-read the index before
   committing — a merge populates it far beyond the conflict.
1. **The shared checkout's divergence was assumed simpler than it was.** The
   reconciliation doc claims a `reset --hard origin/main` is safe. It is not:
   two commits (`9df1a609` DOT-387, `131e2df6` the doc itself) exist on local
   `main` and on **no branch and no remote**. A reset would have destroyed
   both. Recovered onto `agent/recover-local-main` before anything else.
   Lesson: "safe to reset" claims in prose need the same verification as code
   claims — enumerate what is reachable only from the ref being reset.
1. **`backlog-py doctor` reported "No problems found" while I created a
   duplicate task id.** The CLI allocated DOT-388, which already existed on
   `origin/main`; doctor does not scan origin or branch snapshots, so it
   reported clean while `task` and `board` would disagree. Caught by grepping
   `origin/main` for the id after creation. Lesson: allocation is bounded by
   what is *pushed* — verify a new id against `origin/main`, not the local
   tree, and pass `--id` when a collision is plausible.

**Negative results**

- The 12 `test_opencode_config_layers.py` failures I reported as pre-existing
  during PR #181 were genuinely pre-existing at that time, and are **gone** on
  current main — another session fixed them. Re-deriving the baseline per PR
  was still correct; the answer changed, not the method.
- The 6 `claude_credentials` failures fail **only in CI**, not locally (9
  passed on a pristine `origin/main` worktree). That is a CI-environment
  defect, tracked by PR #185, not a code regression, and the local baseline
  could not have revealed it — the CI log had to.
- The quiz on PR #181 scored 4/8 and I deliberately did **not** call the PR
  reviewed. The merge still went ahead on the author's instruction.

**Follow-ups filed**: DOT-375 (the `--amend` proportionality hook bug,
confirmed at `scripts/check_commit_proportionality.py:89-102`), DOT-376 (three
format-dirty `ollama_models` test files). Both remain open.

**Handoff — DOT-343 AC #2 is still open**

DOT-343 is marked `Done` (PR #181 merged) but its AC #2 was never executed and
the checkbox is still unticked on `origin/main`. It is the only unresolved item
this session leaves behind.

- **Current status**: the fix is merged and its convergence is proven against
  the role; the *live topic run* is unverified.
- **Next concrete action**: run the topic twice and confirm the daemon answers.
  This restarts the live daemon, so it is the author's to run.
- **Resume commands** (from the shared checkout, on `main`):
  ```sh
  bash home/dotfiles/executable_run-role.sh backlog
  bash home/dotfiles/executable_run-role.sh backlog
  backlog-py daemon status --json   # expect exit 0
  ```
- **Observation to compare against**: at diagnosis time the daemon was healthy
  (pid 2564, port 18765) because the label happened to be enabled; the failure
  is state-dependent, so a green run today does not by itself prove the fix
  unless the label was disabled first. To exercise the fixed path deliberately:
  ```sh
  launchctl disable gui/$(id -u)/com.backlog-py.daemon
  bash home/dotfiles/executable_run-role.sh backlog
  ```
  and confirm it converges rather than failing with `Bootstrap failed: 5`.
- **Owned files**: `home/dotfiles/roles/services/**`,
  `home/dotfiles/apps/backlog/tasks/{install,remove}.yaml`,
  `tests/topics/test_services_role.py`,
  `tests/topics/test_backlog_daemon_bootstrap.py`.
- **Checks run this session**: role + topic suites 26 passed; role exercised
  end-to-end through Ansible (converged a throwaway label to
  `state = running, pid = 83922`); CI failure set byte-identical to main's.
  **Not verified**: the live topic run (AC #2).
- **No blocker** beyond needing the author's approval and the apply claim.

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
