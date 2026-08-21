# ClamAV

On-demand antivirus plus a daily scheduled scan of `$HOME`. Codifies what used to be an
unmanaged hand-rolled setup in `~/.clamav_automation/`.

## Installation

Handled by the topic — the package manager is guarded in-task, so one command
covers both platforms:

```bash
./run-role.sh clamav
```

Installs `clamav` via Homebrew on macOS and via apt on Debian/Ubuntu. On Linux it
installs `clamav` only, **not** `clamav-daemon`: that package runs an always-on
system clamd, which is exactly what this topic avoids (see below).

## Usage

```bash
./run-role.sh clamav              # provision (install + schedule)
./run-role.sh clamav upgrade      # refresh signature databases now
./run-role.sh clamav remove       # tear everything down
```

Ad-hoc scanning, once the role has run:

```bash
clamscan  -r ~/Downloads          # works any time; loads signatures each run (~4s startup)
clamdscan -r ~/Downloads          # ~25x faster, but needs clamd up (see below)
```

## Design: clamd is ephemeral

clamd holds the whole signature database in memory — about **1.3 GB resident**. Keeping
it up all day to make ad-hoc scans fast is a bad trade on a laptop, so the daily agent
starts it, scans, and shuts it down again.

Consequence: for most of the day `clamdscan` will fail because nothing is listening, and
`clamscan` is the one to reach for. Tools that prefer the daemon should fall back to
`clamscan` on their own.

## What this topic owns

| Artefact | Path (macOS) | Path (Linux) |
|---|---|---|
| package | `clamav` via Homebrew | `clamav` via apt |
| daemon config | `<brew_prefix>/etc/clamav/clamd.conf` | `~/.clamav_automation/clamd.conf` |
| updater config | `<brew_prefix>/etc/clamav/freshclam.conf` | `~/.clamav_automation/freshclam.conf` |
| signature database | `<brew_prefix>/var/lib/clamav/` | `~/.clamav_automation/db/` |
| automation directory | `~/.clamav_automation/` | same |
| scan script | `~/.clamav_automation/daily_scan.sh` | same |
| third-party feed config | `~/.clamav_automation/fangfrisch.conf` | same |
| scheduler | `~/Library/LaunchAgents/com.user.clamscan.plist` | `~/.config/systemd/user/clamav-scan.{service,timer}` |

### Why the Linux paths differ

Homebrew's prefix is user-writable, so on macOS the configs sit where clamav
already looks. Debian's `/etc/clamav` is root-owned and the distro package ships
its own `clamd.conf` and `freshclam.conf` there, driving system-wide
`clamav-daemon` and `clamav-freshclam` services.

Rather than run as root and fight those services for the same files, on Linux
this topic keeps its config and signature database inside the automation
directory it already owns, and passes `--config-file` explicitly to every binary.
The distro's copies are left untouched, so apt's services and this topic's
user-owned scan can coexist without either editing the other's state.

`--config-file` is passed on **both** platforms. Relying on the compiled-in
default location is the same class of bug as the socket mismatch described below:
it works until something else writes a config to that path.

All of it is torn down by `--tags remove`, per the CRUD invariant in
`docs/CONVENTIONS.md`.

### Deliberate convention exception

`docs/CONVENTIONS.md` says config belongs to chezmoi. This topic renders its own config
anyway, for two reasons:

1. `clamd.conf` and `freshclam.conf` live under `<brew_prefix>/etc`, outside `$HOME`,
   where chezmoi does not reach.
2. `clamd.conf` and `daily_scan.sh` must agree on the socket path exactly. Rendering
   both from one Ansible variable makes disagreement impossible — and disagreement is
   precisely what broke the unmanaged setup (below).

If that exception should instead be written into `CONVENTIONS.md`, move it there and
delete this section.

### Not owned here

`fangfrisch` is installed by **apps/mise**, which declares `"pipx:fangfrisch" = "latest"`
in `files/config.toml`. This topic configures and invokes it but never installs it, so
there is no duplicated ownership. `--tags remove` leaves the binary alone; drop it from
the mise config if you want it gone.

Lynis used to be run from `daily_scan.sh` on the first of each month. It now has its own
topic: **apps/lynis**.

## Linux: the timer needs a session

The macOS agent is per-user, so the Linux side is a systemd **user** timer to
match. A user timer only fires while you have a session; on an unattended host,
enable lingering once:

```bash
sudo loginctl enable-linger "$USER"
```

`install.yaml` reports this rather than changing your login behaviour for you. It
also warns if the distro's `clamav-daemon` is active, since an always-on daemon
holds the signature memory this topic exists to release — but it will not disable
another package's service on your behalf.

Inspect the schedule with:

```bash
systemctl --user list-timers clamav-scan.timer
```

### netcat matters on Debian

The scan script talks to clamd over its Unix socket with `nc -U` — that is how it
decides the daemon is alive and how it shuts it down afterwards. Debian has two
providers and only `netcat-openbsd` supports `-U`; `netcat-traditional` does not.
With the wrong one the PING fails silently, the script concludes clamd never came
up, and aborts before scanning. `prerequisites.yaml` installs the right package
and then probes the `nc` actually on `PATH`, failing loudly with the
`update-alternatives` fix if it is the wrong build.

## Two bugs this replaces

Both failed silently, because the old launchd agent sent stdout and stderr to
`/dev/null`.

**The socket path disagreed with itself.** `clamd.conf` declared the socket at
`~/.clamav_automation/clamd.ctl`, but the script waited on and shut down via
`/tmp/clamd.socket`, which never exists. So every run burned the full 30-second wait
loop, and this line never did anything:

```bash
echo "SHUTDOWN" | nc -U /tmp/clamd.socket
```

The comment above it read *"Gracefully terminate clamd to instantly reclaim 1GB+ RAM"*.
It never did: clamd was found resident for **18 days holding 1.3 GB**. Both files now
render the path from `clamav_socket` in `vars/main.yaml`.

**Third-party signatures stopped updating.** The script called `freshclam` by absolute
path but `fangfrisch` bare. launchd gives a job a minimal `PATH` and no shell profile,
and fangfrisch lives at `~/.local/share/mise/shims/fangfrisch`, so it was never found.
Official signatures stayed current while the SaneSecurity/urlhaus/interserver feeds went
weeks without a refresh. Every binary is now absolute, and the agent sets `PATH` too.

`install.yaml` also stops a stale resident clamd once, on the run where `clamd.conf`
changes, so the leaked memory is reclaimed without waiting for the next scan.

## Heuristic alerting

`clamd.conf` deliberately enables `AlertOLE2Macros`, `AlertEncrypted`,
`AlertBrokenExecutables` and friends. These are **anomaly rules, not malware
signatures** — they fire routinely on truncated downloads and password-protected
archives. Worth having for attachments of unknown provenance, as long as you read them
as "unusual" rather than "infected". Findings appear as `Heuristics.*` in `scan.log`.

## Logs

| File | Contents |
|---|---|
| `~/.clamav_automation/run.log` | what each maintenance run did, and every failure |
| `~/.clamav_automation/scan.log` | clamdscan output; infected files only |
| `~/.clamav_automation/agent.log` | whatever launchd itself captures |

`run.log` and `scan.log` are rotated at `clamav_log_max_bytes` (5 MB default). The
unmanaged `scan.log` had reached 5.4 MB with no rotation.

## Tunables

See `defaults/main.yaml` — scan time, scan root, log ceiling, exclude paths, heuristic
toggle, and which fangfrisch feeds are enabled.
