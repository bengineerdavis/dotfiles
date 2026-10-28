**Changed**

- Chezmoi owns the `~/.config/mise/config.toml` symlink; the topics own the
  file it points at. `dotfiles/apps/mise/files/config.toml` is now in
  `.chezmoiignore`, so `chezmoi apply` no longer deploys a second copy to
  `~/dotfiles`. A `mise use -g` capture is a git commit, not an apply.
- `docs/WORKTREES.md` records why `chezmoi diff` and `chezmoi apply` are wrong
  from a worktree: they compare the worktree source against the live targets,
  so the same differing files reappear on every run and open in the configured
  GUI diff tool.
