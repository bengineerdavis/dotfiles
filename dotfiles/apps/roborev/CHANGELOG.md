# roborev — changelog

This topic's own history. It travels with the directory, so a topic lifted into
another repository arrives with its history and its edge cases intact. See
`docs/TOPICS.md` § "Per-topic changelog and local edge cases".

Section names come from **antsibull-changelog** — the Ansible community's
changelog tool. *antsibull* is the project's real name, not a typo for *ansible*.
Using its vocabulary keeps a later move to `changelogs/changelog.yaml` a
conversion rather than a rewrite.

Entries are dated, not versioned. Drop the sections you do not need — an empty
heading is worse than an absent one. Record upstream behaviour you had to work
around under `known_issues`, and keep the *reason* for the workaround in a
comment beside the task that does it.

## 2026-10-13

### minor_changes

- Topic created. Installs the roborev CLI on Darwin (the `roborev` formula
  from upstream's `kenn-io/tap`, trusted before tapping — Homebrew 7 refuses
  an untrusted third-party tap at tap time and the refusal names neither
  cause nor fix) and on Debian (the release `.deb`, checksum-verified
  against the GitHub API's per-asset digest, installed via apt; the topic
  owns its own currency because `apt upgrade` cannot reach a GitHub-release
  deb). `--tags remove` uninstalls the binary and keeps the tap unless
  `roborev_remove_tap` is flipped, mirroring `apps/opencode`.

### known_issues

- **`--check --tags provision` cannot verify a fresh install.** On an
  untapped Mac, check mode fails at the brew install task with "No available
  formula ... This command requires the tap kenn-io/tap": check mode skips
  the actual `brew tap`, so the formula lookup runs against a tap that is
  not there. A real run converges (trust → tap → install). Same class on
  the Debian route: check mode skips the cache-directory creation, so the
  `.deb` fetch reports a missing destination. Verify a fresh machine with a
  real run, not `--check`. Measured on Homebrew with the community.general
  collection, 2026-10-13.
- **The apt step of the Debian route has never run.** It was exercised only
  as far as the checksum-verified fetch (run for real against the temp
  cache dir); the install itself needs a Debian box with become rights.
  Until it runs there, treat the Debian route as rendering-verified only.
