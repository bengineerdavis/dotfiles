# Cutover notice: the task queue is `backlog/` now

**Breaking change, 2026-10-27.** `TASKS.md` and `TASKS-RESOLVED.md` are
deleted. The queue is per-task Markdown files under `backlog/`, managed by
`backlog-py` (CLI) and `backlog-py-mcp` (MCP). The decision record is
`docs/BACKLOG-MIGRATION.md`; this notice is what an agent or human needs to
convert in-flight work. It applies on every machine — pull `main` first.

If your session started before the cutover, read the rewritten `AGENTS.md`
Start-here section before doing anything else.

## For any agent on a machine that is behind

1. `git pull` on `main`. The queue is `backlog/tasks/`.
2. Install the tool: apply `apps/backlog`
   (`ansible-playbook dotfiles/apps/backlog/playbook.yaml`). It installs
   `pipx:backlog-md-py` through mise and the singleton daemon's service
   unit. Until that lands, `uvx --from backlog-md-py backlog-py` works.
3. Smoke the daemon: `backlog-py daemon ensure && backlog-py daemon status
   --json && backlog-py daemon stop` — and on Debian, decide on
   `loginctl enable-linger` yourself; the topic reports, never changes.
4. opencode gets the MCP server from `chezmoi apply --force
   ~/.config/opencode`. Codex: `[mcp_servers.backlog]`
   `command = "backlog-py-mcp"` in `~/.codex/config.toml`. Claude Code:
   `claude mcp add backlog-py backlog-py-mcp`.

## Converting an in-flight branch

The rule from the author: **the cutover wins.** Rebase and convert, in
this order:

```bash
git fetch origin
git rebase origin/main            # or: git merge origin/main
```

Then the conflicts, one rule each:

- **`TASKS.md` (modify/delete): take the deletion.** First check the
  branch's copy for items added after 2026-10-26 — diff it against
  `archive/tasks-md:TASKS.md`; for every item the branch added, create a
  task (`backlog-py task create "<title>" -d "<body verbatim>"`), *then*
  `git rm TASKS.md`. Nothing queued is dropped; it moves.
- **`TASKS-RESOLVED.md`: take the deletion.** It is history; the tag
  `archive/tasks-md` pins it. Do not import it.
- **`tests/tasks_doc/` conflicts: take the deletion.** Replaced by
  `tests/backlog/` (doctor + config + duplicate-id checks). Rebase your
  test changes onto the new suite.
- **Governance docs (`AGENTS.md`, `docs/PROCESS.md`, `spec.md`,
  `docs/WORKTREES.md`): keep main's cutover text**, then replay your
  branch's actual change on top. These files were rewritten; conflicts
  here are almost always mechanical.
- **`backlog/` id collisions** (both sides created `TASK-N`): the tool
  warns and shadows one — `backlog-py doctor` reports it. Renumber the
  branch's file: `backlog-py task renumber TASK-N TASK-M`.
- **`.chezmoidata/opencode.yaml`**: the MCP registration exists on both
  sides already — dedupe to one `backlog-py` entry.

Then verify before pushing: `uv run --frozen pytest tests/backlog -q`
green, `backlog-py doctor` clean, and the branch's own suite green.

## Branch inventory and disposition (as of 2026-10-27)

| Branch | State | Disposition |
|---|---|---|
| `agent_container_setup` | open, live worktree | convert per above; owning session drives |
| `dotagents-topic` | open | superseded by `dotagents-topic-rebased` (merged as PR #76) — close, do not convert |
| local stale branches (`fix-skilltrust-floor`, `handoff_closeout`, `ollama_gpu_fallback`, `precommit-ruff-python-only`) | local only | review and close or convert at owner discretion |
| `backup/*` branches | local only | **do not touch** — they are deliberate history backups; frozen history is the point |

The other machine's branches follow the same rules; nothing there is
exempt because it is out of sight.
