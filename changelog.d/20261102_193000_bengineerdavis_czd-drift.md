### Added

- `czd` — read chezmoi drift as text and as an exit status. `chezmoi diff`
  honours the meld `[diff] command`, so a piped or agent-driven call prints
  nothing and exits 0 even when a managed file differs; `czd` calls
  `chezmoi diff --use-builtin-diff` instead, leaving the graphical config
  untouched for interactive use. It exits 1 on drift and 2 on error, so a
  checker can branch on `$?` rather than parse output.

### Fixed

- Agent guidance now names `czd` for drift reads. An empty `chezmoi diff` had
  been read as "no drift" on a machine with a real difference in
  `~/.config/opencode/opencode.jsonc` (measured 2026-11-02).
