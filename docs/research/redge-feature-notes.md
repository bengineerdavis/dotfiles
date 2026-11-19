# redge — feature notes

Observations that inform `redge`'s base and extended feature set, gathered
while building the gita stopgap and re-settling `docs/LAYOUT.md` (2026-10-18).
This is a notes file, not a spec — it feeds the redge design docs carried on
the `repo-manager` thread. Each line names what was learned and what it says
about redge.

## Base — what must work on day one

- **Group by ownership, not location.** The LAYOUT re-settle made the top
  level `personal` / `work` / `forks` — who owns a repo, not what kind it is.
  Groups must mirror that; a repo's type is a declared property, never derived
  from which folder it happens to sit in.
- **A catalogue is the single source of truth.** `config/repos.yaml` maps path
  → group and the topic registers from it. redge should read a declared
  catalogue, never scan-and-guess; a declared-but-uncloned repo is skipped and
  reported, not silently invented.
- **Sync is fetch-all then fast-forward clean, and it never aborts.** gita has
  no atomic "sync": `gita pull` is whatever git does, and it corrupts the "sync
  most of the time" promise on dirty repos. redge's already-specified
  fetch-all + `git merge --ff-only` on clean repos, with per-repo verdicts and
  a run that exits 0 despite repo trouble, is exactly the shape that is needed.
- **Register at the current path; re-register on move; never relocate.** The
  migration into the type dirs is separate, and it is a move plus a
  re-registration, never something the tool decides to do. Self-healing
  relocation stays off until classification is trusted — a wrong move is worse
  than drift.
- **Per-repo verdicts must distinguish "not up to date" from "unknown".** No
  remote, dirty, detached HEAD, no upstream, or a mid-operation state are each
  their own reported verdict; a failed fetch is never reported as "up to date".
- **Key registrations by path, not basename.** Two repos named `gitignore`
  collide in a basename-keyed index (gita names by basename). The catalogue
  carries relative paths; anything redge indexes must key on path identity.

## Extended — from what the stopgap could not do

- **Fork classification comes from Git metadata, not the owner string.** An
  author can own a fork (`bengineerdavis/promptlint`, upstream
  `AryaanSheth/promptlint`) and "own" a non-fork (`bengineerdavis/bt-import`,
  `fork: false`). Verified via `gh api` 2026-10-18. A repo is `forks` when it is
  a fork upstream, even if the author contributes — so redge discovery should
  classify with GitHub's `isFork`/`parent`, and treat that as base default with
  hand override.
- **Discovery with explicit per-source modes** (`add` / `report` / `off`) is the
  growth path, never a silent clone. Missing `gh`, logged-out access, rate
  limits or truncation are UNKNOWN and add nothing.
- **Employer strings never reach a committed list.** `work/` repos are named
  only in a machine-local overlay. The catalogue must keep that boundary; a
  committed catalogue with work names is a spec.md § Data violation.
- **Schedule/timers belong on top of the sync path**, not in it (the eight-hour
  cadence, linger/report-only warnings). redge's core sync is decoupled from
  *when* it runs.

## Explicitly out of base

- **Moving files** — the physical migration into the type dirs is a human
  decision, not a redge feature. redge registers and re-registers; it does not
  relocate.
- **`work/` on a personal machine** — empty on the author's own box; exercised
  only on the work machine. Don't build a feature only one machine uses.
- **`captures/`** — not a git repo, not registered, not synced. It is a
  private/shareable capture store under `personal/`, out of redge's scope.
- **`resources` as a top level** — parked on purpose. If it ever returns it is
  a *symlink index* over `personal/` and `forks/` (a repo lives in its
  ownership home), which redge would read but not create or populate.

## Adjacent, not redge

Two things this arc surfaced that are provisioning/process, not redge, and are
queued in `TASKS.md` § Planned rather than folded into the feature set:

