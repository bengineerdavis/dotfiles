# Draft: upstream configurable docs and decision paths

Status: **draft, not scheduled** — written 2026-10-26 so the finding is not
lost. Revisit at the backlog cutover and decide whether to open the PRs.

## Why

This repo keeps architecture decisions as Markdown under `docs/`, and the
Matt Pocock engineering flow expects ADRs in `docs/adr/`. `backlog-md-py`
writes decisions and documents under fixed subdirectories of the backlog
folder:

- `<backlog>/decisions/` for `decision create`
- `<backlog>/docs/` for `doc create`

There is no way to point either at `docs/adr` or `docs/specs`. The only
configurable path is the whole backlog folder, which would also move tasks.

We want to coordinate PRs to **both** projects so the docs and decision
directories are configurable, rather than keep two decision stores or accept a
path the repo's docs do not use.

## Checked before drafting (2026-10-26)

| Source | Version / date | Finding |
|---|---|---|
| Backlog.md `ADVANCED-CONFIG.md` (official) | `main`, fetched 2026-10-26 | Config keys include `backlog_directory`; **no** `docs_directory` or `decisions_directory` key |
| Backlog.md `README.md` (official) | `main`, fetched 2026-10-26 | Custom backlog folder via `backlog.config.yml` (`backlog_directory`); docs and decisions live inside the backlog folder |
| backlog-md-py `README.md` (official) | PyPI 2.1.0, fetched 2026-10-26 | "tasks, documents, decisions, and milestones as plain Markdown files under a `backlog/` directory"; `init --backlog-dir` moves the whole folder |
| backlog-md-py source | 2.1.0 installed | `backlog_py/core/documents.py:46` sets `docs_dir = backlog_dir / "docs"`; `backlog_py/core/decisions.py:53` sets `decisions_dir = backlog_dir / "decisions"`; both pass `assert_trusted_subpath(project.root, ...)` |
| Issue search, both repos | 2026-10-26 | `gh search issues` for docs/decisions directory configurability returned no results in either repository |

**Conclusion: the feature does not exist.** `backlog_directory` is the only
path setting. Backlog.md's docs also state it is chosen at `init`, refuses to
move afterwards, is read only from root `backlog.config.yml`, and cannot be set
through `backlog config`. So it cannot be repurposed for this without moving
tasks too.

## Candidate upstream changes

1. **Backlog.md**: add `docs_directory` and `decisions_directory` config keys,
   project-relative, defaulting to `<backlog_directory>/docs` and
   `<backlog_directory>/decisions`. Read them from the same config file as the
   other keys, with the existing traversal checks applied against the project
   root rather than the backlog folder.
2. **backlog-md-py**: mirror the same keys and keep parity with the upstream
   compatibility inventory. The clone's value is compatibility; a key that
   exists only in one implementation is a divergence to avoid.

If only ADRs matter, a narrower `decision_directory` key is the smaller
change. Prefer the pair if upstream wants one shape for docs and decisions.

## Coordination notes

- Backlog.md is MIT (TypeScript/Bun); backlog-md-py is GPL-3.0-only (Python).
  Two PRs, two review cultures, one behaviour.
- Open the Backlog.md PR first. The Python clone's compatibility contract is
  measured against upstream, so landing there first gives the clone a target.
- `backlog-py-mcp` exposes no decision tools at all. If decisions become
  configurable, adding `decision_create` / `decision_list` to the MCP surface
  is the natural companion change, and it is the reason ADRs currently require
  a CLI call.
- Security: the existing `assert_trusted_subpath` and `assert_path_within_base`
  checks are what keep mutations inside the project. A configurable path must
  keep an equivalent check against the project root; do not relax it to a raw
  string join.
- Tests to mirror: path resolution, traversal rejection (`../`, absolute
  paths, symlinks out of the repo), defaults when the key is absent, and
  round-tripping `decision create` / `doc create` into the configured path.

## Open questions

- Does upstream want one `docs_directory` covering both docs and decisions, or
  two keys?
- Should the keys live in `backlog.config.yml` (root) like
  `backlog_directory`, or in `backlog/config.yml` with the rest?
- Is `docs/adr` a path upstream would accept as a first-class example, or does
  it want ADRs to stay under the backlog folder for coherence?
- Does the browser board or TUI assume the docs/decisions paths are inside the
  backlog folder?

## What to do at cutover

- Decide whether this repo still wants `docs/adr` after living with
  `backlog/decisions/` for a while.
- If yes, open the two upstream PRs and link them from this file.
- If no, delete this draft and keep the tool's convention.
