### Added

- **`apps/gita` now owns the work-tree registration.** Every install
  reconciles `~/code/work` into a single `work` group: repos that appeared are
  registered by the recursive walk (which skips vendored dot-directories), and
  every work-tree registration is swept into the group — so `gita fetch` /
  `gita pull` cover the whole tree. Work repo names still never enter the
  committed catalogue (spec.md § Data); discovery, not declaration, is their
  source of truth.

  There is deliberately no prune step. `gita freeze` filters vanished repos out
  of its own output, so the list it prints never contains a ghost to prune, and
  `gita rm` refuses names `gita ls` does not report. A stale row left in
  gita's own CSV is harmless: gita re-adopts the repo if it returns at the same
  path.
