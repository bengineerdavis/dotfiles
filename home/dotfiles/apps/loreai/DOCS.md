# lore — the project, and how to find its answers

What lore *is*, where its documentation lives, and how to refresh this file when
upstream moves. This is the topic's map of a fast-moving third-party project, not
a copy of it: **every line here points at a source rather than restating one.**

Two kinds of statement appear below. **Verified** statements were checked against
the named file on the date given. **Pointers** name where the answer lives and
make no claim about the current content.

Last verified: **2026-11-18**, at fork commit `3b48e546`.

______________________________________________________________________

## Where everything lives

| Thing                                | Location                                                             |
| ------------------------------------ | -------------------------------------------------------------------- |
| Local source of truth (this machine) | `~/code/forks/loreai` — fork of `BYK/loreai`                         |
| This machine's fork                  | `github.com/bengineerdavis/loreai`                                   |
| Local database                       | `~/.local/share/lore/lore.db` (+ `-shm`/`-wal`)                      |
| Curated export                       | `.lore.md` at each repo root                                         |
| Per-project config                   | `.lore.json` at each project root                                    |
| Gateway                              | `lore run` / `lore start`, port **3207** (fallback probe 3207, 5673) |
| Machine env (worker model, keys)     | `~/.config/loreai/env.zsh`                                           |
| Topic                                | `apps/loreai` in dotfiles                                            |
| Reference skill                      | `lore-plugins-reference`                                             |
| Manage skill                         | `lore-plugins`                                                       |

**The fork is the reference, not the GitHub website.** Read source locally at
`~/code/forks/loreai`; the docs site and the `gh api` paths are the same files.

______________________________________________________________________

## Documentation index

Docs are **Markdown in-repo**, at `packages/website/src/content/docs/docs/` —
not a separate wiki. Every page below is a file you can read directly.

### Core pages

| Page                    | File               | Answers                                                                         |
| ----------------------- | ------------------ | ------------------------------------------------------------------------------- |
| Lore Documentation      | `index.md`         | Orientation; start here                                                         |
| Architecture            | `architecture.md`  | How distillation, curation, and memory fit together                             |
| Configuration reference | `configuration.md` | **Every `.lore.json` field.** Auto-generated from `packages/core/src/config.ts` |
| Environment variables   | `environment.md`   | The `LORE_*` family; auto-generated from source                                 |
| Install Lore            | `install.md`       | Installation                                                                    |
| Setup command           | `setup.md`         | `lore setup` for GUI/IDE agents                                                 |
| Import conversations    | `import.md`        | `lore import` semantics                                                         |
| Code review             | `review.md`        | Review integration                                                              |
| Team memory & review    | `team-memory.md`   | `.lore.md` as a git artifact; Folk Lore                                         |

### Guides (`docs/guides/`)

| Guide                            | File                          | Answers                                 |
| -------------------------------- | ----------------------------- | --------------------------------------- |
| Tune knowledge injection         | `tune-knowledge-injection.md` | Budget, LTM injection, recall tuning    |
| Local inference                  | `local-inference.md`          | Pointing lore at a local model server   |
| Custom upstreams and hosted mode | `custom-upstreams.md`         | Proxies; the hosted-mode trust boundary |
| Semantic linter (CI)             | `semantic-linter.md`          | `lore lint`                             |
| Claude Code with Lore            | `with-claude-code.md`         | Per-agent wiring                        |
| Codex with Lore                  | `with-codex.md`               | Per-agent wiring                        |
| OpenCode with Lore               | `with-opencode.md`            | Per-agent wiring                        |
| Pi with Lore                     | `with-pi.md`                  | Per-agent wiring                        |

### Source over docs, when they disagree

Three places where reading the code beats reading the docs:

- **`.lore.json` schema** — `packages/core/src/config.ts`. The published table is
  generated from this file; when they diverge the source wins.
- **Config load path** — `packages/core/src/config.ts`, `load(directory)`.
  Reads `join(directory, ".lore.json")`.
- **Workspace resolution** — `packages/core/src/workspace.ts`,
  `discoverWorkspaceRoot()` and `resolveWorkspaces()`.

______________________________________________________________________

## Load-bearing facts about this machine

These decide behaviour and are not obvious from the docs.

**The gateway runs `--local`.** `lore start --local` means `LORE_HOSTED_MODE` is
unset, so `.lore.json` **is read**. In hosted mode the file is skipped entirely
— a tampering guard, because a client-controlled file could alter budget, model,
and thresholds.

