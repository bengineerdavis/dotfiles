# `roles/guards` — shared pre-flight checks

A guard is a check that runs **before** a topic changes anything, and fails with
the fix named when the machine is not in a state the topic can act on. Topics
already do this locally — `apps/opencode/tasks/install.yaml` refuses to continue
without `brew`, `apps/chrome/tasks/git-refs-guard.yaml` refuses to fetch a tag
that moved. This role is for the checks that more than one topic needs.

## Calling one

```yaml
- name: "Guard against an unmigratable agent skills directory"
  ansible.builtin.import_role:
    name: "roles/guards"
    tasks_from: dotagents-skills-migration.yaml
  vars:
    guard_caller: "apps/<topic>"
    guard_allow_skill_dir_conflicts: "{{ <topic>_allow_skill_dir_conflicts }}"
```

`import_role` (static), not `include_role` (dynamic). The lifecycle in
`tasks/main.yaml` routes by tag, and a static import makes the guard's own tasks
visible at parse time so `--tags install` / `upgrade` / `remove` keep selecting
them without an `apply:` block. `tasks_from` is the built-in way to call one file
from a role; `defaults/main.yaml` supplies every parameter's default so a caller
overrides only what it cares about.

The role name is the path `roles/guards`, matching how the parent playbook
already names topics (`include_role: name: "apps/{{ item.topic_name }}"`). Both
resolve relative to the working directory, so — like `ansible.cfg` itself —
everything must be run from the repo root. `run-role.sh` and `update.sh` already
guarantee that.

## Writing one

- One file per check, named for what it guards, in `tasks/`.
- Every parameter gets a default and a comment in `defaults/main.yaml`.
- Prefix parameters `guard_` so a caller's `vars:` cannot collide with the
  topic's own variables.
- **Collect every problem, then fail once.** One run should report all of it,
  not one item per invocation — the same rule `docs/TOPICS.md` § Script
  dependency guards sets for `~/bin`.
- **Never repair automatically.** A guard exists because the right answer needs
  a human. Offer an explicit per-run override instead, defaulted to `false`.
- Say what has *not* happened yet ("nothing has been installed or moved"), so
  the operator knows the run stopped before doing damage rather than part-way
  through.

## Guards here

| File | Guards against |
|---|---|
| `dotagents-skills-migration.yaml` | An agent's `skills/` is still a real directory whose entry names collide with `~/.agents/skills`, so dotagents aborts mid-relocation. |
