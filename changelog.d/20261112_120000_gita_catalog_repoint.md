### Changed

- **`config/repos.yaml` paths are re-pointed at the type dirs.** The
  catalogue still named the pre-migration `projects/…` layout, so a run on
  the migrated machine matched nothing and reported every repo as
  declared-but-not-cloned. Paths now follow `docs/LAYOUT.md` (`personal/`,
  `forks/`, `templates/`, `try/`), and the repos added since the last settle
  are in it.