**`.lore.json` is per-project-directory, loaded into a process-wide global.**
`load()` reads one directory's file and assigns a module-level `current`;
the next call replaces it. There is no per-request config.

**Workspace discovery walks *up* and stops at the first `.git`.** `discoverWorkspaceRoot()`
checks, in order: a `.lore.json` with non-empty `workspaces` → VCS markers
(`.git`, `.hg`, `.jj`, …) → workspace markers (`pnpm-workspace.yaml`, `go.work`,
…) → language markers (`pyproject.toml`, `package.json`, …).

> **Consequence:** a session started inside a repo returns that repo as the root
> and **never reaches a parent's config**. A `workspaces` declaration at `~/code`
> therefore affects sessions launched at or above `~/code`, not sessions launched
> in an individual repo beneath it.

**`workspaces` and `crossProject` are not alternatives.**

|            | `workspaces`                                                                                                         | `crossProject`                                                                      |
| ---------- | -------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| What       | Sub-project paths/globs, relative to `.lore.json`                                                                    | Boolean, default `true`                                                             |
| Effect     | **Imports** each child's `.lore.md` into the root's knowledge base, attributed to the root; also watches for changes | **Promotes** entries whose meaning recurs across 3+ projects to `cross_project = 1` |
| Cost       | Cheap — file reads                                                                                                   | Expensive — embedding similarity + clustering                                       |
| Exclusions | **None** — only dot-prefixed dirs are skipped                                                                        | n/a (semantic threshold)                                                            |
| Gate       | `loreFile.enabled` and non-empty `workspaces`                                                                        | `cfg.crossProject` **and `embedding.isAvailable()`**                                |

**`crossProject` promotion is inert without an embedding provider.** In
`packages/core/src/curator.ts` the promotion call is gated on
`embedding.isAvailable()`. The runtime's own message when unavailable:
*"local embedding provider unavailable — recall will use FTS-only search. To use
a remote provider, set `search.embeddings.provider` in `.lore.json`."*
**Unverified on this machine:** whether an embedding provider is currently
configured. The DB has no embeddings table and no provider was found in config,
which is *suggestive, not conclusive* — confirm with `lore doctor` or by setting
`search.embeddings.provider` and observing.

**`~/code` is already a lore project** (path `/Users/ben.davis/code`, with its own
`.lore.md` and lore-managed `AGENTS.md` section), even though it is not a git
repo. It exists because sessions were launched there.

**`lore` subcommands have no `--help`** — passing it executes the command. Use
`lore help`.

**`lore data export` is lossy** and silently writes a subset. Verified twice
2026-11-18: it wrote 163 of 201 distinct titles for one project. Back up before
exporting, or prefer `lore data recover` (files → DB).

______________________________________________________________________

## Refreshing this file

The documentation index is mechanical, so regenerate it rather than hand-editing.
Run from the fork; it prints a table you can paste over the index section.

```sh
cd ~/code/forks/loreai && scripts/lore-docs-index.sh
```

The script lives at `scripts/lore-docs-index.sh` in dotfiles' `apps/loreai`
(not in the fork — the fork should stay close to upstream). It:

1. lists `packages/website/src/content/docs/docs/**/*.md`,
1. pulls each page's `title:` frontmatter,
1. reports the fork's `HEAD` commit and date,
1. flags any doc page whose title changed since the last run.

### When to refresh

- **After `git pull` in the fork** — docs move with releases.
- **When `lore --version` changes** — the fork and the installed binary track
  separately; a version bump is the signal that behaviour may have moved.
- **Before any decision that depends on a `.lore.json` field**, because
  `configuration.md` is generated from `config.ts` and fields do get renamed and
  deprecated (`budget.targetBustCost` and `budget.maxContextTokens` are both
  `@deprecated` markers already).

### Verifying a behavioural claim

Docs describe intent; the running system is the tiebreaker. In order of
authority:

1. **The installed binary** — `lore --version`, `lore help`, `lore doctor`.
1. **The local source** — `packages/*/src/`, which is what the binary was built
   from at the fork's commit.
1. **The published docs** — `packages/website/src/content/docs/`.
1. **This file** — a pointer set, last verified on the date above.

When 1 and 2 disagree, the binary wins and the fork is behind: `git pull` before
concluding anything.

### Known divergence to watch

`lore-plugins-reference` records that `@loreai/opencode` **0.40.0 targets the
OpenCode V1 plugin API and does not run in OpenCode V2**. That is a version-pinned
fact; re-check it against `packages/opencode/src/index.ts` after any upgrade
rather than trusting this line.
