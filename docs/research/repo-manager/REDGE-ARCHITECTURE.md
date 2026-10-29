# `redge` architecture — repositories as a package manager

`redge` (binary) / `redge-cli` (registry namespace) treats git repositories the
way a package manager treats packages: a declarative manifest, an `update` /
`upgrade` / `lock` split, safe one-way sync, named groups, and a pluggable
registry for discovery. This is the design sketch the SPEC hangs off; it is
provisional until the new repository bootstraps and turns it into code.

## The metaphor, bounded

`redge` is *declarative presence* with *safe fast-forward*, **not** a lockfile
that pins and enforces revisions. It may record a `pin` (last-known-good ref) per
repo, but the pin is a **record, never a constraint the tool enforces by
rewriting the tree**. The only permitted working-tree mutation is `git merge
--ff-only` on a clean, attached, non-diverged repo. This is the whole safety
contract; everything else follows from it.

## Components

```
redge
├── manifest        # declared repos + groups + optional pins (config, split committed/local)
├── registry        # pluggable discovery seam; GitHub first (gh/API)
├── sync engine    # update / upgrade / lock / pin / status (the R4/R5/R6 core)
├── state store    # machine-local last-fetch / blocked-since (R6)
├── secrets        # runtime injection, no plaintext (R8)
└── cli            # entry point + machine-readable output contract
```

### manifest

- One committed catalogue of personal repos and remotes; a **local overlay** for
  private/work entries and the per-machine pick. No hostname is committed; no
  work/customer identifier leaves its machine (`spec.md` § Data).
- Schema per repo: normalized remote (`host/owner/repo`), group/type, and an
  optional `pin` (ref). Pins on personal repos may be committed and travel;
  work-repo pins live only in the local overlay.
- Groups are **first-class** (listable, selectable, used by commands), not naming
  conventions.

### registry (pluggable, GitHub first)

- A `Registry` seam with one list verb: enumerate an owner → `(identity, url,
  archived/fork/template)` records. GitHub is the first implementation; a second
  forge is additive (declared in the SPEC, not bolted on later).
- R3 discipline lives here: list endpoints, not Search; detect truncation and
  partial pages; treat auth/rate-limit/secondary-rate-limit failure as UNKNOWN,
  never "empty"; record the account scope; at most ten additions per run.

### sync engine (the core no tool owns)

- **update** — fetch every repo (fetch never touches the working tree) and
  refresh the index/available state.
- **upgrade** — for each repo, `ff-only` toward its locked/upstream ref, **only
  if** clean + attached + non-diverged; advance the pin only when that merge
  succeeds. Diverged / force-pushed / detached / no-upstream → verdict
  `skipped: <reason>` and `blocked-since` set, tree untouched.
- **lock / pin / unlock** — move the recorded ref (explicit, user-initiated).
- **status** — per-repo verdicts (fast-forwarded / skipped-reason / failed) plus
  the staleness read.
- Divergence is defined operatively: ahead-only (ff-able) vs ahead-and-behind
  (diverged, blocked); a failed fetch is UNKNOWN, never "up to date". Submodules
  are out of scope for v1 (superproject only), recorded as a known limitation.

### state store

- Machine-local under `$XDG_STATE_HOME` (e.g. `~/.local/state/redge/`), never
  committed, never synced, never backed up. Records are URL/userinfo-free.
- `last-fetch` advances only on a successful fetch; `blocked-since` resets only
  when a clean `ff-only` clears the reason. "Good run" derives from these records,
  never from exit 0.

### secrets

- Credentials resolve at run time via `op run` / `bw get` / a git credential
  helper / the user's existing `gh auth`; no persisted plaintext token in
  `redge`'s config or state. The preference (R8) is no dedicated service token:
  SSH or `gh auth` should suffice.

### cli

- `redge update|upgrade|lock|pin|sync|status|groups|add …` with a JSON output
  mode and per-repo exit semantics: a repo-local problem exits 0; a provider or
  config defect fails the run. A clean alias (`dist`) is a supported ergonomic;
  the binary name never depends on the PyPI token.

## Boundaries (binding, from the house rules)

- **PRD provision/initialize/state:** provisioning (chezmoi/Ansible) installs and
  triggers `redge`; it never contains `redge`'s logic or state. The Ansible role
  is a sibling artifact inside the `redge` repo (`role/`), graduating to an
  installable dependency later.
- **Two sibling tools:** `topical` owns config/topic orchestration; `redge` owns
  repositories. The namespaces and nouns stay distinct.
- **Deferred:** the high-level task-runner/orchestrator layer (a possible later
  consumer of `redge`'s groups), and the formal threat model.

## Where it lives

New repository, outside the dotfiles tree. This directory migrates wholesale into
it; the `redge-cli` package name is reserved on PyPI and crates.io (see
BOOTSTRAP.md).