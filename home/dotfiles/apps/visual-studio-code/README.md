# visual-studio-code

Installs VS Code on macOS via the Homebrew cask into `~/Applications`, then
installs the editor's extension slice from the shared catalogue, and tears
both down the same way. The cask self-updates; the topic owns extension
currency under `--tags upgrade`.

## Run

From `dotfiles/`:

```bash
./executable_run-role.sh visual-studio-code            # provision the topic
./executable_run-role.sh visual-studio-code install    # cask + extensions
./executable_run-role.sh visual-studio-code remove     # opt-in teardown (tagged never)
```

## The extension contract

The extension truth lives in `dotfiles/config/editors.yaml` — one readable
catalogue shared by every editor topic, dated verdicts included. This topic
reads its slice directly (the interim contract; the subscription machinery
queued in `TASKS.md` § Planned replaces the read with playbook injection).

Topic-local knobs live in `defaults/main.yaml`:

- `vscode_extra_extensions` — entries only this editor wants (`id` + `why`)
- `vscode_ignored_extensions` — ids this editor declines even when shared
- `vscode_remove_extensions` — teardown gate, default **false**: `--tags
  remove` preserves extension state unless you set it true; when true, the
  claimed ids are uninstalled *before* the cask (the CLI dies with the cask)

An install run prints one verdict per entry and fails once at the end
naming every id it could not install. An extension the catalogue cannot
provide to this editor needs its `editors:` scope widened or an ignored
verdict — author decisions, recorded in the catalogue with dates.
