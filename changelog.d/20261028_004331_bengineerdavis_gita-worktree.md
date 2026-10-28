### Added

- **`apps/gita` now owns the work-tree registration.** Every install
  reconciles `~/code/work` into a single `work` group: registrations whose
  repos left the machine are pruned, repos that appeared are registered by
  the recursive walk (which skips vendored dot-directories), and every
  work-tree repo lands in the group — so `gita fetch` / `gita pull` cover
  the whole tree. Work repo names still never enter the committed catalogue
  (spec.md § Data); discovery, not declaration, is their source of truth.

### Changed

- **`config/repos.yaml` paths are re-pointed at the type dirs.** The
  catalogue still named the pre-migration `projects/…` layout, so a run on
  the migrated machine matched nothing and reported every repo as
  declared-but-not-cloned. Paths now follow `docs/LAYOUT.md` (`personal/`,
  `forks/`, `templates/`, `try/`), and the repos added since the last settle
  are in it.
