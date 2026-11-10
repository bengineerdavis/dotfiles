---
id: DOT-339
title: Remove the bare top-level fact vars, then make the class fail loudly
status: To Do
created_date: 2026-11-10 04:56
labels:
- ansible
- bug
- testing
priority: high
updated_date: 2026-11-10 04:56
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A production `update.sh` run on 2026-11-09 emitted:

```
[DEPRECATION WARNING]: INJECT_FACTS_AS_VARS default to `True` is deprecated,
top-level facts will not be auto injected after the change. This feature
will be removed from ansible-core version 2.24.
Origin: /home/bdavis/dotfiles/apps/backlog/defaults/main.yaml:23:20
```

`home/dotfiles/ansible.cfg` carries no `inject_facts_as_vars` setting, so it
defaults to true and every bare top-level fact is deprecated. Measured on this
tree: 37 template expressions across 18 files under `home/dotfiles/`, plus 5
prose mentions. Breakdown: `ansible_env` 31, `ansible_hostname` 8,
`ansible_user_dir` 2, `ansible_date_time` 1. Only expressions that actually run
warn, which is why `ansible_hostname` and `ansible_date_time` stay silent today
and will not after 2.24.

Ship:

- Every bare top-level fact expression under `home/dotfiles/` migrated to the
  `ansible_facts[...]` form, across topic defaults, task files, templates,
  molecule scenarios and the playbook.
- `inject_facts_as_vars = False` in `home/dotfiles/ansible.cfg`, landed as the
  last commit of the task because it is what proves the migration complete.
- The 5 prose mentions updated to name the supported form, so the comments stop
  teaching the deprecated one.

Constraints:

- Do not migrate magic vars, which are not facts and survive 2.24:
  `ansible_check_mode`, `ansible_diff_mode`, `ansible_run_tags`,
  `ansible_skip_tags`, `ansible_managed`, `ansible_python_interpreter`,
  `ansible_password`, `ansible_failed_result`. Probed 2026-11-09 with injection
  off: those stayed defined while `ansible_env` went undefined.
- Measured 2026-11-09: `ansible_facts` holds `env`, `hostname`, `date_time` and
  `user_dir`, so those four map to `ansible_facts['env']`,
  `ansible_facts['hostname']`, `ansible_facts['date_time']` and
  `ansible_facts['user_dir']`. `ansible_user_dir` is a fact but NOT a magic var
  (`ansible_user_dir` was undefined in the probe), so the swap is required, not
  optional.
- `apps/loreai/tasks/registry-answers.yaml:37` records that `ansible_env` is
  absent in a facts-less harness. A straight swap breaks any path that runs
  without gathering facts: give those a defined-guard rather than a bare read.
- Molecule scenarios under `apps/loreai/molecule/debian-lima/` are in scope and
  carry their own `ansible_env` reads. There is one `ansible.cfg` for the whole
  tree (`home/dotfiles/ansible.cfg`); scenarios do not carry their own, so the
  flip covers every run path.
- The flip is not `deprecation_warnings = False`. Silencing the warning is the
  opposite of the goal; the class must fail closed.
- Deployed-tree change: `chezmoi apply` is author-run from `main` after the PR
  merges, never from the branch.

Measured 2026-11-09: with `inject_facts_as_vars = False`, bare
`{{ ansible_env.HOME }}` fails with "`'ansible_env'` is undefined" while
`{{ ansible_facts['env']['HOME'] }}` resolves.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 No template expression under home/dotfiles/ reads a bare injected fact var: a scan for ansible_env, ansible_hostname, ansible_date_time and ansible_user_dir in .yaml, .yml and .j2 files returns no expression hits.
- [ ] #2 home/dotfiles/ansible.cfg sets inject_facts_as_vars = False, and that setting lands in its own commit so it can be reverted alone.
- [ ] #3 Magic vars named in the Constraints still work after the flip: a run exercising ansible_check_mode, ansible_run_tags and ansible_python_interpreter reaches them without an undefined-variable error.
- [ ] #4 Every facts-less code path that read ansible_env has a defined-guard, so a run without gather_facts produces a named message instead of an undefined-variable traceback.
- [ ] #5 The five prose mentions name the ansible_facts form, so no comment teaches the deprecated one.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->

<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
<!-- DOD:END -->
