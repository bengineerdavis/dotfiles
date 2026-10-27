# topical App Module

Installs the [topical](https://github.com/bengineerdavis/topical) CLI —
the manager for topic-structured chezmoi-Ansible dotfiles repos — as a
**uv tool** from the git remote.

uv tool owns the environment and the `~/.local/bin/topical` shim; this
topic owns presence (`uv tool install` when absent), currency
(`uv tool upgrade` — no system role reaches uv tools) and teardown
(`uv tool uninstall`).

## Links

- [project git repository](https://github.com/bengineerdavis/topical)
