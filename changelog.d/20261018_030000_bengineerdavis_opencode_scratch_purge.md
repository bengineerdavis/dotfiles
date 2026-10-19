# Added

- `~/.config/user-tmpfiles.d/tmp.conf`: age `/tmp/opencode` (opencode's
  agent scratch dir) on the same 30-day schedule as `~/.cache/tmp`.
  The dir accumulates unbounded — 35+ stale entries spanning weeks were
  observed on 2026-10-17 — because `/tmp` never self-clears on
  root-fs machines and no tool cleans it. The `e` type cleans contents
  of the existing dir only; live sessions are unaffected, and the
  already-running `systemd-tmpfiles-clean.timer` does the sweeping.
