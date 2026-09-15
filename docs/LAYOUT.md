# LAYOUT.md

The cross-machine directory standard: which top-level trees exist, what
lives in each, who owns them, and how the fleet migrates to them. Settled
with the author on 2026-09-15; the interview answers are the record.

## Policy

**Scope.** `~/code` and the capture/state trees. Nothing else is covered
yet; the standard is designed to adjust over time rather than to be right
once. `~/docs` and `~/tools` are deliberately out — their fates belong to
the root-docs-topology and skill-trust topic tasks in `TASKS.md`.

**Sameness.** The same folder on two machines has the same structure. The
layout is designed once and both machines migrate to it; neither machine's
current tree is canonical. Queue prose and docs cite the standard by name
instead of pasting absolute paths — the 2026-09-15 merge broke three
claims on exactly that.

**The taxonomy.** Seven types, flat under `~/code/<type>/<repo>`:

| Type | Holds | Observed members |
|---|---|---|
| `work` | Employer-owned clones | configs, mytools, sentry |
| `personal` | The author's own projects | ai-prompt-library, impromptu, bengineerdavis.github.io |
| `try` | Disposable experiments; nothing here is durable | copier-stamps, git-ai-plugin, openrouter-tools |
| `captures` | Research capture stores, incl. the private/shareable split | llocallabs-capture |
| `templates` | Starting points cloned to copy from | Best-README-Template |
| `forks` | Upstream clones | — |
| `archive` | Cold storage, kept but not active | — |

Promotion between types is a move plus a gita re-registration, never a
copy — repos are managed by git, not duplicated.

**Membership.** `machines.yml` — committed, plain data, hostname → groups →
repo sets — declares which repos a machine gets, and gita consumes it.
Personal repo names are committed; work repos appear by group only and are
named in a machine-local overlay, because employer-identifying strings
must not be committed (`spec.md` § Data). `TASKS.md` already names
`~/code/work/sentry/` in committed text — that is a violation to fix, not
a precedent to extend.

**New repos.** The type is declared at clone time. No default pile, no
post-hoc sorting pass.

**Ownership and enforcement.** An Ansible topic owns the type directories —
system state, per the layering rule in `AGENTS.md` — and gita owns the
repo clones inside them. A `roles/guards` check reports drift (a repo
outside its declared type, an ad-hoc directory) at provision time and
fixes nothing itself, matching the guards' never-auto-repair rule.
Self-healing relocation is the designed evolution and the author wants
recommendations toward it; it ships only when classification is trusted,
because a wrong class that moves files is worse than drift.

**Exceptions.** A directory wanted on one machine only, with its state
still backed up to config, is a declared exception — design deferred,
tracked in `TASKS.md`.

## The plan

Ordered; each phase has its own done-condition. Rollback throughout is
the same: moves are renames with a gita re-registration, nothing is
deleted, so any phase reverses by moving back.

1. **Inventory the second machine.** Queued task. Every divergent tree —
   `~/code/projects/personal/` (at least `llocallabs-capture`),
   `~/code/try/`'s experiments, anything else outside this Mac's layout —
   recorded with its destination type. Done when this plan's migration
   table is complete.
2. **Write `machines.yml` and the overlay schema.** Committed map for
   personal sets; machine-local overlay for work names. Done when the
   parent playbook can slurp the map exactly like a `topic.yml` today,
   per the settled bundle design.
3. **The topic creates the type directories.** Owned by the gita topic
   once its study task settles; empty types are cheap, so all seven are
   created. Done when a fresh machine gets the full skeleton from one run.
4. **Migrate this Mac.** `Best-README-Template` → `templates/`;
   `llocallabs-capture` → `captures/` (out of `personal/`, which is what
   put private notes beside shareable ones). gita re-registers each.
   Done when `~/code` matches the taxonomy and every repo still fetches.
5. **Migrate the second machine.** `projects/personal/*` flattens into the
   right types; `try/` is already conformant; `~/.git-ai` is out of scope
   (the git topic task owns it). Done when the two machines' `~/code`
   trees are structurally identical for shared types.
6. **Switch the citations.** Queue and docs stop carrying absolute paths
   and cite the standard; the drift guard is added under `roles/guards/`.
   Done when `tests/tasks_doc` and the guard both pass and a planted
   drifted repo is reported, not moved.

## What this is not

Not a backup policy (state backup is the deferred exceptions item and the
backup-design task), not a repo-hosting decision (remotes are untouched),
and not permanent — adjust the taxonomy by editing this file, not by
letting a machine drift.
