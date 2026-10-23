# Decision: migrate the task queue to backlog-md-py

Status: **decided 2026-10-22 with the author** — this document is the record,
per the decision-PR-first sequencing. Migration work lands after this merges.
Supersedes the "Migrate the task queue to backlog-md-py, paired with
worktrunk" § Planned item (promoted to § Now the same day; its original
done-condition is amended by ruling 2 below).

## Rulings

1. **Migrate everything.** § Now (58 items) and every § Planned essay (121
   items) become backlog tasks. Nothing in the queue is dropped; content
   moves, it is not triaged.
2. **Remove the old workflow entirely.** `TASKS.md` and `TASKS-RESOLVED.md`
   are deleted, not kept as generated indexes. One queue, one source of
   truth: `backlog/`. The queue item's original done-condition ("TASKS.md is
   an index over per-task files") is amended accordingly — there is no
   TASKS.md to be an index.
3. **Pair worktrunk now.** Installed in the same change; its adoption into
   the worktree workflow is settled during implementation (§ Open design).
4. **MCP is the machine standard.** `backlog-py-mcp` is registered for every
   agent that reads MCP config, so sessions manage the queue through the MCP
   tools rather than shell conventions.
5. **Decision PR first.** This document, the § Now promotion, and nothing
   else. No migration work until it merges.

## Tool of record

`backlog-md-py` (rmusser01/backlog-md-py; PyPI `backlog-md-py`, GPL-3.0-only
— upstream Backlog.md is MIT; the licence difference is recorded in
docs/REFERENCES.md). Entry points: `backlog-py` (CLI) and `backlog-py-mcp`
(SDK-free stdio MCP server, no extra deps). We make the upstream-documented
cutover decision **not** to alias `backlog` — nothing here provides a
`backlog` command, so `backlog-py` stands. Installed via
`pipx:backlog-md-py` in `dotfiles/apps/mise/files/config.toml`; this change
owns that entry (TOPIC-RECIPES.md § tool-entry-ownership — no ad-hoc
`mise use -g`).

The tool's own model covers what our conventions bolted on: per-task
Markdown files (the capture-commit rule becomes "commit the task file"),
statuses and drafts, DoD/acceptance-criteria fields (our "done when X"
lines), assignees, dependencies, milestones, run history, and — replacing
§ Claimed — an **orchestration lease model** (`orchestration
claim/queue/stale-leases`) with version-checked mutations and idempotency
keys, designed for multi-agent use.

## Target design

`backlog/` at the repo root, initialized with `backlog-py init`. Mapping:

| Old | New |
|---|---|
| § Now items | tasks, status In Progress; branch/worktree/owner metadata moves into the task body |
| § Planned essays | tasks, status To Do; the essay becomes the description |
| Unsorted ideas | `backlog-py draft` (the tool's promotion flow) |
| § Claimed lines | `orchestration claim` leases; stale leases are queryable instead of rotting in a file |
| TASKS-RESOLVED.md (56 entries) | deleted; history stays in git under an `archive/tasks-md` tag created at cutover. `backlog/completed/` is the audit trail going forward |
| Handoff snapshot, "Picking this back up", history-rewrite note, sandbox findings | `backlog-py doc create` records where still true, dropped where stale — reviewed line by line during migration |
| Conventions/claims boilerplate, standing reminders | superseded by the tool + this document's rewrite of PROCESS.md/AGENTS.md |

`tests/tasks_doc/` is deleted (it enforces TASKS.md conventions). Its
replacement is a test that runs `backlog-py doctor` (read-only; reports
unreadable task files and id collisions) plus a board render, so the queue
file can never again pass while being structurally broken.

## MCP wiring

`pipx:backlog-md-py` provides `backlog-py-mcp` on PATH. Registered as a
local stdio server for each agent that reads MCP config:

- **opencode** — `mcp.servers.backlog-py` in `.chezmoidata/opencode.yaml`
  (the mechanism the roborev MCP block established; command
  `["backlog-py-mcp"]`).
- **codex** — `[mcp_servers]` in `~/.codex/config.toml`, reconciled with the
  loreai topic's lore_http block (both live in that file).
- **claude-code** — via `claude mcp add` (writes `~/.claude.json`); a manual
  step recorded in the migration PR, not automated config.

stdio-direct to start. The shared singleton daemon (`backlog-py daemon
ensure`) is the documented multi-agent path and stays **out of scope** —
adopt it when concurrent-MCP contention is actually observed, with its
lifecycle (launchd/systemd user service) decided then.

`backlog-py agents --update-instructions` maintains a Backlog-owned,
marker-delimited workflow block in AGENTS.md; our house sections stay
outside the markers, and the queue-specific rules this migration removes
are not re-added.

## Open design (settled during implementation, with the author)

- **worktrunk's command model vs docs/WORKTREES.md.** The 2026-10-18
  direction pairs them, but the house worktree contract (flat
  `.worktrees/<sid>`, underscores, one writer) predates worktrunk's
  adoption. The migration PR evaluates its commands against that contract
  and records what replaces what; WORKTREES.md is updated in the same PR.

## Rewrite scope

`AGENTS.md` (queue references in § Start here, § Working alongside other
sessions, § Everything is branched), `docs/PROCESS.md` (§ The queue and its
workers, § Decomposing work into items — the *method* survives; the
*mechanics* move to the tool), `docs/WORKTREES.md` (worktrunk), `spec.md`
(§ Work — tool-neutral, checked for stale TASKS.md references),
`docs/REFERENCES.md` (backlog-md-py + version pin, worktrunk, upstream
Backlog.md baseline), `tests/tasks_doc/` (deleted, replaced as above), one
changelog.d entry.

## Procedure

1. This decision PR merges.
2. Migration PR, staged commits: mise entry → `backlog-py init` →
   script-assisted import of all 179 items (titles extracted, bodies moved
   verbatim, statuses mapped; script lives in the PR for review) → docs and
   tests rewrite → MCP registration → deletion of `TASKS.md` and
   `TASKS-RESOLVED.md` with the `archive/tasks-md` tag → changelog.
3. Validation per the tool's own cutover checklist: the import runs against
   a **copy** of the repo first; `backlog-py doctor` and `board` must be
   clean; the full repo suite runs before the deletion commit lands.
