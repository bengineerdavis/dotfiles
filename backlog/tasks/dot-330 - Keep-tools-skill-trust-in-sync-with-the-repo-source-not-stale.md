---
id: DOT-330
title: Keep `tools/skill-trust` in sync with the repo source, not stale
status: To Do
created_date: 2026-11-09 00:00
labels:
- skill-trust
- drift
- bug
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
`tools/skill-trust` is installed ad-hoc via
`uv tool install <chezmoi source>/tools/skill-trust` and nothing re-syncs it
afterwards. It therefore drifts stale against the repo source: measured
2026-11-08, the installed binary at `~/.local/bin/skill-trust` exposed only
`{check, audit}` while the repo source (ahead of commit `9a6943f`) had added
`resolve` and `trust add/list/remove`. The result was a live failure —
`update.sh`'s ask-first block and the approved-sources guard's own failure
message both call `skill-trust resolve`, which errored
`invalid choice: 'resolve'`. The reinstall
(`uv tool install --force --upgrade`) is a hand-fix that will recur, because
`install` (not `install --upgrade`) leaves an already-installed copy in
place even when the source has moved on.

DOT-81 covers *first* install from a topic; this task covers the *ongoing*
re-sync. Two halves:

1. **Re-sync mechanism**: whatever installs `skill-trust` (DOT-81's topic)
   must re-sync on upgrade — `uv tool upgrade` or `uv tool install
   --force --upgrade`, run on the deploy path so a repull + update can never
   leave a stale verb set behind.
2. **Drift detection**: a guard or check that surfaces a
   tool-surface mismatch (binary verbs trailing the source) rather than
   letting the next `skill-trust resolve` call discover it. This is the
   stale-tool-surface failure class the AGENTS.md rule names: verify the
   binary's `--help` before trusting the source's CLI contract.

Done when a machine whose installed `skill-trust` predates a new verb gets
re-synced by the normal update path (no hand `uv tool install`), and when a
stale binary is surfaced before a caller trips on it.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria

<!-- SECTION:ACCEPTANCE:BEGIN -->
- [ ] The deploy path re-syncs (upgrades) `skill-trust`, not just first-installs it
- [ ] A stale tool surface (binary verbs behind the source) is detected and reported, not discovered mid-run
- [ ] Update.sh / the guard can call `skill-trust resolve` without error after a repull + update
<!-- SECTION:ACCEPTANCE:END -->

## Related

- DOT-81 — install `tools/skill-trust` from a topic instead of by hand (first install)