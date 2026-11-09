### Fixed

- A VM test run that dies no longer leaves anything behind silently. Molecule
  installs no signal handlers and runs its own teardown only on the exceptions
  it raises, so a killed, cancelled, or hung run held its VM indefinitely. The
  wrapper now bounds the run with `timeout`, and `/tmp/lima-*` roots are aged
  out by the existing `systemd-tmpfiles` timer at one day. Leftovers are
  reported at start rather than removed.

- Molecule's run state no longer lives inside the chezmoi source. A run killed
  during an install left a dangling symlink in the scenario's `.molecule/`, and
  chezmoi resolves the whole symlink chain while loading source state — so
  `chezmoi apply` and `execute-template` failed afterwards while `managed` and
  `status` stayed green. State now lives under
  `$XDG_STATE_HOME/molecule/<checkout>/<topic>/<scenario>`, scoped per checkout
  so two worktrees cannot share it, with a warning when pre-relocation state is
  still present.
