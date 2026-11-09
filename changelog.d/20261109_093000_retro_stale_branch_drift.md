### Changed

- Consolidated "chezmoi acts on the checked-out branch" into one block in
  `docs/WORKTREES.md` § Main-checkout: the three consequences (a reconcile
  misreads, an apply overwrites, a status/diff reports phantom drift) now hang
  off the single root fact instead of being restated across AGENTS.md and
  WORKTREES.md. AGENTS.md's two mentions now point at that block.