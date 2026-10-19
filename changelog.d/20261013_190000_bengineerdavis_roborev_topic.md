### Added

- roborev topic (`apps/roborev`): the automatic AI code-review daemon, on
  both machines. macOS installs the `roborev` formula from upstream's
  `kenn-io/tap` tap, trusted before tapping — Homebrew 7 refuses an
  untrusted third-party tap at tap time and the refusal names neither cause
  nor fix. Debian fetches the release `.deb`, checksum-verified against the
  GitHub API's per-asset digest, and owns its own upgrades because
  `apt upgrade` cannot reach a GitHub-release deb. `--tags remove`
  uninstalls the binary and keeps the tap unless `roborev_remove_tap` is
  flipped, mirroring `apps/opencode`.
