# Git

Owns the Git package as a fleet prerequisite on Darwin and Debian.

| Concern | Owner |
| --- | --- |
| Git package presence | this topic, in `tasks/prerequisites.yaml` |
| Homebrew and apt package upgrades | the system package-manager topics |
| Global Git configuration, excludes, and commit-message guidance | chezmoi, under `home/` |
| git-ai and its shell integration | `DOT-134`, not this base topic |

`topic_provides: [git]` lets gita and Chrome declare Git as a dependency. No
`homebrew` requirement is declared: that would make this topic unschedulable
on Debian. Each package task has its own OS guard.

## Install and upgrade

The parent playbook discovers this topic automatically. A full provisioning
run installs Git during the prerequisites phase. Homebrew and apt continue to
upgrade all their managed packages; this topic does not add a second upgrade
path.

```sh
ansible-playbook playbook.yaml --tags provision
```

## Removal is deliberately restricted

Git is shared by gita, Chrome, and the operator's repositories. Ordinary
`--tags remove` leaves it installed. Removal additionally requires:

```sh
ansible-playbook playbook.yaml --tags remove -e git_remove_package=true
```

Even then, removal is skipped when any other topic requires Git. Running the
standalone playbook has no parent-built `requires_map`, so it also leaves Git
installed rather than assume the package is unshared.

## Configuration

`home/dot_gitconfig.tmpl` retains the existing chezmoi identity prompts and
points at `~/.gitignore_global` and `~/.commit-message-template`. The latter
contains comments only: Git supplies no reusable commit message. See
[git-commit](https://git-scm.com/docs/git-commit) for template and cleanup
behavior.

The `~/.git-template` directory remains operator-owned machine state. Its
retired shim and the follow-up check are tracked in `DOT-316`, outside this
configuration-capture task.
