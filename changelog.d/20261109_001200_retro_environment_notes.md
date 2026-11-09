### Changed

- Recorded three environment notes from the Nov 8 retro, each naming a
  measured incident:
  - `R` in `chezmoi status` means "Run" (script will run next apply), not
    Remove — a `run_before_` script shows it permanently, and it is normal
    (AGENTS.md § Applying-is-main-only).
  - `git add` on an already-`git rm`'d path fails the commit chain and the next
    `git show --stat HEAD` reads the pre-existing commit; verify HEAD moved
    (CONTRIBUTING.md § Commit granularity).
  - Confirm `git branch --show-current` is `main` before a shared-checkout
    reconcile or apply (docs/WORKTREES.md).