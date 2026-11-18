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
