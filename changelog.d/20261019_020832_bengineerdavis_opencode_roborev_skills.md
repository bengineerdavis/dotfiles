# Added

- apps/opencode: declare the roborev skill family (ten skills: review,
  design-review, lookahead-review, and their branch variants, fix, refine,
  respond, snooze) as vendored in the approved-sources guard. `roborev
  skills install` (apps/roborev's binary) writes them into the shared
  `~/.agents/skills` bucket — a surface this topic guards, but one roborev
  has no dotagents source for, since the skills ship inside the binary.
  Each skill directory carries LICENSE (roborev is MIT) and PROVENANCE.md;
  the `why` entries record the tool-trust rationale. Refresh discipline is
  version-locking: skills change only when the binary does, so re-stamping
  belongs in apps/roborev's upgrade pass, not a timestamp sweep.