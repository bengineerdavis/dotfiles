### Fixed

- The dotagents-caller guard now matches dotagents as a **command**, not as a
  word. `test_every_dotagents_caller_reports_stderr` matched the bare string
  anywhere in a task file that contained any `command`/`shell` task, so a task
  named "Check that dotagents installed the tree" — or a failure message telling
  the operator to run the dotagents topic — was treated as a caller that
  discards stderr. That turned the gate red for a change that never invoked
  dotagents (`apps/opencode/tasks/install.yaml`). The guard now parses the task
  YAML and inspects only command/shell values, which is what "shells out to
  dotagents" has always meant. The original 2026-09-12 bug is still caught:
  swapping `.stderr` for `.stdout`, or dropping `failed_when: false`, still
  fails the test.

### Added

- `docs/WORKTREES.md` § Verifying a pre-existing failure: the check that must
  run before reporting a test failure as "pre-existing". Comparing against
  `main`, or against a base from before a rebase, does not answer the question.
  The only commit that answers it is the **actual parent of the commit under
  test**, and a rebase invalidates any earlier answer. This session reported
  three failures as pre-existing and was wrong about one of them; CI caught it,
  the reviewer would not have.
