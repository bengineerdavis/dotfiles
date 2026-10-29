# backlog

The fleet's task queue of record: [backlog-md-py](https://github.com/rmusser01/backlog-md-py),
a Python implementation of the Backlog.md local-file workflow. The queue
itself lives in the repo's `backlog/` directory — per-task Markdown files
that commit with the code — and agents manage it through the `backlog-py`
CLI or the `backlog-py-mcp` MCP server. The adoption decision and the
migration mapping live in `docs/BACKLOG-MIGRATION.md`.

This topic owns two things, per the TOPIC-RECIPES.md recipes:

1. **The pipx entry** (`pipx:backlog-md-py`) via mise's first-party
   capture — `mise use -g` on install, `mise unuse --global` on remove,
   probe-first. The entry change those commands write through the deployed
   symlink is the operator's to commit.
2. **The singleton daemon's service unit.** The daemon is what serializes
   queue mutations across concurrent agent sessions (CLI and MCP writes
   share its filesystem locks); direct per-client MCP is documented by
   upstream only as the rollback path. Per-user launchd agent on macOS,
   systemd **user** unit on Debian — the unit only fires while a session
   exists, so the topic reports `loginctl enable-linger` rather than
   changing login behaviour.

The daemon binds `127.0.0.1:18765` and logs to `~/.local/state/backlog-py/`.
Its runtime state (locks, the disposable SQLite read index) is throwaway by
design; the Markdown files are the source of truth.

`--tags remove` stops and removes the unit and the mise entry, and names
what is preserved.
