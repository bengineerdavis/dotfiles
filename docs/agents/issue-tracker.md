# Issue tracker: backlog-md-py

Work for this repo lives in `backlog/` at the repository root, managed by
`backlog-md-py` (`backlog-py` CLI, `backlog-py-mcp` MCP server). The decision,
the mapping from the old queue, and the verified command surface are in
`docs/BACKLOG-MIGRATION.md`.

## Status: interim

The cutover has not landed. Until it does, the queue is `TASKS.md` and this file
is a forward pointer. Skills that publish or fetch a task use `TASKS.md` under
its own § Conventions until the cutover commit deletes it.

## Agent surface

Prefer the `backlog-py-mcp` tools. The CLI is the fallback for verbs the server
does not expose, not the default. The server is local stdio and resolves the
project from the session directory.

| Need | MCP tool | CLI fallback |
|---|---|---|
| list, search | `task_list`, `task_search` | `backlog-py task list` |
| read one | `task_view` | `backlog-py task <id>` |
| create | `task_create` | `backlog-py task create "<title>"` |
| edit | `task_edit` | `backlog-py task edit <id>` |
| claim, release | `orchestration_claim_task`, `orchestration_release_task` | `backlog-py orchestration claim`, `release` |
| close | `task_complete` | `backlog-py task complete <id>` |
| board, status | `task_board`, `project_status` | `backlog-py board`, `overview` |
| documents | `document_create`, `document_view` | `backlog-py doc create`, `view` |

The MCP path carries the project lock, ids and typed fields. Piping CLI text
loses them, so it is a fallback.

## Spec-driven flow

- **Spec** — a document, not a task: `document_create` with a path such as
  `specs/<slug>`, a `title`, the body as `content`, and
  `metadata: {type: spec}`. It outlives the tickets cut from it.
- **Tickets** — one `task_create` per tracer bullet. Put the done condition in
  `definitionOfDone`, what the checks assert in `acceptanceCriteria`, and
  blocking edges in `dependencies`. Never encode blockers in prose.
- **Implementation** — `orchestration_claim_task` before work,
  `orchestration_record_run` for progress, `task_complete` at the end.
- **Decisions** — `backlog-py decision create` writes `backlog/decisions/`;
  see `domain.md`. The MCP has no decision tools, so this one verb stays on
  the CLI.
- **Triage** — labels on tasks; see `triage-labels.md`.

## Wayfinding

There is no map file convention. `/wayfinder` maps onto one task plus child
tasks created with `orchestration_split_task`; declare blockers with
`dependencies`. Do not create `.scratch/` here.

## Rules

- Never hand-edit `backlog/` files. Ids, statuses and the orchestration lease
  assume the tool wrote them.
- One task per file; never a combined tickets file.
- One task is one outcome with one done condition. Split it with
  `orchestration_split_task` when it is not.
- `autoCommit` is false: commit task files yourself under the house commit
  discipline.
