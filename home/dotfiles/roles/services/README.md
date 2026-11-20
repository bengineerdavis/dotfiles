# `roles/services` — shared per-user service units

A topic that installs a daemon owns the unit that keeps it running, in the same
change as the thing that creates it (`spec.md` § Layering — teardown changes
with the thing it creates). This role is the machinery for that: one launchd
agent on macOS, one systemd **user** unit on Debian, rendered from shared
templates, converged the same way everywhere.

It exists because the same launchd bug was written into every daemon topic and
into `docs/TOPIC-RECIPES.md`, and was rediscovered the hard way (DOT-343,
2026-11-17). The convergence order lives in one tested place now.

## Calling it

Import **one phase at a time**, by name:

```yaml
# the install phase
- name: "backlog: install the daemon service"
  ansible.builtin.import_role:
    name: "roles/services"
    tasks_from: install.yaml
  vars:
    service_label: "com.backlog-py.daemon"
    service_description: "backlog-md-py singleton daemon (queue serialization)"
    service_program_arguments:
      - "{{ backlog_bin }}"
      - "daemon"
      - "run"
      - "--foreground"
      - "--host"
      - "{{ backlog_daemon_host }}"
      - "--port"
      - "{{ backlog_daemon_port }}"
    service_health_command: "{{ backlog_bin }} daemon status --json"
  tags: [backlog, install, upgrade]
```

```yaml
# the teardown phase, in a file tagged `never`
- name: "backlog: remove the daemon service"
  ansible.builtin.import_role:
    name: "roles/services"
    tasks_from: remove.yaml
  vars:
    service_label: "com.backlog-py.daemon"
  tags: [backlog, remove, never]
```

**Do not import the whole role.** Doing so pulls in both phases, and the
importing task's tags are inherited by everything underneath — so
`--tags install` selects the teardown as well. `never` does not save you:
`never` skips a task only when nothing else selects it, and the inherited
`install` tag does select it.

Measured 2026-11-20: a tagged install run stopped the daemon, deleted its
plist, and left a replacement whose `ProgramArguments` was `[shim]` alone —
because `remove.yaml`'s thinner vars re-rendered the unit last. The daemon
was down and the plist named a program with no subcommand.

`tasks/main.yaml` therefore **fails on purpose**. A caller that forgets
`tasks_from` gets a loud error naming the correct form, rather than a run that
tears down a live service. Do not delete it: a role with no `tasks/main.yaml`
is treated as having no tasks, which would turn the bug into a silent no-op.

`defaults/main.yaml` supplies every parameter, so a caller overrides only what
it cares about.

## The convergence order is the whole point

`tasks/converge.yaml` runs this sequence on macOS, and the order is load-bearing:

1. **`launchctl enable` first, unconditionally.** `launchctl disable` writes a
   **persistent** override in the user's launchd domain. It survives `bootout`
   *and reboot*; only `enable` clears it. A bootstrap of a disabled label fails
   with `Bootstrap failed: 5: Input/output error` and leaves the service down —
   and the override survives, so every later run fails identically. Gating
   `enable` behind a `bootstrap` that cannot succeed is the bug: the one command
   that fixes the state becomes unreachable exactly when it is needed.
1. **Boot out only a label launchd reports.** `launchctl print` exits 0 when
   loaded and 113 when absent; `bootout` of a missing label exits 3, so exit
   status is the wrong presence test.
1. **Wait for teardown.** `bootout` is documented as asynchronous, so a
   bootstrap issued immediately after it can see the stale registration. This
   was **not reproduced** on the reference host (0 failures in 25 attempts,
   measured 2026-11-17), so the wait is cheap insurance rather than a fix for
   an observed failure — it breaks on its first check in the normal case.
1. **Bootstrap, then prove it with a health check.** A bootstrap can return 0
   and still leave nothing running, so the exit code is not evidence.

Measured 2026-11-17 with throwaway labels, one variable at a time:

| State before the run | Old recipe    | This role |
| -------------------- | ------------- | --------- |
| absent               | PASS          | PASS      |
| loaded + running     | PASS          | PASS      |
| disabled + absent    | **FAIL rc 5** | PASS      |
| loaded + disabled    | **FAIL rc 5** | PASS      |
| twice in a row       | PASS          | PASS      |

## What the role deliberately does not do

- **No `loginctl enable-linger`.** A systemd user unit only fires while the user
  has a session. The role prints the fix and leaves the decision alone; changing
  login behaviour silently is not a provisioning run's call (`AGENTS.md`
  § Cross-platform).
- **No version-pinned paths.** `service_program_arguments` is the caller's, and
  the caller points it at a shim or a resolved-at-install path. A path under
  `mise/installs/<tool>/<version>/` breaks on the first upgrade.
- **No log deletion on teardown.** `remove.yaml` removes the unit and names the
  log directory it preserved. Logs are evidence.
- **No scheduling.** `KeepAlive` + `RunAtLoad` suit a long-running daemon. A
  one-shot or calendar job needs `StartCalendarInterval`, which is a different
  shape; those topics keep their own plist and only borrow the convergence
  rules.

## Related

- `docs/TOPIC-RECIPES.md` § service ownership — the recipe that points here.
- `docs/CROSS-PLATFORM.md` — launchd versus systemd user-timer traps.
- `apps/backlog` — the first caller, and the topic that found the bug.
