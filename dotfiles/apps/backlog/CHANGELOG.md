# backlog — changelog

This topic's own history. Section names come from **antsibull-changelog**.

## 2026-10-23

### release_summary

Topic created for the backlog-md-py queue migration
(docs/BACKLOG-MIGRATION.md): the pipx entry via mise's first-party capture
and the singleton daemon's per-user service unit.

### known_issues

- **Debian sessions only.** The systemd user unit fires only while a user
  session exists. Always-on needs `loginctl enable-linger <user>` — run by
  the operator, deliberately not by the topic.
- **Never install upstream Backlog.md alongside.** Its locks are
  incompatible with backlog-md-py's; running both mutation paths against
  the same live project corrupts the queue (upstream-documented).
