### Added

- Root `pyproject.toml` and `uv.lock`: the test suite now runs from locked
  dependency groups instead of a seven-flag `--with` incantation. `uv run
  --frozen` rebuilds the environment offline from cache. The repo is never
  built or installed (`package = false`).

### Fixed

- Repo tooling no longer deploys to `$HOME`: convention docs (`LANGUAGES.md`,
  `GLOSSARY.md`, `WORKTREES.md`), hook scripts (`scripts/`), `tools/`, and
  two stray `bin/` backups are ignored. The governance guard now works from
  git worktrees (`chezmoi -S`) and covers project files.
