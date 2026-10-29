# claude-code — changelog

Section names come from antsibull-changelog; see `docs/TOPICS.md`
§ "Per-topic changelog and local edge cases".

## 2026-09-14

### release_summary

Topic created. Claude Code and the Claude desktop app are now installed from
Homebrew casks, and the undeclared mise install that shadowed the CLI on PATH
is removed.

### minor_changes

- Install the CLI from a Homebrew cask, defaulting to `claude-code@latest`.
  `claude_code_cask` selects the channel; the conflicting cask is uninstalled
  first, since the two refuse to coexist.
- Install the Claude desktop app from cask `claude`, behind
  `claude_code_install_gui`.
- Remove an orphaned mise install of `npm:@anthropic-ai/claude-code` and reshim,
  behind `claude_code_remove_mise_orphan`.
- Report `claude doctor` at the end of an install without failing the run on it.

### known_issues

- **A mise shim can shadow the Homebrew binary, and the symptom is a version
  that does not match.** Measured on this machine 2026-09-14:
  `~/.local/share/mise/shims/claude` sat at PATH position 71 against
  Homebrew's 81, so `command -v claude` returned the shim. It worked only by
  falling through to the cask binary, while `mise ls` reported `2.1.140` and
  the binary answered `2.1.236`. The mise install was never declared in
  `apps/mise/files/config.toml`, so nothing in the repo would have recreated
  it. `claude doctor` reports this class of problem; upstream documents it
  under "Check for conflicting installations". This topic clears it, but any
  hand-run `npm install -g` or native installer will reintroduce it.

- **Homebrew installs never update themselves.** Upstream: "Homebrew
  installations do not auto-update." A machine that skips the upgrade pass
  stays on the version it has, indefinitely and silently. Setting
  `CLAUDE_CODE_PACKAGE_MANAGER_AUTO_UPDATE=1` would make Claude Code run
  `brew upgrade` on its own — deliberately not set, because it reintroduces a
  second version owner.

- **The two casks are channels and cannot coexist.** `claude-code` tracks
  stable, `claude-code@latest` tracks latest, each declares `conflicts_with`
  the other, and both ship a `claude` binary. Changing `claude_code_cask` is a
  channel switch, not a version bump, and it uninstalls before it installs.
  Claude Code's own `autoUpdatesChannel` setting has no effect under Homebrew.

- **The desktop app self-updates.** Cask `claude` declares `auto_updates`, so
  brew's recorded version drifts from what is installed. It is not added to
  `homebrew_upgrade_cask_exclude` — that list exists for rancher's
  sudo-invoking uninstall stanza, not for self-updating apps generally.

- **Debian is not supported by this topic.** Claude Code on Debian installs
  from a signed apt repository (keyring at `/etc/apt/keyrings/claude-code.asc`,
  fingerprint `31DDDE24DDFAB679F42D7BD2BAA929FF1A7ECACE`, with `stable` and
  `latest` suites). That needs sudo and a repo file, so it is separate work
  rather than a branch here. `topic_os` is `[Darwin]` until it is done.

- **`~/.claude/` is unmanaged.** Settings, credentials and session history live
  together and have not been split into portable and machine-local halves, so
  none of it is versioned. Teardown leaves it alone unless
  `claude_code_remove_config` is set. Note the VS Code extension, the JetBrains
  plugin and the desktop app write there too, so the directory reappears while
  any of them is installed.
