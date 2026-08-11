# Lynis

Monthly system hardening audit.

## Installation

```bash
brew install lynis
```

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

It now has its own launchd agent using launchd's native monthly `Day` key, its own log
directory, and log retention. On first run, `install.yaml` copies the old
`~/.clamav_automation/lynis_monthly_audit.log` to `~/.lynis/audit-legacy.log` so the
existing history survives `apps/clamav --tags remove`.

## What this topic owns

| Artefact | Path |
|---|---|
| formula | `lynis` via Homebrew |
| state directory | `~/.lynis/` |
| audit script | `~/.lynis/monthly_audit.sh` |
| launchd agent | `~/Library/LaunchAgents/com.user.lynis-audit.plist` |
| reports | `~/.lynis/audit-YYYY-MM-DD.log` (newest `lynis_keep_logs` kept) |

## Note on privileges

The agent runs as your user, so Lynis skips checks needing root and says so in the
report. This matches the previous behaviour. Run `sudo lynis audit system` by hand for a
complete picture.
