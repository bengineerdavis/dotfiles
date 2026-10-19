2026-10-19 — topic created

## Added

- **agentsview topic** — installs [agentsview](https://agentsview.io), the
  local AI session viewer, on both machines: cask on Darwin (homebrew-core,
  no tap trust needed; the cask carries both the desktop app and the CLI
  binary), and on Debian the release tarball CLI into `~/.local/bin` plus
  the desktop AppImage into `~/Applications`, both checksum-verified
  against the GitHub releases API's per-asset digests.

## Known issues

- Debian desktop use requires `libfuse2`, which prerequisites.yaml
  installs when `agentsview_install_desktop_appimage` is on; the package
  stays after remove unless `agentsview_remove_libfuse2` is flipped
  (AppImages are shared state — the apps/roborev tap pattern).
- The upstream `agentsview update` self-updater is deliberately unused:
  it would replace topic-managed files outside Ansible's knowledge, the
  same reasoning apps/roborev records.
- No linuxbrew on the Debian box; if it is ever adopted the topic
  collapses to the cask on both platforms (recorded in the README so the
  retirement path is already written down).