**Added**

- `mattpocock/skills` is an approved skill source. MIT, verified 2026-10-26
  with `gh api repos/mattpocock/skills`. It is a plugin-marketplace repository,
  so dotagents installs it as a plugin rather than a wildcard skill source.

**Known issues**

- A plugin source's skills are linked into `~/.config/opencode/skills` only.
  dotagents publishes client marketplaces under `~/.agents/` but does not point
  claude, cursor, codex or copilot at them; per-client wiring is queued as its
  own task.
- Plugin skills sit outside the provenance audit, which reads
  `~/.agents/skills`. A plugin source is approved by source trust alone.
