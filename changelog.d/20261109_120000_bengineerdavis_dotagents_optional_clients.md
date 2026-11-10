### Fixed

- **`apps/dotagents` no longer fails when an agent CLI is absent.** The client
  plugin wiring assumed `claude` and `codex` were installed, so a Debian box —
  where `claude` is deliberately absent, since `apps/claude-code` is Darwin-only
  (Debian is DOT-141) — aborted the whole topic. Each CLI is now probed; an
  absent one is skipped and named in the run report, while the skill set still
  reaches every agent through `~/.agents/skills`.

### Changed

- **A failing client now says what it actually said.** The failure messages
  mapped `stderr` alone, and `ansible.builtin.command` reports a missing binary
  as rc 2 with an empty stderr and the reason in `msg`, so the message read
  "nothing on stderr" for the failure that mattered most. A new `client_said`
  filter reports stderr, then stdout (where `claude plugin install` prints
  "Aborted."), then `msg`.

- **`dotagents_wire_claude` and `dotagents_wire_codex`** let a machine decline
  wiring for an installed client. A declined client is reported as declined,
  never as absent, so the two states stay distinguishable.
