# claude-code

Installs [Claude Code](https://claude.com/product/claude-code), Anthropic's
terminal coding agent, and the Claude desktop app — and removes the conflicting
install that used to shadow them.

## What it manages

| Layer   | State                                              | Owner      |
|---------|----------------------------------------------------|------------|
| Ansible | the `claude` CLI, from a Homebrew cask              | this topic |
| Ansible | `Claude.app`, from cask `claude`                    | this topic |
| Ansible | removal of the orphaned mise `claude` shim          | this topic |
| nobody  | `~/.claude/`, `~/.claude.json` — settings, credentials, session history | machine-local, not versioned |

## Channels, not versions

Homebrew ships two mutually exclusive casks, and they are release channels:

| Cask                | Channel | Measured 2026-09-14 |
|---------------------|---------|---------------------|
| `claude-code`       | stable — about a week old, skips releases with major regressions | 2.1.236 |
| `claude-code@latest`| latest — new versions as soon as they ship | 2.1.270 |

Both ship a `claude` binary and each declares `conflicts_with` the other, so
exactly one can be installed. `claude_code_cask` picks; `install.yaml`
uninstalls the other first, because brew refuses the install otherwise.

Under Homebrew the cask name *is* the channel — Claude Code's own
`autoUpdatesChannel` setting does not apply.

## One version owner

**brew owns the version, and nothing competes with it.** Upstream is explicit
that "Homebrew installations do not auto-update", so there is no self-updater to
switch off. Two consequences worth knowing:

- Skipping the upgrade pass means staying on the installed version indefinitely.
  `brew upgrade` is the only thing that moves it.
- `CLAUDE_CODE_PACKAGE_MANAGER_AUTO_UPDATE=1` would make Claude Code run
  `brew upgrade` itself in the background. This topic never sets it: that is a
  second owner, which is the problem the topic was built to remove.

The desktop app is different — cask `claude` declares `auto_updates` and keeps
itself current, so brew's recorded version for it is approximate.

## The shim this topic clears

Before this topic existed, `claude` on this machine resolved to
`~/.local/share/mise/shims/claude` — a shim from an **undeclared** mise install
of `npm:@anthropic-ai/claude-code`, which was never in
`apps/mise/files/config.toml`. mise's shim directory precedes `/opt/homebrew/bin`
on `PATH`, so the shim won and worked only by falling through to the cask
binary, while `mise ls` reported a version that was not the one running.

`install.yaml` uninstalls it and reshims. `claude doctor` is the tool that
reports this class of problem; upstream documents it as "conflicting
installations".

## macOS only

`topic_os: [Darwin]`. Homebrew casks are macOS-only, and Claude Code on Debian
installs from a signed apt repository — a different mechanism needing sudo, a
GPG keyring and a repo file. That is a separate piece of work rather than a
conditional here.

## Teardown

`--tags remove` uninstalls both casks. User data is guarded:

- `claude_code_remove_config` — `brew uninstall --zap`, which trashes
  `~/.claude.json*`, `~/.config/claude`, `~/.local/share/claude` and
  `~/.cache/claude`: credentials, settings and session history. Off by default.

```bash
ansible-playbook apps/claude-code/playbook.yaml --tags remove
ansible-playbook apps/claude-code/playbook.yaml --tags remove \
  -e claude_code_remove_config=true
```

The VS Code extension, the JetBrains plugin and the desktop app also write
`~/.claude/`, so zapping while any of them remain installed removes state they
still use.

## First run on a new machine

1. Provision homebrew.
2. `./run-role.sh claude-code install`
3. Run `claude` and log in — credentials are machine-local by design.
