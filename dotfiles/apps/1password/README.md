# 1password

Two parts of 1Password, managed in one topic:

- **The CLI, `op`**, on macOS and Debian. The [mise](../mise) topic installs and
  upgrades the binary through `apps/mise/files/config.toml`:

  ```toml
  "1password-cli" = "latest"
  ```

  This topic lets other topics depend on the concept "1password". It also lets
  the parent playbook check that `op` is on `PATH` before a topic needs to fetch
  secrets.

- **The desktop app**, on macOS only. The topic installs it as the `1password`
  Homebrew cask and restarts it when an update left it running the old binary.

## The desktop app

| | How |
|---|---|
| Install | `brew install --cask 1password --adopt --appdir=/Applications`. `--adopt` takes over an app that is already there and leaves it in place. |
| Upgrade | 1Password's own updater. The cask is `auto_updates`, and brew does not also upgrade it. `tasks/upgrade.yaml` explains why. |
| Restart | `roles/restart-stale`, at the end of `tasks/install.yaml`, under `--tags install` and `--tags upgrade`. It asks the app to quit, waits, and reopens it. If the app does not quit, the role reports it and leaves the app running. It never force-quits. |
| Remove | Opt-in with `-e onepassword_remove_app=true`. The uninstall never zaps, so vault data under `~/Library` stays. |

### Why /Applications and not ~/Applications

This repo installs casks into `~/Applications` so that they do not need sudo.
1Password is the exception. Its support article on the error "We weren't able
to connect to the 1Password extension in your browser" says both 1Password and
the browser must be in `/Applications`. The reason is recorded next to
`onepassword_appdir` in `defaults/main.yaml`.

### Known issues

- By the same 1Password article, the browser must be in `/Applications` too.
  `apps/firefox` installs Firefox into `~/Applications`, which is where it is on
  this machine. So Firefox cannot connect to the 1Password app. Chrome is in
  `/Applications` and is not affected. This topic does not move Firefox.

## Cross-platform

`topic_os` includes both `Darwin` and `Debian`. The desktop app is only managed
on macOS. `homebrew` is not in `topic_requires` because that would make the
topic unschedulable on Debian. `tasks/install.yaml` checks for `brew` on macOS
instead.

## Verification

```bash
./run-role.sh 1password
```

If `op` is not on `PATH`, this fails with a message that names the next step.

To use 1Password as the secrets source for another topic, pass
`-e debget_secrets_manager=1password` (example: deb-get).

## Tests

```bash
mise exec -- ansible-playbook apps/1password/tests/topic-metadata.yaml
uv run --with pytest --with pyyaml --with hypothesis pytest tests/restart_stale -q
```
