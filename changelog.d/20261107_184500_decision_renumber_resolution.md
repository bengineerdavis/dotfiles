### Changed

- The duplicate `decision-2` in `backlog/decisions/` is resolved in favour of
  the configuration-trials record, which keeps `decision-2`; the codex routing
  record became `decision-4` in `7eb3a2a`. A second session reached the same
  collision with the opposite assignment — trials to `decision-4`, codex kept
  at `decision-2` — reasoning that codex is cited from three places against the
  trials record's one. Both resolved it; main keeps the first. That branch
  (`agent/decision-renumber-4`, commit `b481ea3`) was deleted after its one
  unique finding was taken: four places in DOT-289 named `decision-1` for the
  VM-verified deployment gate, which is `decision-3`, landed separately as
  `99eecd2`. Recorded here because a branch deleted without a trace leaves the
  next session re-deriving a decision that was already made twice.