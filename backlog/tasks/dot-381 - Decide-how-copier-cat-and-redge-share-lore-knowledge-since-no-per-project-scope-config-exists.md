---
id: DOT-381
title: Decide the lore sharing shape for personal projects, now that .lore.json
  workspaces exists
status: To Do
created_date: 2026-11-18 21:42
updated_date: 2026-11-18 21:43
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->

> **Corrected 2026-11-18.** The first version of this task claimed lore has "no
> per-project config file at all" and framed sharing as needing hosted sync. That
> was wrong, and the error is instructive: a `find -maxdepth 4`/`-maxdepth 6`
> returned no `.lore.json` on this machine, and *no instance* was misread as *no
> mechanism*. The mechanism is documented upstream and has two fields that
> address this task directly. The premise below is rebuilt from
> `packages/core/src/config.ts` and `packages/website/src/content/docs/docs/configuration.md`
> in the fork at `3b48e546`, not from a filesystem search.

The author asked for copier-cat and redge to share lore knowledge.

**`lore.json` does exist and is the per-project config.** It is `.lore.json`, JSONC,
at each project root. It is loaded by `load(directory)` in
`packages/core/src/config.ts`, which does `join(directory, ".lore.json")` and
parses with the Zod `LoreConfig` schema. Nothing existed on this machine simply
because nobody had created one.

Two fields bear on the ask:

- **`crossProject`** (`boolean`, default `true`) — include cross-project knowledge
  in compaction summaries, and auto-promote knowledge recurring across 3+ projects
  to `cross_project = 1`.
- **`workspaces`** (`array<string>`, default `[]`) — sub-project paths or
  single-level globs, relative to the `.lore.json` directory. **"At startup, Lore
  imports `.lore.md` from each resolved sub-project into the root project's
  knowledge base"**, and a file watcher re-imports on change.

Verified constraints that shape what is achievable (2026-11-18, lore 0.40.0):

- **The gateway runs `lore start --local`**, so `LORE_HOSTED_MODE` is unset and
  `.lore.json` *is* read. In hosted mode the file is skipped as a tampering guard.
- **Config is loaded per-directory into a process-wide global.** `load()` assigns
  a module-level `current`; the next call replaces it. No per-request config.
- **Workspace discovery walks up and stops at the first `.git`**
  (`discoverWorkspaceRoot()`: a `.lore.json` with non-empty `workspaces` →
  VCS markers → workspace markers → language markers). A session started inside a
  repo returns that repo and **never reaches a parent's config**.
- **`crossProject` promotion is gated on `embedding.isAvailable()`**
  (`packages/core/src/curator.ts`). No embeddings table exists in the DB and no
  provider was found in config — suggestive, not conclusive. The runtime's own
  message when unavailable: *"local embedding provider unavailable — recall will
  use FTS-only search."* So on this machine, crossProject likely promotes nothing
  today.
- **`workspaces` has no exclusion mechanism.** `resolveWorkspaces()` skips only
  dot-prefixed directories; a glob matching `work/` would import employer
  knowledge into the same base as personal knowledge.
- **`~/code` is already a lore project** (path `/Users/ben.davis/code`, 23 entries,
  own `.lore.md` and lore-managed `AGENTS.md` section) despite not being a git repo.
- **redge is not cloned and has no lore project row**, so nothing can be imported
  from it until a session runs there.

Therefore the task is narrower than first thought. It is not "can sharing work",
it is **which of two mechanisms to use, at which root, and whether the narrower
copier-cat↔redge goal is achievable at all** — it appears not to be, since both
sessions live inside repos and the walk-up stops at `.git`.

Ship:

- A `.lore.json` at `~/code` scoped to **personal projects only**, with
  `workspaces` globs that cannot reach `work/`. The author has asked for personal
  first; work content must stay out of the shared base by construction, not by
  review.
- A decision record stating the root, the exact globs, and what `work/` would
  have to change for it ever to be included
- Verification that the import actually happens: an entry from one personal
  project's `.lore.md` is recallable from a session launched at `~/code`
  — demonstrated, not assumed
- A determination on the copier-cat↔redge pair specifically: either a mechanism
  is found that reaches across two repo-rooted sessions, or the record states
  plainly that it is not achievable with `.lore.json` and names what would be
  needed instead
- Resolution on `crossProject`: measure whether an embedding provider is
  configured, and either enable one (with its cost) or record that crossProject
  is inert here and should not be relied on

Constraints:

- **Personal only.** No glob may match `work/`. Employer content staying off any
  shared or exportable surface is a standing boundary, not a preference.
- Do not create a `.lore.json` at any repo that already has one, and do not
  hand-edit lore's DB as a first resort.
- Never enable hosted sync (`lore login` + `sync enable`) without explicit
  consent — knowledge leaves the machine.
- The walk-up behaviour means a `~/code` config does not help in-repo sessions.
  Any plan that assumes otherwise is wrong; state the limitation in the record
  rather than discovering it in use.
- Prefer `.lore.md`-based sharing (git-owned, reviewable) over DB pokes.

Decision 2026-11-18: start with personal projects only, sharing through a
`~/code` root rather than attempting to bridge individual repos.

**Superseded 2026-11-19.** No `~/code/.lore.json` will be created, and no
`workspaces` globs are wanted. The author's ruling: each repo imports its own
knowledge with `lore import` **in its own session**. Having one repo's session
run `lore import` on another repo's behalf is not a good idea right now — the
imports would land in a session whose context is about different work, and the
walk-up behaviour means the mechanism only ever helped sessions launched at a
root nobody actually works from.

This removes the whole `workspaces` branch of the task. What remains is the
narrower, answerable question: whether copier-cat and redge can share anything
at all, given both sessions live inside their own repos and the walk stops at
`.git`. The in-tree channel (`docs/research/redge-feature-notes.md`) is the
answer that works today; hosted sync stays off and unconsidered.

Consequence for the backlog: do not configure lore's sharing surface. If a
future need appears, it starts from this decision rather than re-running the
`workspaces` analysis.

<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria

<!-- AC:BEGIN -->

- [ ] #1 No lore sharing config is created: no ~/code/.lore.json and no workspaces globs, matching the 2026-11-19 ruling
- [ ] #2 The decision records that each repo imports its own knowledge with lore import in its own session
- [ ] #3 The copier-cat-to-redge pair is resolved: either a mechanism spanning two repo-rooted sessions is named with evidence, or the record states it is not achievable via .lore.json and says what would be needed instead
- [ ] #4 crossProject is resolved with a measurement: with embeddings verified active (1056 vectors, 1051 live rows), the record states whether promotion is enabled and its threshold
- [ ] #5 The in-tree channel is confirmed as the working answer: docs/research/redge-feature-notes.md exists where redge can consume it
- [ ] #6 The walk-up limitation is recorded plainly: a parent config does not reach sessions started inside a repo
- [ ] #7 The board lists DOT-381 with the full description and every criterion: uvx --from backlog-md-py backlog-py board
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:IMPLEMENTATION_NOTES:BEGIN -->

<!-- SECTION:IMPLEMENTATION_NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done

<!-- DOD:BEGIN -->

<!-- DOD:END -->
