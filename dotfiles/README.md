# Ben's Dotfiles

A topic-based dotfiles system built on [chezmoi](https://www.chezmoi.io/),
[Ansible](https://www.ansible.com/), and zsh — evolved significantly from
[holman/dotfiles](https://github.com/holman/dotfiles), which inspired the
original topic structure.

---

## How it works

Three tools, three concerns, no overlap:

```
chezmoi    ← drives everything: manages dotfiles, triggers Ansible
Ansible    ← provisions machines: installs packages, sets up system state
zsh        ← runtime: sources topic shell files dynamically
```

Everything under `apps/` is a topic — a self-contained unit for one tool or
concern. Each topic is a full Ansible role that can be run standalone or
loaded by the parent playbook.

→ **[Full architecture doc](docs/ARCHITECTURE.md)**

---

## Quick start

```bash
# Bootstrap a new machine via chezmoi:
sh -c "$(curl -fsLS get.chezmoi.io)" -- init --apply git@github.com:bengineerdavis/dotfiles.git

# Or run Ansible directly:
ansible-playbook playbook.yaml --tags provision
```

→ **[Usage guide](docs/USAGE.md)**

---

## Adding a topic

```bash
./init-config.sh my-app
# then edit apps/my-app/tasks/install.yaml
```

→ **[Contributing guide](docs/CONTRIBUTING.md)**

---

## From holman/dotfiles

This project started as a fork of Zach Holman's
[dotfiles](https://github.com/holman/dotfiles), which introduced the idea of
organizing shell config by topic rather than dumping everything into one long
`.zshrc`. That core idea — one directory per concern, `.zsh` files sourced
automatically — is still here and still works the same way.

What's changed is everything else. Holman's project is intentionally minimal:
shell scripts, symlinks, and a bootstrap script. That's a great starting point,
but it doesn't scale well to managing full machine provisioning across multiple
operating systems and machines.

This repo replaces the shell-script provisioning layer with Ansible, adds
chezmoi as the dotfile driver, and introduces a structured role system where
each topic owns its own install, remove, and shell config in a predictable
layout. The `.symlink` convention is gone — chezmoi handles that. The
`script/bootstrap` and `dot` scripts are gone — Ansible handles that.

If you want something simpler that doesn't need Ansible or chezmoi, Holman's
original project is the right starting point.

---

## Structure

```
dotfiles/
├── playbook.yaml        # Ansible entry point
├── init-config.sh       # scaffold a new topic from template_dir
├── migrate-to-roles.sh  # migrate old topic structure to current standard
├── template_dir/        # canonical topic template
├── apps/                # one subdirectory per topic
│   ├── homebrew/        # system role: macOS package manager
│   ├── apt/             # system role: Linux package manager
│   ├── docker/          # system role: container runtime
│   └── */               # topic roles: one per tool or concern
└── zsh/                 # global zsh config
```

---

## Docs

- [Architecture](docs/ARCHITECTURE.md) — stack overview, topic structure, tag hierarchy
- [Usage](docs/USAGE.md) — commands for provisioning, adding topics, day-to-day use
- [Contributing](docs/CONTRIBUTING.md) — rules, patterns, and what goes where