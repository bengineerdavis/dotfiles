---
id: decision-7
title: Chezmoi owns the ~/code subdirectory tree; gita fails loudly when it drifts
date: 2026-11-18 13:05
status: accepted
---

## Context

Before this decision the skeleton was hardcoded in
`home/dotfiles/apps/gita/defaults/main.yaml` as `gita_layout_skeleton`
(`personal`, `personal/templates`, `personal/try`, `personal/captures`,
`personal/interviews`, `forks`, `work`). Chezmoi managed **zero** paths under
`~/code`, so nothing owned the shape.

That produced a real failure. On 2026-11-17 the template repos moved from
top-level `~/code/templates/` to `~/code/personal/templates/` per
`docs/LAYOUT.md` § Structure. Nothing detected the move:

- `config/repos.yaml` still declared 11 old-shape paths (`templates/` 7,
  `try/` 3, `tutorial/` 1), so gita reported those repos as
  declared-but-not-cloned and registered **none** of the seven repos in
  `personal/templates/`.
- Gita's own `repos.csv` kept seven registrations pointing at the old paths
  (`templates/` 6, `try/` 1). Gita filters missing paths from every operation
  and cannot prune them via `gita rm`, so the stale rows were unreachable *and*
  unfixable through the CLI.
- Lore's database still mapped the projects to the old paths, so it kept
  regenerating `.lore.md`/`AGENTS.md` into a directory that no longer held the
  repos — creating a duplicate-name trap where `~/code/templates/copier-cat`
  resolved to a two-file stub instead of the repository.

Every one of those is a silent-drift failure. A loud check at the point of
mismatch would have surfaced all three immediately.

## Decision

The `~/code` subdirectory tree is **chezmoi-owned**. The directory skeleton —
which type trees exist and how the named subdirs nest under `personal/` — is
declared in chezmoi, deployed by `chezmoi apply`, and is the single source of
truth for the shape.

`apps/gita` **consumes** that tree and **fails loudly** when the structure on
disk does not match. A mismatch is never reconciled silently: it halts and
requires the user to confirm reconciliation manually (typically via an agent
session). Gita registers what exists; it does not decide what should exist.

## Consequences

- `gita_layout_skeleton` in `apps/gita/defaults/main.yaml` moves to chezmoi.
  Gita's install task reads the deployed tree rather than provisioning it.
- The install task gains a **hard check**: compare the observed tree against
  the declared shape, and fail with the specific mismatch and the
  reconciliation command instead of proceeding.
- Provisioning is no longer a side effect of running the gita topic. A fresh
  machine gets its skeleton from `chezmoi apply`.
- `docs/LAYOUT.md` stays descriptive of the standard; chezmoi becomes the
  executable declaration of it.
- DOT-366's acceptance criterion #4 ("a check fails when a declared repo's path
  does not match its catalogue entry") is satisfied by this check rather than
  by a separate catalogue validator.

## Impact graph

Changing who declares the tree reaches further than the two files it edits.
Edges below are marked **verified** (measured this session) or **expected**
(reasoned, not yet exercised).

**Who declares → who consumes.**

- `gita_layout_skeleton` has exactly two references today: its definition
  (`defaults/main.yaml:35`) and the provisioning loop (`install.yaml:91`).
  *Verified by grep; no test pins the skeleton.*
- Chezmoi managed **zero** paths under `~/code` before this. *Verified.*
- Chezmoi deploys empty directories and leaves non-empty ones alone: a probe
  declared `code/personal/captures` empty and it appeared; dropping the
  declaration left a populated directory intact. *Verified by probe.* This is
  what makes chezmoi the right owner — `personal/captures` and
  `personal/interviews` are **empty today**, so only a declaration can keep
  them existing on a fresh machine.
- ⇒ Consequence: gita's install stops creating directories. Under the CRUD
  ownership invariant (`docs/TOPICS.md:471`) a topic must undo only state it
  created, so `remove.yaml` correctly keeps its hands off the skeleton — it
  already does. *Verified.* No teardown change is required, but the invariant
  is now the reason, not an accident.

**The shape feeds the capture, which feeds redge.**

- `tree.yaml` (`~/.local/state/layout/`) is written by `install.yaml:189` and
  deleted by `remove.yaml:30`. No other consumer exists in-repo today.
  *Verified by grep.*
- Its comment claims redge-cli's SPEC R1/R2 will consume it. **Not verified:**
  R1 and R2 describe the catalogue and named groups; neither names `tree.yaml`.
  Treat the link as intent, not contract. *R2 does independently require
  membership to "cite paths under the type directory, never bare basenames (a
  known collision source)" — the same defect class as the duplicate clones in
  this incident.*
- ⇒ Consequence: once chezmoi declares the shape, the capture stops being the
  only record of intent and becomes a **comparison target**. Drift detection
  is then "observed capture vs declared shape" rather than "observed vs a
  hardcoded list". That is the whole point, and it is why the capture must
  survive the ownership move.

**What a shape change silently moves with it.**

- `config/repos.yaml` paths must resolve against the shape. After the unmerged
  catalogue fix, 38/49 do. *Verified.*
- Gita's `repos.csv` is keyed by path. A move leaves rows that gita filters
  from every operation and cannot prune via `gita rm` — seven such rows exist
  right now. *Verified.*
- Worktree `gitdir` pointers break on a move. 21 worktrees across four repos
  needed repair in this incident. *Verified.*
- Lore resolves a project from **cwd, not from its DB row**
  (`hdrProject=absent` → `project=<cwd>`). A shape change therefore redirects
  lore's writes with no error. *Verified.* Two project rows already pointed at
  vacated paths.
- ⇒ Consequence: the loud check must fail on shape drift **before** anything
  moves, because every downstream consumer fails silently and some fail
  destructively (worktrees).

**The check's own blast radius.**

- A strict check fires on the **second machine**, which DOT-366 records as
  still on the old layout (`projects/…`, 43 entries). *Expected — reasoned from
  DOT-366, not measured.*
- A check that compares *contents* rather than *shape* fires on every fresh
  machine, where the tree exists and the repos do not.
- ⇒ Consequence: the check compares declared-vs-observed **shape**, and its
  failure message must distinguish "drift to reconcile" from "machine not yet
  migrated". Both are mismatches; only one is a defect.

**Out of scope, deliberately.** Work-repo membership stays in the machine-local
overlay (`machines.local.yaml`); only the *shape* becomes chezmoi-owned.
Per-machine membership stays rejected (`decision-1`, `8c008d1`,
`test_the_registry_carries_no_repo_membership`). *Verified.*

## Rejected alternatives

- **Keep the skeleton in gita and add a drift warning.** Rejected: gita would
  remain the thing that both declares and mutates the shape, so the declarer and
  the observer stay the same actor. Drift stays possible because the same tool
  that notices it also fixes it silently.
- **Auto-reconcile on drift.** Rejected: moving repositories is destructive to
  worktree gitdir pointers (four repos carried live worktrees in the 2026-11-17
  incident). Reconciliation must be a confirmed, human-gated act.
- **Per-machine membership in `machines.yml`.** Already rejected 2026-11-04
  (decision-1, commit 8c008d1) and forbidden by
  `tests/topics/test_machines_registry_data.py`. Membership stays in one shared
  catalogue; only the *shape* becomes chezmoi-owned.
