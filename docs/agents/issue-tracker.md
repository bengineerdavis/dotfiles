# Issue tracker: backlog-md-py

Work for this repo lives in `backlog/` at the repository root, managed by
`backlog-md-py` (`backlog-py` CLI, `backlog-py-mcp` MCP server). The decision,
the mapping from the old queue, and the verified command surface are in
`docs/BACKLOG-MIGRATION.md`.

## Status: active

The 2026-10-27 cutover is complete. `TASKS.md` and `TASKS-RESOLVED.md` are
deleted; `backlog/` is the queue of record.

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

The CLI has no `view` subcommand. Task reads are the bare positional
`backlog-py task <id>` or `backlog-py task list`; `backlog-py task view <id>`
errors `Unknown task command: 'view'`. The CLI's own `task --help` opens with
"View tasks", which invites exactly that wrong subcommand — treat the "View
tasks" line as a description, not a verb name.

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

### `autoCommit: false` means a write is not a save

`draft create` and `task create` write to disk and do **not** commit; nothing
survives until the `backlog/` commit lands. A draft left uncommitted is
indistinguishable from a draft that was never filed — and a report saying "the
draft is done" while it sits untracked is a silent loss, the same shape this
repo keeps catching elsewhere (measured 2026-11-08: three drafts filed across
two template repos; one repo's backlog went fully uncommitted and the drafts
existed only on disk until a later session ran the commit). Before declaring a
draft or task durable, run `git status --short` on the target repo and confirm
the `backlog/` change is staged *and* committed — not merely written.

## The `--notes` trap

`task --notes` and `task --append-notes` do not apply the flag. They print the
description and drop into an interactive editor:

```
Actions: [E]dit in editor  [Q]uit
```

In a non-interactive run — an agent session, a worker, a subagent — that prompt
gets no answer, the command aborts, and the note is discarded **without an error
and without a non-zero exit**. Measured 2026-11-04 on two task updates; both
looked like they had written and neither had.

What works in an automated run: edit the task file directly, frontmatter
included (`status:`, `updated_date:`), then verify with `backlog-py doctor`.
Hand-editing is normally forbidden here — this is the documented exception, and
it applies only to `--notes`, not to ids, statuses the tool owns, or leases.
