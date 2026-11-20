# agentsview

[agentsview](https://agentsview.io) is a local viewer for AI agent sessions:
it discovers session transcripts from every supported agent CLI on the
machine (opencode, Claude Code, Codex, Cursor, and dozens of others), indexes
them into a local SQLite archive, and serves a loopback-only web UI with
search, usage, and cost reporting. This topic installs it on both machines —
the CLI and the desktop app, each by its native channel.

## Install

| | Darwin | Debian |
|---|---|---|
| Source | `homebrew-core` cask | GitHub release `.tar.gz` + `.AppImage` |
| Mechanism | `brew install --cask agentsview` | checksum-verified fetch (API digest) → unpack CLI to `~/.local/bin`, AppImage to `~/Applications` |
| Desktop app | `AgentsView.app` in `/Applications` (part of the cask) | `AgentsView.AppImage` in `~/Applications` (toggled by `agentsview_install_desktop_appimage`, on by default) |
| CLI binary | linked into the brew `bin` by the cask | `~/.local/bin/agentsview` |
| Currency | apps/homebrew's `brew upgrade` pass | this topic (install.yaml carries the upgrade tag; the upstream `agentsview update` self-updater is deliberately unused) |
| Privilege | none | `apt install libfuse2` (once, so the AppImage can execute) and nothing else |

The Darwin cask is in `homebrew-core`, so unlike `apps/roborev` there is no
third-party tap to trust — the cask is installed with one task.

On Debian there is no Homebrew and upstream publishes no `.deb`. The two
release assets — the CLI tarball and the desktop AppImage — are fetched from
the latest GitHub release and verified against the SHA256 digests the
releases API publishes per asset, so the checksum never comes from the same
URL the file came from. Pin a release with
`-e agentsview_release_tag=v0.45.0 -e agentsview_sha256=<64 hex chars>`; a
pinned run is deterministic and needs no API call.

The AppImage lands exactly where the upstream cask targets its Linux
artifact (`$HOME/Applications/AgentsView.AppImage`), so both platforms agree
on the location. Running it needs `libfuse2`; the topic installs that
package and leaves it in place on teardown unless
`agentsview_remove_libfuse2` is flipped, because other AppImages on the box
may depend on it.

An alternative Linux route exists and was deliberately not taken: the cask
also publishes Linux AppImage artifacts, so a machine running Linuxbrew
could `brew install --cask agentsview` and get the same desktop app. This
repo's Debian box runs no Homebrew, and bootstrapping one for a single cask
is the tail wagging the dog; if Linuxbrew is ever adopted machine-wide, this
topic collapses to the cask on both platforms and the tarball/AppImage tasks
retire with it.

## Why not the upstream `curl … | bash`?

[The installer](https://agentsview.io/install.sh) downloads the same
tarball, verifies it against the same SHA256SUMS, and installs the binary to
`/usr/local/bin` (falling back to `~/.local/bin` with a `sudo mv`). Doing
those steps natively keeps the install idempotent and change-reporting, gets
a precise teardown, avoids the un-auditable pipe-to-shell, and — on Debian —
stays entirely user-owned instead of reaching for sudo. The same reasoning
applied to `apps/roborev` and `apps/ori`.

## Why not the PyPI wheel / uv route?

agentsview's PyPI wheels wrap the same Go binary — `uv tool install
agentsview` (or the pipx backend, which is uv tool install on this machine)
works and would put the CLI on PATH without this topic. It is documented
here as the route third-party contributors can take when a project vends an
agentsview dependency, but the topic deliberately installs from the release
assets instead: release digests are checked in-repo against the same asset
the user's machine runs, the wheel channels pull ~47 MB per platform for the
identical binary, and a second CLI channel would be the exact shadowing
hazard the tool-entry-ownership recipe exists to prevent. One CLI on PATH:
the one this topic owns.

## What is intentionally left alone

`~/.agentsview` — the SQLite archive of every agent session, the daemon
configuration, and the telemetry-install-id — belongs to the user. Neither
install nor `remove` touches it; retiring agentsview entirely is a manual
`rm -rf ~/.agentsview` decision.

**No mise entry, deliberately.** This topic does not add `pipx:agentsview` to
the global mise config — that would be a second CLI channel, the shadowing
hazard the tool-entry-ownership recipe exists to prevent. Measured
2026-11-09 on the author's Linux box: `pipx:agentsview` was already
installed (0.44.0 and 0.45.0) with no topic and no committed config entry
behind it, which is the ownerless channel DOT-234 tracks. Removing that
installation is the author's call; this topic neither adds to it nor
depends on it.

## Usage

```
agentsview serve           # discover sessions, start the loopback web UI
agentsview daemon start    # same, backgrounded
agentsview usage daily     # per-model spend across every agent CLI
```

The daemon binds to `127.0.0.1` only and needs no AI agent CLI to drive —
it reads session directories, it does not run agents.