# Lynis

Monthly system hardening audit.

## Installation

Handled by the topic — the package manager is guarded in-task, so the same command
works on either platform:

```bash
./run-role.sh lynis
```

Installs `lynis` via Homebrew on macOS and via apt on Debian/Ubuntu.

## Usage

```bash
./run-role.sh lynis           # install + schedule
./run-role.sh lynis remove    # tear down
lynis audit system            # ad-hoc, interactive
```

## Why this is its own topic

The audit used to run from inside `apps/clamav`'s `daily_scan.sh`, gated on
`[ "$(date +%d)" = "01" ]`. That violated the CRUD ownership rule in
`docs/CONVENTIONS.md` — an unrelated lifecycle riding another topic's schedule — and it
inherited that script's `/dev/null` output, so failures were invisible.

It now has its own scheduler — a launchd agent using launchd's native monthly `Day`
key on macOS, and an equivalent systemd **user** timer on Linux — plus its own log
directory and log retention. On first run, `install.yaml` copies the old
`~/.clamav_automation/lynis_monthly_audit.log` to `~/.lynis/audit-legacy.log` so the
existing history survives `apps/clamav --tags remove`.

## What this topic owns

| Artefact | Path |
|---|---|
| package | `lynis` via Homebrew (macOS) or apt (Debian) |
| state directory | `~/.lynis/` |
| audit script | `~/.lynis/monthly_audit.sh` |
| launchd agent (macOS) | `~/Library/LaunchAgents/com.user.lynis-audit.plist` |
| systemd units (Linux) | `~/.config/systemd/user/lynis-audit.{service,timer}` |
| reports | `~/.lynis/audit-YYYY-MM-DD.log` (newest `lynis_keep_logs` kept) |

## Linux: the timer needs a session

The macOS agent is per-user, so the Linux side is a systemd **user** timer to match —
same ownership, no root. The catch is that a user timer only fires while you have a
session. On an unattended host, enable lingering once:

```bash
sudo loginctl enable-linger "$USER"
```

`install.yaml` checks this and prints the command if it is missing, rather than
changing your login behaviour on your behalf. Inspect the schedule with:

```bash
systemctl --user list-timers lynis-audit.timer
```

## Note on privileges

The agent runs as your user, so Lynis skips checks needing root and says so in the
report. This matches the previous behaviour. Run `sudo lynis audit system` by hand for a
complete picture.
