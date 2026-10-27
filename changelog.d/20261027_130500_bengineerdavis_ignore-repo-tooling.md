**Fixed**

- `.chezmoiignore` now covers the repo tooling added after its per-file docs
  list was written: `backlog/` (the task queue) and `docs/agents/`,
  `docs/BACKLOG-MIGRATION.md`, `docs/BACKLOG-UPSTREAM-CONFIG.md`. Without this,
  `chezmoi apply` would create `~/backlog` and deploy repository documentation
  into `~/docs`.
