# 1password — changelog

## 2026-09-23

### major_changes

- The topic now owns the 1Password desktop app on macOS as the `1password`
  Homebrew cask. The install adopts the existing app in `/Applications` in
  place, so no second copy appears in `~/Applications`. `/Applications` is a
  documented exception to the repo's `~/Applications` convention, because
  1Password's browser integration requires it.
- The app is restarted when an update left it running the old binary, using
  `roles/restart-stale`. It is asked to quit and then reopened. It is never
  force-quit.

### minor_changes

- `--tags remove` uninstalls the app only with
  `-e onepassword_remove_app=true`, and never zaps its data.

### known_issues

- brew does not upgrade the app. 1Password's own updater does, because the cask
  is `auto_updates`. If that updater is turned off, nothing updates the app.
- Firefox is installed into `~/Applications` by `apps/firefox`. 1Password
  requires the browser in `/Applications` too, so Firefox cannot connect to the
  app.

## Unreleased

### major_changes

- Added `apps/1password` as an `app`-tier dependency-provider topic for the
  1Password CLI (`op`) on Debian-family work machines. The binary itself is
  managed by the mise topic; this topic verifies it and fails loudly if it is
  missing.

### minor_changes

- Marked topic as supported on Darwin as well as Debian.
