### Fixed

- The changelog collector retries a rejected push instead of losing the entry.
  It built its collection commit on the merged PR's own commit, then pushed
  fifteen seconds later. A merge that landed on main in between made the push
  a non-fast-forward rejection: the run went red, the commit died with the
  runner, and the fragment sat on main with no changelog entry. PR #106's
  fragment was lost this way on 2026-10-30 and stayed uncollected for a week.
  The collector now replays its commit onto the new main and retries, at most
  three times, then fails with an error naming the fragment that is still
  uncollected.
- A failed collection can be re-run by hand. The workflow gained a
  `workflow_dispatch` trigger taking the PR number, because a red run
  previously had no recovery path: the commit died with the runner and no
  later PR's file list mentions that fragment.
