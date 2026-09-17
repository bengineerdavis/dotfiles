# cursor — changelog

Section names come from antsibull-changelog; see `docs/TOPICS.md`
§ "Per-topic changelog and local edge cases".

## 2026-09-17

### release_summary

Topic brought to TOPICS.md conformance: this changelog and a real README
added, the dead pre-role `tasks.yaml` removed. The topic's substance is
unchanged — it installs the Cursor IDE from the Homebrew cask and tears it
down the same way.

### trivial

- Remove `tasks.yaml`, a leftover from the pre-role include era that nothing
  referenced.
- Replace the template-boilerplate README with one describing the topic.

### known_issues

- **The cask is `auto_updates`, so brew's recorded version drifts.** Cursor's
  own updater moves the app between brew runs, which is the same standing
  drift the two other self-updating casks already carry (noted in
  `TASKS.md` § Where things stand). Not excluded from the brew upgrade pass.
- **This topic installs no extensions.** Cursor shares its extension set
  with VS Code and the other downstream IDEs; that design is queued in
  `TASKS.md` § Now (downstream-IDE extension sharing, advisor council) and
  lands as its own wiring. Availability differs per editor — Cursor resolves
  extensions through OpenVSX rather than Microsoft's marketplace, so
  closed-source `ms-*` extensions (pylance is the known risk class) cannot
  be assumed to install.
