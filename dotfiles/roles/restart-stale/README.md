# `roles/restart-stale` — restart what an upgrade left running

An upgrade that replaces a binary does not restart the process running it. On
2026-09-22 `apps/homebrew` upgraded ollama 0.33.3 → 0.34.3, and the
`com.ollama.server` agent kept running 0.33.3 until someone restarted it by
hand. A handler in `apps/ollama` could not have caught this, because the binary
changed in a different topic. This role checks the machine directly: if the
process started before its binary last changed, it restarts it.

## Calling it

Call it once per service or app, at the end of the topic's `install.yaml`,
tagged `upgrade` so it runs under `--tags install`, `--tags upgrade` and
`provision`. That is the `[install, upgrade]` convention in
`docs/TOPICS.md` § Currency. Putting it last means it runs after anything the
topic itself did to the binary or the service.

```yaml
- name: "Restart the ollama server if an upgrade left it on the old binary"
  ansible.builtin.import_role:
    name: "roles/restart-stale"
  vars:
    restart_stale_caller: "apps/ollama"
    restart_stale_kind: launchd
    restart_stale_launchd_label: com.ollama.server
    restart_stale_binary: "{{ ollama_bin | default('/opt/homebrew/bin/ollama') }}"
  when: ansible_facts['os_family'] == 'Darwin'
  tags: [upgrade]
```

Use `import_role`, not `include_role`. The static import keeps the role's tasks
visible to tag selection, the same reason `roles/guards` gives.

## Parameters

Each parameter has a default and a comment in `defaults/main.yaml`.

| Kind | Required | Found by | Restarted by |
|---|---|---|---|
| `launchd` (macOS) | `restart_stale_launchd_label` | PID in `launchctl list` | `launchctl kickstart -k gui/<uid>/<label>` |
| `systemd` | `restart_stale_systemd_unit`, `restart_stale_systemd_scope` (`user`/`system`) | `MainPID` from `systemctl show` | `ansible.builtin.systemd_service`, `become` for `system` scope |
| `app` (macOS) | `restart_stale_app_name` | exact executable path in `ps` | `osascript` quit, wait, then `open -a <bundle>` |

Every kind also needs `restart_stale_binary`, the executable the process runs.
For `app`, that is the bundle's main executable
(`<Name>.app/Contents/MacOS/<exe>`), and the bundle to reopen comes from that
path. Quit and reopen both target that exact bundle, rather than an app name
that may also identify a second installation.

## What counts as stale

A process is stale if it started before its binary's **ctime**. The role
resolves symlinks before it reads the ctime.

Do not use mtime, and do not use birthtime. Homebrew copies both from the bottle,
so both are days older than the install. The measurements are in the header of
`filter_plugins/restart_stale.py`. The ctime also changes on `chmod`, `chown` and
xattr changes. That can cause a restart that was not needed, which is the safe
direction to be wrong in.

| State | Action |
|---|---|
| Not running | Nothing. It starts on the new binary. |
| Running, started after the change | Nothing. |
| Running, started before the change | Restart, and report why. |
| Binary missing | Nothing. Reported. |

## Apps are never force-quit

The role asks an app to quit with the same request the Quit menu item sends. It
waits `restart_stale_quit_timeout` seconds, then reopens the app only if it
exited. If the quit fails or the app does not exit, the role reports that and
leaves the app running. It never sends a kill.

A failed process probe stops the task with an error. Only an explicit
no-such-process result permits reopening; an unreadable process table is not
evidence that the app stopped.

## Tests

```bash
uv run --with pytest --with hypothesis pytest tests/restart_stale -q
```

`test_decision.py` tests the decision as pure functions, with properties.
`test_role.py` runs this role in a real play, with stub `launchctl`,
`systemctl`, `ps`, `osascript` and `open` on `PATH`. No real service or app is
touched.
