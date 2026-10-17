**Changed**

- The global opencode `external_directory` boundary now also allows the two
  external-skill trees, `$HOME/.agents/skills/*` and `$HOME/.claude/skills/*`.
  Motivating case: `aboyeur`, installed 2026-10-13, was unreadable from a
  session started earlier — opencode's runtime auto-allow only covers skill
  directories registered at session start, so mid-session installs and
  unregistered directories had no rule. The static allows make the trees
  readable in every session without per-skill entries. Contract test updated
  (trio → deny + four allows), mutation-proven; the boundary stays
  deny-everywhere-else.
