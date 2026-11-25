### Added

- OpenCode gains a global `/resume` command: it names the current session from
  `HANDOFF.md` or other project context, then resumes that work, instead of
  opening a blank session. It is a chezmoi-owned config file
  (`home/dot_config/opencode/commands/resume.md`), not topic state — the opencode
  topic still owns only the binary and the skill set. This is the manual
  counterpart to DOT-344: that task makes a claim name the session
  automatically, where `/resume` lets you name one on demand.

  It is deliberately not named `/new`. That name is already a TUI built-in
  (`session.new`, "Create a new session"), and OpenCode's slash autocomplete
  appends server commands without deduplicating them
  ([anomalyco/opencode#66019](https://github.com/anomalyco/opencode/issues/66019),
  reproduced on 2.2.5 and 2.2.6): `/new` would list twice and the default
  selection would open a blank session instead of running this command.
