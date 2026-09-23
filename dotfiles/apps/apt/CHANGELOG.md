# apt — changelog

This topic's own history. See `docs/TOPICS.md` § "Per-topic changelog and local
edge cases". Section names follow antsibull-changelog.

## Unreleased

### minor_changes

- 2026-09-23: signing-key repair for configured third-party repos
  (`apt_keyrings`, `tasks/keyrings.yaml`, `files/apt_keyring.py`). The keyring
  path is read from each source's `signed-by=`; the download is dearmored and
  must contain a public key, and the key IDs listed in `require_keys`, before
  anything is written. Runs before every cache refresh. Moved from deb-get,
  whose app-tier position made it run too late.

### bugfixes

- 2026-09-23: apt tasks wait `apt_lock_timeout` (300s) for the dpkg/lists lock
  instead of the module's 60s. On 2026-09-20 an idle-but-busy PackageKit held
  `/var/lib/apt/lists/lock` long enough to fail the upgrade.

### known_issues

- PackageKit (GNOME Software, update notifier) takes the apt lists lock for
  seconds at a time on desktop hosts. It was diagnosed as short-lived, not
  wedged, so the fix is to wait rather than stop the daemon. If a run still
  times out, `sudo systemctl stop packagekit` (it is D-Bus activated and comes
  back on its own) or the `unlock-apt` alias.
- `ansible.builtin.apt` with `update_cache` hard-fails after
  `update_cache_retries` (5) when any source errors, including a foreign one.
  That is correct — a partial refresh would upgrade against stale indexes — and
  is why a dead source has to be dealt with rather than tolerated.
