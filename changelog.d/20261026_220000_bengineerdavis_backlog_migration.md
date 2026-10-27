### Changed

- **The task queue is now `backlog/` (backlog-md-py), and `TASKS.md` is
  gone.** All 177 queued items (58 Now + 119 Planned) were imported as
  per-task Markdown files, validated on a repo copy first; the old files'
  final state is pinned at the `archive/tasks-md` tag. Agents manage the
  queue through the `backlog-py` CLI or the `backlog-py-mcp` MCP server
  (registered for opencode). Claims are orchestration leases with
  expiry and version checks instead of lines in § Claimed, and `backlog/`
  writes commit straight to main as coordination overhead — the one
  carve-out to everything-is-branched (author ruling 2026-10-23). The
  `apps/backlog` topic owns the pipx install and the singleton daemon's
  per-user service unit; worktrunk is installed alongside for worktree
  mechanics. See `docs/BACKLOG-MIGRATION.md` for the decision record.
