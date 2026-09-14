# opencode — changelog

Section names come from antsibull-changelog; see `docs/TOPICS.md`
§ "Per-topic changelog and local edge cases".

## 2026-09-14

### bugfixes

- Trust `anomalyco/tap` before tapping it. Homebrew 7 refuses to load a
  third-party tap's formulae until the tap is trusted, so the install had been
  failing on macOS and the binary was never present. See `known_issues` below
  for what the failure actually looks like.
- Teardown now revokes both trust entries. `brew trust --tap` writes a tap
  entry and `brew install` writes a separate formula entry; `brew untrust --tap`
  removes only the first, so `opencode_remove_tap` left the formula entry behind.

### known_issues

- **A tap that is not trusted fails at tap time, and the error names neither
  trust nor the fix.** On Homebrew 7.0.1, `brew tap anomalyco/tap` validates
  every formula in the tap, refuses each one as untrusted, and aborts with:

      Error: Cannot tap anomalyco/tap: invalid syntax in tap!

  Nothing in that message mentions trust. The fix is `brew trust --tap
  anomalyco/tap`, which `tasks/install.yaml` now runs first — trust is keyed by
  name rather than by tap contents, so trusting an untapped tap is valid, and it
  is the only ordering that works.

- **`./update` will not install a missing binary.** `update.sh` runs
  `--tags upgrade`, and the binary tasks are tagged `install`/`provision` only,
  so an upgrade pass syncs skills and leaves an absent opencode absent. This is
  the tier model working as designed — `brew upgrade` refreshes what is
  installed — but it means a machine that has only ever run `./update` never
  gets the topic. Use `./run-role.sh opencode install` or `--tags provision`.

- **The tap tracks releases; homebrew/core trails it.** Measured 2026-09-14:
  tap 1.18.31, core 1.18.30. core's formula sets `livecheck { throttle 5 }`, so
  it follows every fifth release by design. The tap is pinned deliberately for
  that reason — see `tasks/install.yaml`.

- **`opencode auth login` is not automated and will not be.** Tokens live in
  machine-local `auth.json`; a provisioning run does not capture credentials
  interactively. A fresh machine needs it run by hand once.

### minor_changes

- Permission rules now template the home directory. `external_directory` had
  carried literal `/home/bdavis` paths, which never matched on any machine whose
  home was elsewhere — leaving the surrounding `"*": "deny"` as the only rule in
  force, silently. The file is `dot_config/opencode/opencode.jsonc.tmpl` in the
  chezmoi source and renders `{{ .chezmoi.homeDir }}` per machine.
