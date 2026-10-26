**Added**

- `docs/agents/` configures the Matt Pocock engineering skills for this repo.
  The issue tracker is `backlog-md-py` (`backlog-py` CLI, `backlog-py-mcp`
  server), with `TASKS.md` named as the interim queue until the cutover. Triage
  uses the five canonical labels. Domain docs are `docs/GLOSSARY.md`; ADRs are
  created with `backlog-py decision create` under `backlog/decisions/`.
- The `backlog-py-mcp` server is registered for opencode under `mcp.servers` in
  `.chezmoidata/opencode.yaml`, ahead of the cutover.
- `docs/BACKLOG-UPSTREAM-CONFIG.md` records that neither Backlog.md nor
  backlog-md-py can point docs or decisions outside the backlog folder, with
  the drafted upstream PRs to change that.

**Known issues**

- The MCP server starts and answers `initialize` with no `backlog/` project
  (verified 2026-10-26), but its task tools have nothing to act on until the
  cutover. Registration is deliberate so the surface exists when the queue
  lands; calls fail until then.
- `backlog-py` exposes no decision tools over MCP. ADRs are a CLI verb until
  the upstream work in `docs/BACKLOG-UPSTREAM-CONFIG.md` lands.
