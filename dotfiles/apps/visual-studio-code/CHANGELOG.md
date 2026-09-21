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

### minor_changes

- **The topic now installs, updates and tears down its extensions from the
  shared catalogue — the interim direct-read contract** (2026-09-17, author
  direction "also wire now"). `install` reads
  `dotfiles/config/editors.yaml` by a role-relative path
  (`vscode_catalogue_path`, stable under both the parent playbook and
  `run-role.sh`), filters to this editor plus topic-local
  `vscode_extra_extensions`, lists what is installed (empty output is a
  valid state), installs the missing, prints one verdict per entry, and
  fails once at the end naming every unresolved id. `upgrade` runs
  `code --update-extensions` (`changed_when: false` — the CLI reports its
  own changes at -v; parsing its wording would bake it in as a contract).
  `remove` gained the gated teardown: `vscode_remove_extensions` (default
  false, house pattern cf. `chrome_remove_browser`) uninstalls the claimed
  ids BEFORE the cask, because the CLI dies with the cask. Isolation lives
  in the topic's defaults; the catalogue holds the domain truth. **This
  read is interim** — the subscription machinery queued in `TASKS.md`
  § Planned replaces it with `topic_subscribes` + an injected var, and
  that switch must be a no-op on a converged machine. Guarded by
  `tests/config/test_editors_catalogue.py` (mutation-proven: a commented-out
  `why` turns the schema test red). Check-mode note: the CLI probes and
  list step cannot run under `--check`, so a dry run reports every slice
  entry as would-install and the verdicts read "installed"; the real run's
  no-op convergence is the author's apply.

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
