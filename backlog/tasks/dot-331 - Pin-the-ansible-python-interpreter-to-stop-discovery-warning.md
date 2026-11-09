---
id: DOT-331
title: Pin the ansible python interpreter to stop the discovery warning
status: To Do
created_date: 2026-11-09 00:00
labels:
- ansible
- warning
- self-healing
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
`update.sh` (and any bare `ansible-playbook` run) emits this on every run:

```
[WARNING]: Host 'localhost' is using the discovered Python interpreter at
'/home/bdavis/.local/share/mise/installs/python/3.14/bin/python3.14', but
future installation of another Python interpreter could cause a different
interpreter to be discovered.
```

Cause: the localhost play sets no `ansible_python_interpreter`, so
auto-discovery finds whichever `python3` the mise shim currently resolves to
(today 3.14.8). A future mise python change silently switches the interpreter
ansible runs modules under — exactly the drift the warning names.

Note `apps/lima/molecule/debian/.molecule/ansible.cfg` already sets
`interpreter_python = auto_silent` for its scenario; the molecule *inventory*
overrides pin `/usr/bin/python3` per-VM, which is a different concern. The root
playbook/`ansible.cfg` for the real machine carries no pin.

Fix to research before landing (see research note): pin the interpreter for the
localhost play — either `interpreter_python` in the repo `ansible.cfg`, or an
inventory/host_var `ansible_python_interpreter` — consistent with how the
deployed tree resolves python. The pin must not hardcode a per-user mise path
(that breaks on other machines); it must resolve at deploy time like the rest
of the fleet's machine-specific values.

Done when a bare `ansible-playbook -i localhost, playbook.yaml` run emits no
interpreter-discovery warning, on both the author's box and a clean machine.
<!-- SECTION:DESCRIPTION:END -->

## Research note

<!-- SECTION:RESEARCH:BEGIN -->
Research (see the DOT-330 self-healing plan) should confirm: whether
`interpreter_python` in `ansible.cfg` vs `ansible_python_interpreter` inventory
var is the correct seam; what value is portable across the mise/python and
bsd/Linux targets; and whether `auto_silent` suppresses rather than fixes (it
hides the warning without pinning — likely the wrong choice for this task).
<!-- SECTION:RESEARCH:END -->

## Acceptance Criteria

<!-- SECTION:ACCEPTANCE:BEGIN -->
- [ ] localhost play runs with no interpreter-discovery warning
- [ ] the pin resolves at deploy time (no hardcoded per-user mise path)
- [ ] verified on a non-author machine shape where python differs
<!-- SECTION:ACCEPTANCE:END -->