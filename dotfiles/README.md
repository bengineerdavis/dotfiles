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

## What's new

### Claude Code
A dedicated Ansible role (`apps/claude-code/`) installs and manages
[Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview) — Anthropic's
terminal-based agentic coding assistant. The role supports three install methods
(native binary, npm, Homebrew), syncs `~/.claude/settings.json` from the dotfiles
repo, wires the binary into shell PATH, and installs the VS Code extension. Run it
standalone with:

```bash
ansible-playbook apps/claude-code/claude_code.yml
# Switch install method:
ansible-playbook apps/claude-code/claude_code.yml -e "install_method=npm"
# Update only:
ansible-playbook apps/claude-code/claude_code.yml --tags update
```

### LLM scripts (`~/bin`)
A growing collection of shell and Python scripts that wrap the
[`llm`](https://llm.datasette.io/) CLI tool for day-to-day AI workflows:

| Script | What it does |
|---|---|
| `mailbox-llm` | Processes support-inbox emails; refactored into Python with timer support |
| `triage` | Assesses inbound support requests from first-reply email contents |
| `summarize-email` | Summarizes customer outreach and first replies |
| `bashed` | Wraps `llm` to attach text and binary files to a prompt via glob patterns |
| `fuzzy-model` | Interactive fuzzy search-and-select over available LLM models |

`llm`, `uv`, and `uvx` are all managed as global [mise](https://mise.jdx.dev/) tools
(see `apps/mise/`).

### Testing — BATS
A [BATS](https://github.com/bats-core/bats-core) (Bash Automated Testing System)
suite lives under `test/` and covers shell scripts by convention across all
subdirectories. Git hooks trigger the suite automatically via
[prek](https://github.com/azer/prek), which is installed as a global mise tool.

```bash
# Run the full suite manually:
bats test/
```

### Scheduled maintenance
A user-level crontab (`apps/cron/`) runs two jobs:

- **System update** — `ansible-playbook playbook.yaml --tags update` on a schedule,
  keeping packages, mise tools, and Ollama models current without manual intervention.
- **Trash cleanup** — prunes stale files from `~/` via
  [trash-cli](https://github.com/andreafrancia/trash-cli) so the home directory
  stays tidy.

### Ollama model management
The main `playbook.yaml` now auto-updates all locally installed
[Ollama](https://ollama.ai/) models on every run. A separate helper script
handles bulk-pulling new models. Completions are installed to
`~/.zsh_completions/` and sourced by `.zshrc` automatically.

### CLI quality-of-life
- **`smart_wrap`** — reusable shell function that pipes any CLI's `--help` output
  through [bat](https://github.com/sharkdp/bat) for syntax-coloured help menus.
  Used by the `cz` (chezmoi) wrapper and others.
- **`hbat`** — adds colour to any CLI's output in the terminal.
- **Chezmoi wrapper** (`cz`) — thin alias around `chezmoi` that ensures the help
  menu is always rendered with colour via `smart_wrap`.

---

## Structure

```
dotfiles/
├── playbook.yaml           # Ansible entry point (dynamically loads topic roles)
├── ansible.cfg             # Ansible configuration
├── init-config.sh          # scaffold a new topic from template_dir
├── migrate-to-roles.sh     # migrate old topic structure to current standard
├── update.sh               # run Ansible update pass (also called by cron)
├── template_dir/           # canonical topic template (role layout)
├── test/                   # BATS bash test suite
├── apps/                   # one subdirectory per topic
│   ├── homebrew/           # system role: macOS package manager
│   ├── apt/                # system role: Linux package manager
│   ├── mise/               # runtime version manager + global tool registry
│   ├── ollama/             # local LLM runtime + model management
│   ├── claude-code/        # Claude Code CLI + VS Code extension
│   ├── cron/               # scheduled system maintenance jobs
│   ├── trash-cli/          # safe-delete + scheduled cleanup
│   ├── tmux/               # terminal multiplexer config
│   ├── starship/           # cross-shell prompt
│   ├── ghostty/            # terminal emulator config (symlinked)
│   ├── visual-studio-code/ # VS Code settings + extensions
│   └── */                  # topic roles: one per tool or concern
├── zsh/                    # global zsh config
└── docs/                   # architecture, usage, contributing guides
```

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

## Docs

- [Architecture](docs/ARCHITECTURE.md) — stack overview, topic structure, tag hierarchy
- [Usage](docs/USAGE.md) — commands for provisioning, adding topics, day-to-day use
- [Contributing](docs/CONTRIBUTING.md) — rules, patterns, and what goes where