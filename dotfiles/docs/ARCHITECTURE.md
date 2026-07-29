# Architecture

Stack overview, topic structure, and the tag hierarchy. For the exact
per-topic contract (file layout, `topic.yml` schema, dependency resolution,
the CRUD-ownership invariant) see [CONVENTIONS.md](CONVENTIONS.md).

## Three tools, three concerns

```
chezmoi    ← driver: manages dotfiles in $HOME, renders OS-specific templates,
             and is the entry point for bootstrapping a machine
Ansible    ← provisioner: installs packages and sets up system state
zsh        ← runtime: sources each topic's shell fragments dynamically
```

They do not overlap. chezmoi owns files in `$HOME`; Ansible owns installed
software and system state; zsh owns interactive-shell wiring. The Ansible tree
itself is deployed by chezmoi to `~/dotfiles`, which is where playbooks run
from (`$ZSH="$HOME/dotfiles"`).

## Topics are Ansible roles

Everything under `apps/` is a **topic** — a self-contained Ansible role for one
tool or concern. Each topic can run standalone (`apps/<topic>/playbook.yaml`) or
be loaded by the parent `playbook.yaml`. Required files per topic:

```
apps/<topic>/
├── topic.yml            # metadata (name, provides/requires, os, tier)
└── tasks/
    ├── main.yaml        # lifecycle router — imports the five files below by tag
    ├── bootstrap.yaml   # bring the tool into existence on a fresh machine
    ├── prerequisites.yaml
    ├── upgrade.yaml
    ├── install.yaml
    └── remove.yaml
```

App-tier topics usually leave `bootstrap`/`prerequisites`/`upgrade` as no-op
stubs — the package-manager tier covers them.

## Discovery, tiers, and OS gating

The parent playbook discovers topics dynamically: it finds every `topic.yml`,
reads its metadata, and orders execution by `topic_tier`:

| Tier              | Purpose                                        | Examples                    |
|-------------------|------------------------------------------------|-----------------------------|
| `pkg-manager`     | Foundational system installer                  | `apt`, `homebrew`, `docker` |
| `runtime-manager` | Manages a set of versioned tools/models        | `mise`, `ollama`            |
| `app`             | Normal application, no subordinate state       | everything else             |

Within a tier, topics run alphabetically. Each topic declares the OS families
it supports via `topic_os` (`Darwin`, `Debian`); the parent playbook skips
topics that don't apply to the current host. This is how one capability can
have different providers per OS — e.g. `docker` is provided by `apps/docker`
(apt engine) on Linux and by `apps/rancher-desktop` (Homebrew cask) on macOS.

Dependencies between topics are expressed with `topic_provides` /
`topic_requires` and resolved by the parent playbook before install; see
[CONVENTIONS.md](CONVENTIONS.md#dependency-resolution).

## Lifecycle tags

`tasks/main.yaml` is a pure router that imports the five lifecycle files, each
tagged so a run can target a phase:

| Tag             | Runs                                                        |
|-----------------|-------------------------------------------------------------|
| `bootstrap`     | first-time setup of a system tool                           |
| `prerequisites` | core deps before topics install                             |
| `upgrade`       | refresh installed state                                     |
| `install`       | install the topic                                           |
| `provision`     | bootstrap + prerequisites + upgrade + install               |
| `remove`        | teardown — tagged `never`, runs **only** with `--tags remove` |

The `never` tag on `remove` makes a bare (untagged) run safe: it does
`provision` and never tears a topic down. Uninstalling is always a deliberate
`--tags remove`. New topics inherit this from `template_dir`.

## zsh runtime

`~/.zshrc` is a thin loader (deployed by chezmoi from a template). It sources
each topic's canonical shell fragments — `apps/<topic>/files/zsh/*.zsh` plus the
top-level `zsh/*.zsh` — exactly once, keeping `PATH`/`fpath` deduplicated. A
topic's runtime shell wiring lives in those fragments; its install/system state
lives in `tasks/`.

## See also

- [CONVENTIONS.md](CONVENTIONS.md) — the full per-topic contract
- [USAGE.md](USAGE.md) — day-to-day commands
