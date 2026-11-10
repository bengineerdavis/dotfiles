# dotagents — changelog

Section names come from antsibull-changelog; see `docs/TOPICS.md`
§ "Per-topic changelog and local edge cases".

## 2026-11-09

### minor_changes

- **Client plugin wiring tolerates an absent CLI.** `claude` and `codex` are
  probed on the extend PATH; an absent one is skipped and named in the run
  report. The wiring assumed both were installed, which aborted the whole topic
  on Debian, where `claude` is absent by design (apps/claude-code is Darwin-only;
  DOT-141 is open). The skill set reaches every agent through `~/.agents/skills`
  regardless, so absence is a supported state — a client that IS installed and
  then fails still fails the run.

- **Failure messages report what the client actually said.** The gates mapped
  `stderr` alone; `ansible.builtin.command` answers a missing binary with rc 2,
  empty stderr, and the reason in `msg`, so they printed "nothing on stderr".
  A `client_said` filter reports stderr, then stdout (where `claude plugin
  install` prints "Aborted."), then `msg`.

- `dotagents_wire_claude` and `dotagents_wire_codex` (default true) let a
  machine decline wiring for an installed client. A declined client reports as
  declined, never as absent.

## 2026-11-01

### minor_changes

- dotagents 3.4.0's first `--user sync` adopted the vendored skill set: the
  12 directories this topic tolerates undeclared (no-ai-slop + the roborev
  family) are now declared in `~/.agents/agents.toml` as `[[skills]]` entries
  with `path:` sources. Adoption, not a new approval — the files were already
  on disk under `dotagents_vendored`'s supervision, and `path:` sources declare
  what is here rather than grant trust (no upstream fetch). The provenance
  guard still audits all 28 store skills, so an undeclared directory would
  still fail the run. Recorded in `defaults/main.yaml`.

## 2026-10-26

### major_changes

- New topic. It owns the machine's global agent-artifact declaration, moved out
  of `apps/opencode`: the approved source list, the source-trust allow-list,
  the per-source excludes, the vendored-skill exceptions, and the sync that
  installs them. `apps/opencode` keeps its binary and config and no longer
  carries a skill manifest.
- The topic calls the pinned `dotagents` binary from mise instead of
  `npx @sentry/dotagents@latest`. The split channel is how plugin support
  (3.4.0) reached the machine while mise still pinned 3.3.0.
- `dotagents_agents` names all six supported runtimes (`claude`, `cursor`,
  `codex`, `vscode`, `opencode`, `copilot`) and is written on a fresh machine
  only. `agents.toml` belongs to dotagents once it exists.

### minor_changes

- `mattpocock/skills` added as an approved source. MIT, verified 2026-10-26
  with `gh api repos/mattpocock/skills`. The repository is a plugin
  marketplace, so it installs as a plugin rather than a wildcard skill source.
- The provenance guard now runs from this topic, last in the install, and
  receives this topic's source and vendored lists.

### known_issues

- **Plugin skills for claude/codex load per-client, registered by this
  topic.** dotagents publishes the local marketplace
  (`~/.agents/plugins/marketplace.json`, name `dotagents-local`) but does not
  register it with any client (measured 2026-10-28 on dotagents 3.4.0; upstream
  getsentry/dotagents#201 is a library API for embedding hosts, not client
  wiring). Install now registers the marketplace and installs every declared
  plugin into claude (`claude plugin marketplace add` + `claude plugin
  install`) and codex (`codex plugin add`), reading the plugin names from the
  marketplace file. Both CLIs are idempotent on re-run.

### exclusions

- **cursor** — no plugin registration surface. The cursor CLI exposes no
  plugin or marketplace subcommand (checked 2026-10-30, cursor 3.27.22), and
  its `~/.cursor/plugins/` cache is populated only by cursor's own client
  (the sentry plugin arrived there, not via any CLI). Skills still reach it
  through `~/.cursor/skills` (dotagents-managed store skills).
- **copilot** — no plugin system and no CLI on this machine. `~/.copilot/`
  has no plugins dir; skills reach it through the `~/.copilot/skills →
  ~/.agents/skills` symlink. The GitHub Copilot CLI (`gh copilot`) is not
  installed.
- **vscode** — dotagents itself refuses to target it: sync warns `Plugin
  "mattpocock-skills" targets "vscode", but "vscode" does not support plugin
  outputs` (measured 2026-10-28, dotagents 3.4.0). There is no skills dir to
  link into either.
- **`dotagents init --force` deletes the skills store.** Measured 2026-10-26 in
  a throwaway HOME: every installed skill directory and every trust entry was
  removed. This is why init runs only when `agents.toml` is absent; changing
  the agent list later is a deliberate destructive act, not part of install.
- **`init` installs a skill from an untrusted source.** A fresh `init` writes
  `~/.agents/skills/dotagents` from `getsentry/dotagents`, which is not in
  `dotagents_sources`. Install removes it immediately so the provenance guard
  does not fail on it. Re-check this on dotagents upgrades.
- **Plugin skills are outside the provenance audit.** The guard reads
  `~/.agents/skills`; a plugin's skills live under `~/.agents/plugins/<name>/`
  and `~/.config/opencode/skills`. Until the guard learns the plugin inventory,
  a plugin source is approved by source trust alone, not by per-skill audit.
