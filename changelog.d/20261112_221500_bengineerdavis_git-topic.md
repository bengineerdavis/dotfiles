### Added

- Git now has a cross-platform topic. It installs Git during fleet
  prerequisites and provides the dependency used by gita and Chrome.
- Global excludes and comment-only commit-message guidance join the existing
  chezmoi-managed Git configuration. Git identity still comes from the
  existing chezmoi prompts, not a machine-specific value in the repository.

### Changed

- Git package ownership moved out of the Homebrew and apt core package lists.
  Their system-wide upgrade passes continue to keep Git current.

### Security

- Removing the Git topic does not remove Git by default. Package removal needs
  explicit opt-in and is refused while another topic requires Git or the
  dependency index is unavailable.
