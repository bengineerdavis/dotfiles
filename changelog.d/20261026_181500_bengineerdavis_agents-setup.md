**Added**

- `docs/agents/` configures the Matt Pocock engineering skills for this repo.
  The issue tracker is `backlog-md-py` (`backlog-py` CLI, `backlog-py-mcp`
  server), with `TASKS.md` named as the interim queue until the cutover. Triage
  uses the five canonical labels. Domain docs are `docs/GLOSSARY.md` and
  `docs/adr/`.
- The `backlog-py-mcp` server is registered for opencode under `mcp.servers` in
  `.chezmoidata/opencode.yaml`, ahead of the cutover.

**Known issues**

- The MCP server starts and answers `initialize` with no `backlog/` project
  (verified 2026-10-26), but its task tools have nothing to act on until the
  cutover. Registration is deliberate so the surface exists when the queue
  lands; calls fail until then.
- `backlog-py` exposes no decision tools over MCP. Architecture decisions stay
  in `docs/adr/`; the tool's `backlog/decisions/` store is deliberately unused,
  so there is one decision record.
