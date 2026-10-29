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