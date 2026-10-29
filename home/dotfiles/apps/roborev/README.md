# roborev

[roborev](https://roborev.io) is an automatic code-review daemon: it reviews
git commits with the AI agent CLI of your choice and keeps the review history
per repository. This topic installs the `roborev` binary on both machines.

roborev needs at least one AI agent CLI to drive. The `opencode` and
`claude-code` topics provide them.

## Install

| | Darwin | Debian |
|---|---|---|
| Source | `kenn-io/tap` Homebrew tap | GitHub release `.deb` |
| Mechanism | `brew trust` → `brew tap` → `brew install` | checksum-verified fetch → `apt install ./…deb` |
| Currency | apps/homebrew's `brew upgrade` pass | this topic (install.yaml carries the upgrade tag) |
| Destination | brew prefix `/bin` | `/usr/bin` (the one privileged step) |

macOS installs from upstream's own tap. Homebrew 7 will not load a
third-party tap's formulae until the tap is trusted, and it refuses at tap
time with `Cannot tap kenn-io/tap: invalid syntax in tap!` — a message that
names neither the cause nor the fix. The topic therefore runs
`brew trust --tap kenn-io/tap` first. The full story, including the two
trust entries teardown has to revoke, is in
[`apps/opencode/README.md`](../opencode/README.md) § "The tap must be
trusted first".

Debian fetches `roborev_<version>_linux_<arch>.deb` from the latest GitHub
release and verifies it against the SHA256 digest GitHub publishes for the
asset in the releases API response, so the checksum never comes from the
same URL the file came from. Pin a release with
`-e roborev_release_tag=v0.71.0 -e roborev_deb_sha256=<64 hex chars>`; a
pinned run is deterministic and needs no API call.

### Why not the upstream `curl … | bash`?

The installer downloads the same binary to `~/.local/bin` and checks it
against the same checksums. Doing those steps natively keeps the install
idempotent and change-reporting, and gives it a precise teardown — the same
reasoning applied to `apps/ori`. The `.deb` route additionally gets the
binary into dpkg's records, which is what the version check reads back.

### Upgrades on Debian

`apt upgrade` cannot reach a GitHub-release deb, so the topic owns its own
currency: `--tags upgrade` resolves the latest release and reinstalls only
when the installed dpkg version differs. Upstream's `roborev update`
self-updater is deliberately not used — it would replace the dpkg-managed
binary outside Ansible's knowledge and make the next run's version
comparison lie.

## What is not managed here

The daemon's configuration and the per-repository `roborev init` state
(git hooks, review database) are not touched by this topic. Wire config
through chezmoi only when there is a config worth managing — not
speculatively.

## Teardown

`--tags remove` uninstalls the binary (and on Debian, the cached `.deb`).
The tap stays unless `roborev_remove_tap=true` — it is shared
infrastructure, and untapping it would break any other formula installed
from it. Per-repository git hooks and review history are left in place; they
belong to the repositories `roborev init` was run in, not to this topic.
