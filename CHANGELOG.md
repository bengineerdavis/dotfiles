# Changelog

What changed here, written for someone who wants to know what is different since
they last looked.

This is not `git log`. A commit message serves someone reverting one change and
asking what it was; this serves someone asking what changed and why they should
care. Both are kept, deliberately, because they answer different questions.

Entries are written as fragments in `changelog.d/` at the time of the change and
collected here on release. Add one with:

```bash
uv run --with scriv scriv create
```

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

<!-- scriv-insert-here -->

<a id='changelog-Unreleased'></a>
## Unreleased — 2026-09-10

### Added

- A changelog. Entries are written as fragments in `changelog.d/` when the
  change is made and collected here on release, so nothing is reconstructed
  from commit messages later.
- Contribution standards for agents and people in `CONTRIBUTING.md`,
  including what to do when an agent fails part-way through a task.
- A register of every external standard this repo follows, in
  `docs/REFERENCES.md`, with the version followed and when it was last checked.

### Changed

- Commit messages are now checked against the size of the change they describe.
  An over-long message usually means the commit should have been two.
- Agent permissions were rebuilt from scratch. `chezmoi apply` is refused
  outright; publishing, installing and deleting ask first.

### Fixed

- The git hooks had never run. `.pre-commit-config.yaml` was configured but no
  hooks were installed, so shellcheck had never checked anything.
- The documented test command was missing a dependency and produced 53 errors
  when run exactly as written.
