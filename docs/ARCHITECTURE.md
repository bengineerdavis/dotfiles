# Dotfiles Architecture

## The Stack

```
chezmoi          ← driver: manages dotfiles, triggers Ansible
  └── Ansible    ← provisioner: installs packages, sets up system state
        └── zsh  ← runtime: dynamic shell config via topic sourcing
```

**chezmoi** owns config files and symlinks (`~/.config/*`).  
**Ansible** owns packages and system state.  
**zsh** sources topic shell files at runtime — no Ansible involvement in shell setup.

These three never overlap. If you're writing a symlink task in Ansible, it belongs in chezmoi. If you're writing shell config in chezmoi, it belongs in `files/zsh/`.

---

## Repository Layout

```
dotfiles/
├── playbook.yaml          # parent playbook — entry point for all provisioning
├── migrate-to-roles.sh    # migration tool — upgrades topics to role structure
├── init-config.sh         # scaffolding tool — creates new topics from template_dir
├── template_dir/          # canonical structure — source of truth for all topics
├── apps/                  # one subdirectory per topic (app or system role)
│   ├── homebrew/          # system role
│   ├── apt/               # system role
│   ├── docker/            # system role
│   └── mise/              # topic role (example)
└── zsh/                   # global zsh config (path, completion, aliases, fpath)
```

---

## Topic Structure

Every directory under `apps/` is a self-contained Ansible role:

```
apps/<topic>/
├── playbook.yaml          # standalone runner — run this topic independently
├── tasks/
│   ├── main.yaml          # router — imports subtasks by tag
│   ├── install.yaml       # package installation, explicit per OS/package manager
│   └── remove.yaml        # uninstall, mirrors install structure
├── files/
│   └── zsh/               # shell config files, sourced dynamically by zsh
├── defaults/
│   └── main.yaml          # role default variables (lowest precedence)
├── vars/
│   └── main.yaml          # role variables (higher precedence than defaults)
└── templates/             # Jinja2 templates (if needed)
```

System roles (`homebrew`, `apt`, `docker`) extend this with additional subtasks:

```
apps/<system-role>/tasks/
├── main.yaml              # router — imports all subtasks
├── bootstrap.yaml         # ensure the package manager exists (confirmed, never silent)
├── prerequisites.yaml     # core tools required before topic installs
├── upgrade.yaml           # system-wide upgrade (no topic involvement)
├── install.yaml           # install this role's own packages
└── remove.yaml            # remove this role's own packages
```

---

## Tag Hierarchy

Tags control which tasks run. They compose:

| Tag             | What runs                                              |
|-----------------|--------------------------------------------------------|
| `provision`     | Full fresh machine: bootstrap → prerequisites → upgrade → install |
| `bootstrap`     | Ensure package managers exist. Confirmed, never silent |
| `prerequisites` | Core tools (git, curl, xcode-cli, etc.). Idempotent   |
| `upgrade`       | System-level upgrades only. No topic installs          |
| `install`       | All topic package installs. Assumes env is ready       |
| `remove`        | Explicit uninstall only. Never part of provision       |

```
provision
└── runs in order:
    ├── bootstrap      (homebrew/apt/docker)
    ├── prerequisites  (homebrew/apt)
    ├── upgrade        (homebrew/apt)
    └── install        (all topics)
```

`remove` is never implied by any other tag. It must be called explicitly.

---

## Package Manager Philosophy

Each topic is explicit about which package manager it uses. No abstraction layer.  
Use `when:` conditions to guard per OS:

```yaml
- name: "Install mise via Homebrew (macOS)"
  community.general.homebrew:
    name: mise
    state: present
  when: ansible_facts['os_family'] == 'Darwin'

- name: "Install mise via apt (Linux)"
  ansible.builtin.apt:
    name: mise
    state: present
  become: true
  when: ansible_facts['os_family'] == 'Debian'
```

This keeps each topic self-contained and makes multi-OS support explicit and auditable.

---

## chezmoi as Driver

chezmoi is the entry point on a new machine:

```
chezmoi apply
  └── triggers ansible-playbook playbook.yaml --tags provision
        ├── bootstraps package managers
        ├── installs prerequisites
        ├── upgrades existing environment
        └── installs all topic packages
```

chezmoi handles its own dotfile state (symlinks, config templates) independently.  
Ansible handles everything chezmoi cannot: package installation, system state, service setup.