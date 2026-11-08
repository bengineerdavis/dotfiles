### Changed

- `scripts/check_commit_proportionality.py` now leads its failure message with
  the escape hatch — "if the length is genuinely warranted, add a
  `Proportionality:` trailer" — instead of burying it after the word-count
  arithmetic. The split-into-two advice follows. A failing author now sees the
  way forward first.

### Fixed

- `docs/agents/issue-tracker.md` records that `backlog-py task` has no `view`
  subcommand (reads are the bare `backlog-py task <id>`), after the CLI's own
  `--help` "View tasks" line invited the wrong verb.

### Changed

- `docs/WORKTREES.md` § Reap now says squash merges rewrite every commit SHA,
  so `git merge-base --is-ancestor` reports "not merged" after a PR merges;
  verify by content (`git show main:<path>`) or `git cherry`.

### Changed

- `tests/docs/test_lore_md_rules_survive.py` docstring notes that title-only
  corruption is not caught by design — the anchor lives in the body, so a
  title/body swap that keeps the body still passes, and that is correct.