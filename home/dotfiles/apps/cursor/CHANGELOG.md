# cursor — changelog

Section names come from antsibull-changelog; see `docs/TOPICS.md`
§ "Per-topic changelog and local edge cases".

## 2026-09-17

### release_summary

Topic brought to TOPICS.md conformance: this changelog and a real README
added, the dead pre-role `tasks.yaml` removed. The topic's substance is
unchanged — it installs the Cursor IDE from the Homebrew cask and tears it
down the same way.

### trivial

- Remove `tasks.yaml`, a leftover from the pre-role include era that nothing
  referenced.
- Replace the template-boilerplate README with one describing the topic.

### known_issues

- **The cask is `auto_updates`, so brew's recorded version drifts.** Cursor's
  own updater moves the app between brew runs, which is the same standing
  drift the two other self-updating casks already carry (noted in
  `TASKS.md` § Where things stand). Not excluded from the brew upgrade pass.
- **Cursor pulls Anysphere tooling alongside an installed extension — measured
  2026-09-17.** `cursor --install-extension ms-python.python` reported three
  installs: the manifest id itself (`ms-python.python` v2025.6.1), a declared
  dependency (`ms-python.debugpy` v2026.6.0), and **`anysphere.cursorpyright`
  v1.0.12, requested by nobody** — Cursor substitutes its own Anysphere build
  into the Python stack. The manifest id survives, so id-based bookkeeping
  works for the entry; any id-diff drift report must expect Anysphere extras
  or everything reads as drift. (Probe installed, recorded, and uninstalled —
  machine returned to zero extensions, verified.)
- **Cursor CLI facts, verified 2026-09-17 on this machine.** A bogus
  `--install-extension` id exits 1 and names the cause ("Extension ... not
  found. Make sure you use the full extension ID"); `--list-extensions` at
  zero extensions prints nothing and exits 0 — empty is a valid state, not an
  error; both `code` and `cursor` resolve through `/opt/homebrew/bin`
  symlinks into the app bundles, so hand-deleting an app leaves a dangling
  symlink where `command -v` still succeeds; and the CLI dies with the cask,
  so any extension teardown must run before cask removal or it cannot run at
  all.
