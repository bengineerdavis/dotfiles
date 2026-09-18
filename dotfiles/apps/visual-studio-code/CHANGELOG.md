# visual-studio-code — changelog

Section names come from antsibull-changelog; see `docs/TOPICS.md`
§ "Per-topic changelog and local edge cases".

## 2026-09-17

### bugfixes

- Refreshed `vs_extensions.txt` from the live `code --list-extensions`: it
  recorded 18 extensions against 40 actually installed (golang, jupyter,
  biome, claude-code, mise, bats and 17 more were missing).

### removed_features

- Retired the superseded extension record: `vs_extensions.txt` and all four
  `executable_{export,import}.manual` copies (topic root and `files/`) are
  gone, 2026-09-17. The hand-run scripts were the drift mechanism diagnosed
  below — written by hand, consumed by hand, wired to nothing, which is how
  the manifest silently fell 22 extensions behind. Their job is absorbed by
  the shared catalogue `dotfiles/config/editors.yaml` (seeded `b4bc9db`),
  which this topic now consumes directly — see the interim contract entry
  the same day. The `files/` copies were chezmoi-deployed; the next apply
  clears them from the deployed tree. `vs_settings.json` remains: live
  settings sharing is a separate, still-open question.

### known_issues

- **The manifest drifted because nothing consumed or refreshed it.** The
  historical diagnosis, kept because it is why the catalogue exists:
  install was cask-only, `vs_extensions.txt` was written only by the
  hand-run `executable_export.manual` and consumed only by the hand-run
  `executable_import.manual`, and any extension installed after the last
  manual export was invisible to the repo — 18 recorded against 40
  installed when measured 2026-09-17. The subscription model closes this
  structurally: the catalogue is the only input, and wiring a refresh in
  belongs to the upstream-reference cadence design queued in `TASKS.md`.
