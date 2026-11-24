### Added

- OpenCode gains a global `/new` command: it names the current session from
  `HANDOFF.md` or other project context, then resumes that work, instead of
  opening a blank session. It is a chezmoi-owned config file
  (`home/dot_config/opencode/commands/new.md`), not topic state — the opencode
  topic still owns only the binary and the skill set. This is the manual
  counterpart to DOT-344: that task makes a claim name the session
  automatically, where `/new` lets you name one on demand.
