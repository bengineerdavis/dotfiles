# loreai — changelog

This topic's own history. It travels with the directory, so a topic lifted into
another repository arrives with its history and its edge cases intact. See
`docs/TOPICS.md` § "Per-topic changelog and local edge cases".

Section names come from **antsibull-changelog** — the Ansible community's
changelog tool. Entries are dated, not versioned.

## 2026-10-21

### release_summary

Topic created: Lore.AI persistent-memory gateway — checksum-verified binary,
per-agent extensions behind detection, first-install prompts saved per
machine.

### minor_changes

- Native install of the `lore` standalone binary from BYK/loreai releases,
  checksum-verified against the release's `lore-checksums.txt`; the topic
  owns upgrades (`get_url` re-fetches only on checksum change), tagged
  `[install, upgrade]`.
- First install prompts (telemetry, worker-model inference) run before any
  mutation and save per machine to `~/.config/loreai/env.zsh`; later runs
  never prompt. Non-interactive runs pass `-e loreai_telemetry` /
  `-e loreai_inference` or fail fast before changing anything.
- Agent extensions for claude-code, codex, pi and hermes via
  `lore setup <app>`, each behind CLI/config detection.
- opencode extension via the chezmoi-included plugin fragment
  (`files/opencode/lore-plugin.jsonc`) rather than `lore setup opencode`;
  see known_issues.
- `lore import` is report-only at install: a dry-run preview plus the
  per-project command; provisioning never spends curator tokens.

### known_issues

- **opencode config is chezmoi-owned on this fleet.** `lore setup
  opencode` writes `opencode.json`, but when both `opencode.json` and
  `.jsonc` exist the `.jsonc` wins (measured 2026-09-12), so setup's
  writes would be shadowed. The integration is the plugin fragment the
  chezmoi template includes; it only reaches the deployed file on the next
  `chezmoi apply` after merge, and `tasks/agents/opencode.yaml` warns
  (never fails) until it does.
- **Persistent setups need the gateway running.** After
  `lore setup claude-code|codex`, the agent's provider points at
  127.0.0.1:3207; if no gateway is up the agent's calls fail. `lore start`
  runs one; launching via `lore run` instead manages the gateway
  per-invocation. The topic deliberately installs no launchd/systemd
  service for the gateway — that is a separate decision.
- **The local worker tier is unexercised.** The `local` inference answer
  exports `LORE_UPSTREAM_OLLAMA` / `LORE_WORKER_UPSTREAM` /
  `LORE_WORKER_MODEL=ollama/<tag>`, but no machine in the fleet has run it
  yet — treat it as rendered, not proven.
