### Added

- A `branch-sync` pre-push hook fast-forwards local `main` and simulates the
  merge with `git merge-tree`, so a branch that no longer merges with `main`
  is named at push time instead of at merge time. It reports conflicts and
  never merges for you.

### Changed

- New Worktrunk worktrees fast-forward clean `main` before creation. A
  push-triggered and 15-minute GitHub pulse updates eligible same-repository
  PR branches using native clean merges, expected-head protection, and a
  manual dry-run.
