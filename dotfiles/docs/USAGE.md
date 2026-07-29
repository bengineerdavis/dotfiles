# Usage

Day-to-day commands for provisioning, running individual topics, adding
topics, and maintenance. For how the pieces fit together see
[ARCHITECTURE.md](ARCHITECTURE.md); for the per-topic contract see
[CONVENTIONS.md](CONVENTIONS.md).

Ansible is a mise-managed tool, so commands below assume it is on `PATH`
(via `mise exec` or an activated mise shell). The playbooks run from
`~/dotfiles`.

## Bootstrap a new machine

```bash
# chezmoi installs itself, clones the repo, and applies dotfiles:
sh -c "$(curl -fsLS get.chezmoi.io)" -- init --apply git@github.com:bengineerdavis/dotfiles.git

# then provision system state with Ansible:
ansible-playbook playbook.yaml --tags provision
```

## Whole-machine runs (parent playbook)

```bash
ansible-playbook playbook.yaml --tags provision   # bootstrap+prereqs+upgrade+install, all topics
ansible-playbook playbook.yaml --tags upgrade     # refresh everything
ansible-playbook playbook.yaml --tags install     # install all topics
ansible-playbook playbook.yaml                    # no tags → provision (never removes)
ansible-playbook playbook.yaml --tags remove      # uninstall all topics (deliberate)
```

Add `--check --diff` to any of these for a no-op dry run that reports what
*would* change without applying it.

## Single-topic runs (standalone)

Each topic has a standalone runner. A bare run does `provision`; `remove` is
opt-in (tagged `never`):

```bash
ansible-playbook apps/<topic>/playbook.yaml --tags install    # install just this topic
ansible-playbook apps/<topic>/playbook.yaml                   # provision just this topic
ansible-playbook apps/<topic>/playbook.yaml --tags remove     # uninstall just this topic

# convenience wrapper (adds -vv and the inventory):
./run-role.sh <topic> [tag]
```

> Always scope real runs with a tag (`--tags install` is the common one).
> `remove` never runs unless you ask for it explicitly.

## Adding a topic

```bash
./init-config.sh my-app          # scaffolds apps/my-app/ from template_dir
# then fill in:
#   apps/my-app/topic.yml               (name, provides/requires, os, tier)
#   apps/my-app/tasks/install.yaml      (install steps)
#   apps/my-app/tasks/remove.yaml       (matching teardown — required)
```

The scaffold ships all five lifecycle files plus a router that already tags
`remove` as `[remove, never]`, so a new topic is safe to run standalone
immediately. See [CONVENTIONS.md](CONVENTIONS.md) for the file/`topic.yml`
contract and the CRUD-ownership invariant (anything you create must have a
matching teardown in `remove.yaml`).

## Maintenance

```bash
./update.sh              # upgrade pass; prompts for profile on first run
./update.sh minimal      # apps only
./update.sh full         # apps + heavy attachments (e.g. Ollama models)
```

`update.sh` upgrades Ansible out-of-band first (it can't safely swap its own
venv mid-run), then runs the parent playbook with `--tags upgrade,<profile>`.
A user crontab (`apps/cron/`) runs this on a schedule.

## Testing

```bash
bats test/               # BATS shell-script suite (also triggered by git hooks)
```

## Verifying without changing anything

```bash
ansible-playbook apps/<topic>/playbook.yaml --syntax-check       # structure/imports resolve
ansible-playbook apps/<topic>/playbook.yaml --list-tasks         # task plan + tag routing
ansible-playbook apps/<topic>/playbook.yaml --check --tags provision   # dry run, reports would-be changes
```