- A **declarative mise module/role** (call `mise use -g` / `mise unuse
  --global` / `mise upgrade` the way Ansible calls apt/homebrew), so the
  stopgap's shell-outs disappear.
- The **backlog-md-py + worktrunk migration**, which is the prerequisite that
  gates the mise module.
## Breakage observed in the gita stopgap (2026-11-18)

The 2026-11-17/18 reconciliation of the duplicate `~/code/templates/` tree
produced failure evidence that bears on redge's design. Each item states what
broke and what it implies for redge. Source: dotfiles
`backlog/decisions/decision-7 - Chezmoi-owns-the-home-subdirectory-tree-and-gita-fails-loudly-on-drift.md`.

- **A registration whose path vanishes becomes unremovable.** Six entries in
  gita's `repos.csv` pointed at deleted directories. gita filters missing paths
  out of *every* operation, including `gita rm`'s choice list, so the rows could
  not be pruned through the CLI at all — only by hand-editing the CSV. **redge
  must offer an explicit "remove a registration whose path is gone" path, or it
  inherits a permanently polluted store.** This is the single strongest finding
  here: the failure is silent, permanent, and unfixable by the tool that owns it.

- **A path-keyed store silently accumulates ghosts.** gita keys its CSV by
  absolute path. Any move creates a new registration and orphans the old one;
  nothing detects the duplicate. Two clones of one repo register as two
  independent repos with the same name. Observed duplicates on this machine:
  `sentry` (two employer orgs), `symbolicator`, `sillysnakes-python-sdk-…`.
  **redge's R2 requirement — "membership SHALL cite paths under the type
  directory, never bare basenames (a known collision source)" — already names
  half this defect.** The other half is that path identity is not *stable*
  identity across a move. Consider recording the remote as the stable key and
  the path as an attribute, not the primary key.

- **Nothing detects that declared and observed disagree.** The repos moved into
  `personal/templates/`; the catalogue still declared top-level `templates/`;
  gita registered neither. No component reported an error. The drift was found
  by a human noticing a directory looked wrong. **A loud declared-vs-observed
  check is worth more than any single feature here**, because every consumer of
  this state fails silently: the catalogue stops resolving, the CSV keeps dead
  rows, worktree `gitdir` pointers break, and lore keeps writing to the old
  location. redge should fail loudly at the point of mismatch rather than
  auto-reconcile — reconciliation moves repos, and moving repos breaks live
  worktrees (21 needed repair across four repos in this incident).

- **Ownership of the shape belongs outside the repo manager.** The decision
  reached in this incident: chezmoi declares the `~/code` shape; redge (and
  gita before it) consumes it and halts on mismatch. A repo manager that both
  declares and mutates the tree is the tool that notices drift *and* the tool
  that silently fixes it. **redge's role should be to read a declared shape and
  compare, never to own it** — this is consistent with redge's existing
  "moving files is explicitly out of base".

- **Chezmoi is a create-only owner, which redge must account for.** Probing
  showed chezmoi creates declared directories and never removes them: undeclaring
  an empty directory leaves it in place. So a declared shape can *assert* a
  directory but cannot *retract* one. **redge must not assume a declared-but-
  absent directory implies "should not exist"** — it may be retained state.

- **`tree.yaml` was documented as feeding redge's SPEC R1/R2; neither names it.**
  The in-repo comment in `apps/gita/tasks/install.yaml` claims the layout capture
  feeds redge. Checked: R1 covers the declarative catalogue, R2 covers named
  groups; neither mentions the capture file. **Recorded as intent, not
  contract** — if redge is meant to consume a layout capture, that requirement
  needs to be written into the spec rather than assumed by a comment in another
  repo.

### What this suggests for redge ordering

The loud declared-vs-observed check is a prerequisite for the migration/repair
tooling, not a follow-on: without it, "repair" has no signal to act on. It is
also cheap relative to the rest of the feature set — it compares two lists.
