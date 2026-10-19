# Prior art — what each reviewed tool teaches `redge`

The adoption search concluded (no tool meets R1–R11 end to end), so this document
changes purpose from "is there a tool" to **"what does each tool teach the
design"?** One row per tool the thread inspected, each with a **take** (borrow),
an **avoid** (the trap), and **why** (the lesson it encodes).

## The two positive inspirations

### mani (Go) and garden (Rust) — the runner/catalogue layer is a commodity

- **Take:** declarative projects + tags, parallel command execution with
  `--ignore-errors`, dry-run, and stream/table/html output. garden adds "grow a
  worktree into existence from a declared remote" — the nicest expression of
  R1 + R7 seen anywhere.
- **Avoid:** adopting them as the sync engine. mani declares sync-is-not-a-
  contract; garden is the same shape in Rust.
- **Why:** the catalogue+runner layer has been re-solved in several languages
  (gita, mani, garden). It is worth *borrowing as UX*, not adopting as a
  dependency. `redge` needs none of their engines.

## The one to copy the group model from, carefully

### gita — groups done right, error handling done wrong

- **Take:** named groups usable in both automation and interactive use; a small
  flat registry; `freeze`/overview.
- **Avoid:** it discards child exit codes and has no ff-only default — its merge
  is `git merge @{u}`.
- **Why:** gita is the proof that *registry + groups* and *safe reporting* are
  independent. `redge` must build the former cleanly and never inherit the
  latter. It is also where the "pure normalizer, property-tested" rule came from
  (gita's basename-keyed registry collides silently).

## The anti-patterns (why R4 exists)

### west (Zephyr) and Google `repo` — manifest convergence

- **Avoid:** a manifest that pins revisions and an `update` that *enforces* them
  by detaching HEAD, rebasing, or resetting the working tree.
- **Why:** "converge the checkout to the manifest" is the exact opposite of
  R4's "never touch local work except `ff-only`". `redge` may carry a pin as a
  *record*, but the only permitted tree mutation is fast-forward.

### ghorg — discovery yes, destructive default no

- **Take:** enumerate an org/user with filters/exclusions and a dry-run.
- **Avoid:** a default update path that `clean`+`reset --hard`s the tree.
- **Why:** discovery and update must be separable; `redge`'s discovery never
  unregisters or mutates, and its update is ff-only.

### gitup — the swallowed failure

- **Avoid:** an internal `_fetch_remotes()` that turns a failed fetch into
  "looks current" and exits 0.
- **Why:** this is the single clearest articulation of R4/R5: a failed fetch is
  UNKNOWN freshness, never "up to date", and a run must report per-repo.

### repoman (klokie, Go) — closest shape, and a cautionary tale in both directions

- **Take:** per-host manifest + local status + clone-missing + parallel
  ff-only-ish pull + per-repo skipped/failed counts. The closest overall shape.
- **Avoid:** it skips dirty repos *before* pull (R4: fetch dirty, never merge),
  keys the registry by basename (R7: remote identity), and relies on one
  contributor with no releases/CI.
- **Why:** it proves the full shape is buildable, and that the two requirements
  it got wrong are exactly the ones that need tests; it also proves the
  go-it-alone maintenance risk the build-cost skeptic keeps flagging.

### myrepos (`mr`) and batchfetch — policy in our config, not in a tool

- **Avoid:** moving the safe-sync policy into a hand-edited `.mrconfig` or a
  merge/rebase/delete task list.
- **Why:** these relocate the requirement into less-testable config; `redge`
  owns the policy in code, where a mutation test can prove it relents.

## The modules, confirmed out of scope

### `ansible.builtin.git` and `community.general.github_repo`

- **Take:** `git` for clone-only, never sync; `github_repo` manages remote-repo
  settings, has **no owner-list discovery** (pinned at 13.4.0 — the sonar got
  this wrong).
- **Why:** the Ansible layer is for installing and triggering `redge`, per the
  PRD rule (provision may install/trigger, never own logic/state). `redge` owns
  discovery and sync itself.

### The Ansible fallback — the composition `redge` replaces

- **Why:** the "thin `ansible.builtin` fetch/ff-only loops + hand-rolled state"
  fallback was the Path-A shape. Once the PRD rule is applied, that shape is
  disallowed for state/logic, so it collapses into "an Ansible role that installs
  `redge` and triggers it". The role is a roadmap item in the `redge` repo.

## The meta-lesson

Every family's evocative single-word name is taken (see the `naming` skill's
watchlist), and every maintained tool stops short of the core. The core —
fetch-everything, ff-only-only, per-repo verdicts, persistent staleness state,
remote-identity adoption — is unowned by everyone, which is why `redge` exists.