# visual-studio-code — changelog

Section names come from antsibull-changelog; see `docs/TOPICS.md`
§ "Per-topic changelog and local edge cases".

## 2026-09-17

### bugfixes

- Refreshed `vs_extensions.txt` from the live `code --list-extensions`: it
  recorded 18 extensions against 40 actually installed (golang, jupyter,
  biome, claude-code, mise, bats and 17 more were missing).

### known_issues

- **Nothing refreshes the manifest — it drifted for exactly that reason.**
  The topic's install is cask-only; `vs_extensions.txt` is written only by
  the hand-run `executable_export.manual` and consumed only by the hand-run
  `executable_import.manual`, neither wired to `update.sh` or any upgrade
  path. Any extension installed after the last manual export is invisible to
  the repo until someone re-exports by hand. Wiring a refresh in belongs to
  the downstream-IDE extension design queued in `TASKS.md` § Now, which
  decides where the shared manifest lives and who updates it.

- **The `.manual` scripts exist twice** — at the topic root and in `files/` —
  and both are hand-run helpers, not lifecycle tasks. They are not wired to
  anything, and `files/` is what chezmoi deploys; the topic-root copies are
  the working set. Untangling them is part of the same queued design.
