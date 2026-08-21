# Contributing

## Rules

**1. One concern per layer.**

| Layer   | Owns                                      | Does not own                        |
|---------|-------------------------------------------|-------------------------------------|
| chezmoi | Dotfiles, symlinks, config templates      | Package installs, system state      |
| Ansible | Package installs, system state            | Dotfiles, symlinks, shell config    |
| zsh     | Shell runtime config (aliases, env, path) | Package installs, dotfile state     |

If you find yourself writing a symlink task in Ansible, stop — it belongs in chezmoi.  
If you find yourself writing `brew install` in a shell script, stop — it belongs in Ansible.

---

**2. Be explicit about package managers.**

No abstraction. No `install_method` variables. Use `when:` per block:

```yaml
# ✅ correct
- name: "Install ripgrep via Homebrew (macOS)"
  community.general.homebrew:
    name: ripgrep
    state: present
  when: ansible_facts['os_family'] == 'Darwin'

- name: "Install ripgrep via apt (Linux)"
  ansible.builtin.apt:
    name: ripgrep
    state: present
  become: true
  when: ansible_facts['os_family'] == 'Debian'

# ❌ wrong — hides which package manager is used
- name: "Install ripgrep"
  package:
    name: ripgrep
    state: present
```

---

**3. Use fully qualified module names (FQCNs).**

```yaml
# ✅
ansible.builtin.apt
community.general.homebrew
community.general.homebrew_cask
community.docker.docker_image

# ❌
apt
homebrew
```

---

**4. Topics own install and remove only.**

Upgrade logic belongs in system roles (`homebrew`, `apt`, `docker`), not in topics.  
If you find an upgrade task in a topic's `install.yaml`, move it to the system role.

```yaml
# ❌ wrong — upgrade logic in a topic
- name: "Update Homebrew"
  community.general.homebrew:
    update_homebrew: true

# ✅ correct — topic only installs
- name: "Install my-app via Homebrew"
  community.general.homebrew:
    name: my-app
    state: present
  when: ansible_facts['os_family'] == 'Darwin'
```

---

**5. `remove.yaml` is never implied.**

Never include `remove` in `provision`, `install`, or any composite tag.  
It must always be called explicitly: `--tags remove`.

---

**6. Keep `tasks/main.yaml` as a pure router.**

No task logic in the router — only `import_tasks` with tags:

```yaml
# ✅ correct
- name: "Import install tasks"
  ansible.builtin.import_tasks: install.yaml
  tags: [install, provision]

# ❌ wrong — task logic in the router
- name: "Install my-app"
  community.general.homebrew:
    name: my-app
  tags: [install]
```

---

**7. One logical change per commit.**

The same idea as rule 1, applied to history. Not "how many files" — three questions:
is the tree working before and after (atomic), can it be reverted without
untangling something else, and can a reviewer hold it in their head?

Split a cross-platform change from a behaviour change to existing platforms:

```
# ✅ correct — the macOS fix can be reverted without losing Linux support
clamav: pass --config-file to every clamav binary
clamav: resolve config, database and binary paths per platform
clamav: enable the topic on Debian

# ❌ wrong — five concerns welded together, revert takes all or nothing
clamav: extend the topic to Debian/Ubuntu
```

Order so every intermediate state works: land the inert parts first, and the
switch that activates them (usually `topic_os`) last.

Do **not** split a mechanical change spanning many files, or a feature whose
pieces are individually dead code — a unit template without the task that
installs it is not atomic. A list of files is not a list of concerns.

Full guidance, including the language, test and model conventions, is in
`AGENTS.md` at the repo root.

---

## Adding a System Role

System roles (`homebrew`, `apt`, `docker`) follow the same topic structure  
but include additional subtasks. When adding a new package manager:

1. Create `apps/<pm>/` using `init-config.sh <pm>`
2. Add `tasks/bootstrap.yaml` — existence check + confirmed install
3. Add `tasks/prerequisites.yaml` — core tools, idempotent
4. Add `tasks/upgrade.yaml` — system-wide upgrade
5. Update `tasks/main.yaml` to import all five subtasks with correct tags
6. Add the new system role to the parent `playbook.yaml` bootstrap/prerequisites/upgrade sequence
7. Add it to `SYSTEM_ROLES` in `migrate-to-roles.sh`

Bootstrap tasks must:
- Use an explicit `stat` check — never rely on module idempotency alone
- Prompt for confirmation before installing
- Verify success after installing
- Fail loudly if something goes wrong

---

## Template Conformance

`template_dir/` is the canonical structure. `init-config.sh` copies it verbatim.  
`migrate-to-roles.sh` uses it as the reference for LLM conformance checks.

If you change the canonical structure, update `template_dir/` first,  
then run `migrate-to-roles.sh` to propagate changes to existing topics.

Do not add `tasks/bootstrap.yaml` or `tasks/prerequisites.yaml` to `template_dir/` —  
those are system-role-only files.