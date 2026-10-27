### Breaking changes

- **The task queue is now `backlog/` (backlog-md-py); `TASKS.md` is
  deleted.** This breaks every in-flight branch that touches the old
  files: rebase onto main and convert — `docs/BACKLOG-CUTOVER.md` is the
  procedure (cutover wins; import branch-added items, take the
  deletions). All 177 queued items were imported as per-task Markdown
  files, validated on a repo copy first; the old files' final state is
  pinned at the `archive/tasks-md` tag. Agents manage the queue through
  the `backlog-py` CLI or the `backlog-py-mcp` MCP server (registered
  for opencode). Claims are orchestration leases with expiry and version
  checks instead of lines in § Claimed, and `backlog/` writes commit
  straight to main as coordination overhead — the one carve-out to
  everything-is-branched (author ruling 2026-10-23). The `apps/backlog`
  topic owns the pipx install and the singleton daemon's per-user
  service unit; worktrunk is installed alongside for worktree mechanics.
  Decision record: `docs/BACKLOG-MIGRATION.md`.
