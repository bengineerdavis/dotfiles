# herdr topic

Installs and manages [herdr](https://herdr.dev/) — the runtime that hosts
coding-agent CLIs (claude, opencode, cursor-agent, …) in persistent panes,
tracks their working/blocked/idle state, and restores their sessions across
restarts and machines. One binary, Apache-2.0, macOS/Linux/Windows; current
docs version 0.9.1 (checked 2026-09-19).

The design decisions below were settled with the author 2026-09-18/19 and
generalized into `dotfiles/docs/TOPIC-RECIPES.md` — each decision here links
to the recipe row it instantiates. Read `dotfiles/docs/TOPICS.md` for the
binding topic rules this topic follows.

## Decisions

**Both OSes.** `topic_os: [Darwin, Debian]`, `topic_tier: app`. Per-OS
branching is guarded in-task (CONTRIBUTING.md rule 2 pattern); nothing here
declares `homebrew` in `topic_requires`, so Debian stays schedulable.

**The binary installs through mise; this topic owns the entry.** Not brew, not
a release fetch — see the install-mechanism chooser in TOPIC-RECIPES.md
(cross-OS GitHub-release CLI, per-user is fine, `mise upgrade` owns upgrades).
Concretely:

- install: entry-probe first, then `mise use -g herdr` (registry resolves; the
  `github:herdrdev/herdr` fallback exists if the registry entry predates mise).
- remove: `mise unuse --global herdr`, which prunes the install too.
- **`mise use`/`mise unuse` write through the deployed symlink into the
  tracked `apps/mise/files/config.toml` — the run leaves the repo dirty by
  design; the entry change is committed as the capture** (mise hazard in
  TASKS.md § Cross-session hazards).
- **Never call `herdr update`**: it is valid for direct installs only; mise
  installs are upgraded by `mise upgrade`. A comment in the upgrade task says
  so.

**Agent integrations live in a shared catalogue.** `dotfiles/config/agents.yaml`
(editors.yaml pattern, shared-catalogue recipe in TOPIC-RECIPES.md) maps herdr
integration ids to the agent topics:

- wired: `opencode` (lifecycle authority; needs herdr integration v5+ for
  native restore), `claude` (session-identity hook), `cursor` (session
  identity; `cursor-agent` probe — not installed on this Mac as of
  2026-09-19, so it skips-and-reports).
- candidates listed but not wired: `codex` (mise-owned npm binary, no topic),
  and the rest of herdr's integration list, marked why-not.

The integration loop follows the skip-vs-raise recipe: it runs only after
install, installs per entry whose probe binary and config dir both exist,
**skips-and-reports** when the agent is absent (herdr itself refuses when a
config dir is missing), and **raises** when a required dependency fails.
Remove uninstalls only the installed intersection, gated by
`herdr_remove_integrations` (default off, same gate pattern as
`vscode_remove_extensions`).

**The topic owns the server's service unit.** `herdr server` is the explicit
headless server "for supervised or service-style setups" (CLI reference):

- Darwin: per-user launchd agent `com.herdr.server` in the `gui` domain,
  `ProgramArguments = [<stable bin path>, server]`, RunAtLoad + KeepAlive,
  health-checked after boot.
- Debian: systemd **user** unit `herdr-server.service` (launchd-agent
  equivalent; needs a session or `loginctl enable-linger`).
- The bin path resolves to the mise shim (`~/.local/share/mise/shims/herdr`),
  stable across upgrades — never a version-pinned install path.

**Config is captured, minimally.** `~/.config/herdr/config.toml` deploys as a
chezmoi template with only the settings we have an opinion on today:
`update.channel = "stable"` and `[session] resume_agents_on_restore = true`.
Everything else stays default; `herdr --default-config` prints the full
commented set (208 keys) when an opinion forms. Machine-specific values
resolve via `{{ .chezmoi.* }}` per the AGENTS.md resolved-never-written rule.

**Zsh completion is topic-owned, not chezmoi-owned.** `herdr completion zsh`
is generated at install time to `~/.zfunc/_herdr` (herdr's documented fpath
recipe) and removed under `--tags remove`. Deliberately not vendored into the
zsh tree: that is how the `_ollama_zsh_completion` dual-ownership trap was
created (TASKS-RESOLVED § [5]).

## Structure

    apps/herdr/
    ├── topic.yml            # topic_name/provides/requires/os/tier
    ├── README.md            # this file — the design record
    ├── CHANGELOG.md
    ├── playbook.yaml        # standalone runner
    ├── defaults/main.yaml   # gate vars, catalogue path, service names
    ├── tasks/main.yaml      # tag router [bootstrap|prerequisites|upgrade|install|remove(,never)]
    ├── tasks/bootstrap.yaml     # app-tier stub (router keeps all five files wired)
    ├── tasks/prerequisites.yaml # app-tier stub (mise arrives via topic_requires)
    ├── tasks/install.yaml   # mise entry, integrations, service, completion
    ├── tasks/upgrade.yaml   # mise upgrade; never herdr update
    ├── tasks/remove.yaml    # gated, ordered: integrations → service → entry
    └── templates/           # com.herdr.server.plist.j2, herdr-server.service.j2

`topic_provides: [herdr]`; `topic_requires: [mise]` — mise is the mechanism
and a runtime-manager-tier topic, so tier ordering brings it up first.

## Verification status (honest)

The swarm-built suite lives in `tests/herdr/` (test-first: it was authored
against this README before the topic existed, then the topic was implemented
to green, with mutations recorded per spec.md § Verification). Renders are
checked under both `os_family` values with `StrictUndefined`. What has **not**
been exercised: a real converge on either machine — agents never run
`chezmoi apply`/`run-role.sh`. The author's three passes: converge, second-run
idempotence, remove.

## Upstream references

| Source | URL | Last checked |
|---|---|---|
| Install | https://herdr.dev/docs/install/ | 2026-09-19 |
| Integrations | https://herdr.dev/docs/integrations/ | 2026-09-19 |
| CLI reference | https://herdr.dev/docs/cli-reference/ | 2026-09-19 |
| Config reference | https://herdr.dev/docs/config-reference/ | 2026-09-19 |

These feed the upstream-reference cadence design (TASKS.md § Now): refresh the
checked dates and the integration versions in `agents.yaml` when herdr moves.
