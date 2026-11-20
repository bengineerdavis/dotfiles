### Fixed

- The Claude credential tests no longer require macOS's `/bin/zsh`. CI installs
  zsh explicitly, and the harness finds it on the supplied `PATH`, so Ubuntu
  runs the same real-shell profile tests instead of failing on a missing path.
- The profile-deployment test no longer fails on a missing `chezmoi` binary.
  CI installs the pinned chezmoi release before the suite runs, matching how a
  developer machine already provides it.
