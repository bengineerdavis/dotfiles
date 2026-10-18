# Changed

- mise: `@sentry/skillet` approved past aube's npm supply-chain threshold
  (`allow_low_downloads = true`) — aube had refused it at 7 weekly downloads
  against the 1,000 threshold; the approval is recorded in-tree next to the
  tool entry with the verification note. roborev is intentionally NOT pinned
  in mise: `apps/roborev` remains the sole install owner (checksum-verified
  .deb on Debian, brew on Darwin), and a mise shim would shadow the
  topic-installed binary.
# Added

- `~/.zshenv` (chezmoi): TMPDIR defaults to `~/.cache/tmp` when unset and
  usable, exported only after the directory is created and verified writable
  (an unusable dir falls back to stock /tmp). Reason: aube derives its npm
  lock dir from TMPDIR and defaults to shared `/tmp/fslock`, which a root run
  had created root-owned — breaking npm installs for every user on a machine
  whose /tmp never self-clears. Accumulation handled by the new user
  tmpfiles rule (`~/.config/user-tmpfiles.d/tmp.conf`, 30-day purge).
  Known bounds recorded in the file: cron's /bin/sh bypasses zsh, and
  preserved-env privileged runs are out of reach of shell config.
