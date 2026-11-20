# agentsview — changelog

This topic's own history. It travels with the directory, so a topic lifted
into another repository arrives with its history and its edge cases intact.

Entries are dated, not versioned. Drop the sections you do not need — an
empty heading is worse than an absent one. Record upstream behaviour you
had to work around under `known_issues`, and keep the *reason* for the
workaround in a comment beside the task that does it.

## 2026-10-19

### Added

- Topic created: cask on Darwin, checksummed tarball CLI + AppImage desktop
  on Debian, both verified against the releases API's per-asset digests.

### Known issues

- libfuse2 is installed for the AppImage and kept on remove by default
  (shared AppImage dependency; see the flag in defaults).
- The upstream self-updater is unused on purpose — it would fight the
  topic's version stamp.
- No Linuxbrew on the Debian box; the cask's Linux artifacts are the
  documented collapse path if that changes.