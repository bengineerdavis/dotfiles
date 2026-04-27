# Usage

## Fresh Machine

```bash
# chezmoi will eventually drive this — for now, run directly:
ansible-playbook playbook.yaml --tags provision
```

This runs in order: bootstrap → prerequisites → upgrade → install.  
You will be prompted before any package manager is installed.

---

## Common Commands

```bash
# Upgrade all packages (brew, apt) without reinstalling topics
ansible-playbook playbook.yaml --tags upgrade

# Install all topic packages (assumes env is already set up)
ansible-playbook playbook.yaml --tags install

# Run a single topic
ansible-playbook apps/mise/playbook.yaml
ansible-playbook apps/mise/playbook.yaml --tags install
ansible-playbook apps/mise/playbook.yaml --tags remove

# Bootstrap package managers only
ansible-playbook playbook.yaml --tags bootstrap

# Dry run — see what would change without making changes
ansible-playbook playbook.yaml --tags provision --check
```

---

## Adding a New Topic

```bash
# 1. Scaffold from template
./init-config.sh my-app

# 2. Edit the generated files
#    tasks/install.yaml  ← add your package installs
#    tasks/remove.yaml   ← add your uninstall steps
#    files/zsh/          ← add any shell config files

# 3. Run it standalone to test
ansible-playbook apps/my-app/playbook.yaml --tags install
```

The scaffold copies `template_dir/` into `apps/my-app/`. All `<topic>` placeholders  
are replaced with your topic name.

---

## Migrating an Existing Topic

If a topic still uses the old flat `tasks.yaml` structure:

```bash
# Preview what would change (no LLM calls execute)
./migrate-to-roles.sh --dry-run my-app

# Migrate a single topic
./migrate-to-roles.sh my-app

# Migrate all topics
./migrate-to-roles.sh

# Verbose output
./migrate-to-roles.sh --verbose my-app
```

The script uses local LLMs to split tasks, resolve conflicts, and check conformance  
against `template_dir`. Review `migration-backups/<topic>/migration-report.md`  
for any decisions that need human verification.

```bash
# After reviewing backups:
rm -rf migration-backups/
```

---

## Shell Config

Topic shell files live in `apps/<topic>/files/zsh/` and are sourced automatically  
by zsh at runtime. No Ansible tasks needed for shell setup.

```
apps/mise/files/zsh/
├── init.zsh        # sourced on shell init
├── env.zsh         # environment variables
├── alias.zsh       # aliases
└── path.zsh        # PATH additions
```

Global zsh config (shared across all topics) lives in `zsh/` at the repo root.

---

## Dotfile Config

chezmoi manages all dotfile state: symlinks, config file templates, secrets.  
Do not write symlink or config-file tasks in Ansible — put them in chezmoi instead.

```bash
# Apply chezmoi dotfiles
chezmoi apply

# See what chezmoi would change
chezmoi diff
```