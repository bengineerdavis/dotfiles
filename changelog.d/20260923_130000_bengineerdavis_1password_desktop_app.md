**Changed**

- The `1password` topic now also manages the 1Password desktop app on macOS,
  as the `1password` Homebrew cask. The existing app in `/Applications` is
  adopted in place, not moved or copied. The app stays in `/Applications`
  rather than `~/Applications` because 1Password's browser integration requires
  it. 1Password's own updater still does the updating. If an update leaves the
  old app running, the next install or upgrade run quits it gracefully and
  reopens it. If the app does not quit, the run reports it and leaves it
  running.
