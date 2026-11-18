# Git — changelog

## 2026-11-12

### release_summary

Create a cross-platform Git topic and transfer Git package ownership from the
Homebrew and apt core prerequisite lists.

### minor_changes

- Provide Git during fleet prerequisites with OS-specific Homebrew and apt
  tasks. System package-manager roles retain package upgrades.
- Keep global Git settings, local-tool excludes, and a comment-only
  commit-message template in chezmoi.
- Guard package teardown behind explicit opt-in and a complete dependency
  index; shared or unproven removal leaves Git installed.

### known_issues

- `topical new` expects the legacy `dotfiles/` layout by default. This topic
  was scaffolded with explicit `--repo <checkout>/home --into
  <checkout>/home/dotfiles` paths. Its emitted manager blocks also required
  Darwin-only Homebrew and Debian-only apt guards.
- The global `~/.git-template` directory is not captured here. `DOT-316` owns
  its machine-state hook validation.
