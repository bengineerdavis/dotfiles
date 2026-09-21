**Added**

- The `herdr` topic (`dotfiles/apps/herdr`): installs the agent-runtime server
  through mise with the topic owning the entry (`mise use -g herdr` /
  `mise unuse --global herdr`, probe-first, capture committed), wires agent
  integrations from a new shared catalogue (`dotfiles/config/agents.yaml` —
  opencode and claude wired, cursor skip-and-report, all 18 upstream ids
  accounted), owns the server as a launchd gui-domain agent (Darwin) and a
  systemd user unit (Debian) at the stable mise shim path, captures a minimal
  `~/.config/herdr/config.toml`, and generates a topic-owned zsh completion
  into `~/.zfunc/_herdr`. Teardown is gated (`herdr_remove_integrations`,
  default off) and intersection-only, ordered integrations → service → entry.
- A test-first swarm-built suite (`tests/herdr/`, 108 tests): four independent
  fresh-context authors deduced the contract from written artifacts before the
  topic existed, plus an executable contract module the YAML is pinned against.
  A measured judge loop (see `dotfiles/docs/JUDGE-SELECTION.md` and
  `tests/herdr/calibration/`) ran one ITERATE round and a unanimous SHIP panel.
- Two reusable docs from the same work: `dotfiles/docs/TOPIC-RECIPES.md`
  (install-mechanism chooser, catalogue pattern, skip-vs-raise, service
  ownership, the test-first recipe) and `dotfiles/docs/JUDGE-SELECTION.md`
  (the calibrated judge methodology, with the measured pool recommendation).

**Fixed**

- The remove-side status parsing was written against an assumed JSON wire
  shape; measured on the real binary (herdr 0.9.1) the format is
  `<id>: installed|not installed (<path>)` lines — including a
  `(experimental)` annotation variant — and the YAML grammar regexes carried
  a latent double-escaping bug (never would have matched). Both corrected
  against the binary; a golden-transcript test now pins the real wire.

**Changed**

- `apps/mise/files/config.toml` gains the `herdr = "latest"` entry with the
  ownership comment — the capture the topic's first-party commands write
  through the deployed symlink.
- Real machine state is **not** touched: converge, second-run idempotence and
  remove are the author's three passes; the `mise upgrade` output predicate
  and `launchctl enable` idempotence are recorded as what that pass settles.
