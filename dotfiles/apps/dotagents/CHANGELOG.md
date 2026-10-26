# dotagents — changelog

Section names come from antsibull-changelog; see `docs/TOPICS.md`
§ "Per-topic changelog and local edge cases".

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

- The provenance guard now runs from this topic, last in the install, and
  receives this topic's source and vendored lists.

### known_issues
