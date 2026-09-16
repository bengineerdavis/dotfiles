# TASKS-RESOLVED.md

A stopgap archive for resolved tasks, ahead of the process refactor queued in
`TASKS.md` § Planned. The convention says a finished task is deleted — "the
commit is the record" — but the queue now spans two machines, and a task
deleted into flattened git history is hard to audit later. Until the
replacement process exists, resolved work moves here instead: one entry per
task, with the outcome, the evidence, and where the durable record lives.
Newest last. Do not grow this file past the refactor — it exists to be
deleted.

## 2026-09-14

- **Approved-source allowlist replaced `apps/opencode`'s per-skill manifest,
  with a guard.** Resolved by the other machine's session (landed via merge
  a586c5b — the opencode defaults change in e60982c, the skill-trust/guard
  work in 10ccccd and 33f6ad7; machine attribution is not verifiable from
  git, identical author identity on both sides; verified against the tree
  2026-09-14). `dotfiles/apps/opencode/defaults/main.yaml`
  now holds approved *sources* — owner/repo shorthand, a `why`, per-source
  `exclude` vetoes — wired to `dotagents trust add` and
  `dotagents add <source> --all`; the guard
  `dotfiles/roles/guards/tasks/dotagents-approved-sources.yaml` also compares
  on-disk skill directories against the declared set, so a hand-placed skill
  is reported rather than ignored. All three done-conditions met: the topic
  names only sources, an unapproved source fails the run, an undeclared
  on-disk skill directory is reported.
- **Source denylist and licence-as-implicit-trust shipped as
  `tools/skill-trust`.** Same session; verified 2026-09-14.
  `tools/skill-trust/skill_trust/decide.py` implements the full precedence
  (denied source > excluded skill > approved source > approved licence >
  deny), the three licence tiers (permissive auto-trusts, copyleft opt-in,
  source-available denied — BSL-1.1, FSL, SSPL, Elastic-2.0), and
  absent-is-not-permissive (no LICENSE or `NOASSERTION` → deny). Follow-on
  still open in § Now: a topic should install skill-trust rather than the
  current hand install.

## 2026-09-15

- **Fix `cosine()` in `apps/ollama/files/executable_ollama-evals` — it could
  return above 1.0.** Resolved 2026-09-14 as 6c3079b, before the
  move-to-RESOLVED convention existed (the other entries here predate it by
  hours, which is why this one was missing); backfilled 2026-09-15 with the
  author's ratification. Cosine now returns 0.0 when either norm's square is
  subnormal — the honest answer, not a clamp — and hypothesis's shrunk
  counterexample (`[1.0]`, `[1.2794807103967847e-160]` → 1.000070683603874)
  is pinned as its own test in `tests/ollama_evals/test_harness_property.py`,
  with a mutation check recorded. Verified again on this machine 2026-09-15:
  28 passed, 1 skipped in that file. Follow-on lives in TASKS.md § Planned:
  the overflow tail, NaN-cannot-classify, and scale invariance.
- **A8 — what each dependency manager requires of a topic, as data the CLI
  can read.** Delivered 2026-09-14 by the other machine's session as
  `dotfiles/managers.yaml`; the handoff snapshot and A9 both record it
  delivered, yet the task line stayed queued — found by the advisor pass.
  The design detail (four axes: variables, privilege, currency, channel
  selection; per-manager exceptions) is in git history under the A8 task
  line and in the file itself. Moved here per the finish-a-task convention.
- **Document that `git add -p` and `git commit -o` do not compose.** Landed
  2026-09-15: AGENTS.md § Working alongside other sessions now teaches the
  correct sequence for a co-edited file (add -p, then a bare commit with
  nothing else staged, then verify with `git show --stat HEAD`) instead of
  pairing `-o` with partial staging. Fixed before it bit — the advisor pass
  caught AGENTS.md still teaching the unsafe combination while the fix sat
  queued here.
- **Standardize the cross-machine directory layout — policy and plan first,
  then migration.** Reframed by the author from the registry capture,
  interviewed 2026-09-15 (three question rounds), approved the same day:
  the policy and six-phase plan are `docs/LAYOUT.md` (df080f7) — seven
  flat types under `~/code`, designed layout with both machines migrating,
  `machines.yml` declares membership with work names in a machine-local
  overlay, an Ansible topic owns the dirs and gita the repos, drift is
  guard-reported with auto-repair as the designed evolution. Same-session
  execution: this Mac migrated (seven type dirs exist,
  Best-README-Template → `templates/`, repo intact) and
  `dotfiles/machines.yml` carries this machine's membership (a3513d6).
  What remains lives in the plan, not here: the second-machine inventory
  (queued in § Now), the topic-owned skeleton (with the gita study), the
  second-machine migration, and the citation switch plus drift guard. The
  author's two permission-blocked steps are in the handoff.
- **Rework the project opencode permission config and add the `autonomous`
  agent.** Renamed `opencode.json` → `opencode.jsonc` (fa29fcd) so the map
  carries its why inline; deduplicated, ordered catch-all-first for
  last-match-wins, interpreters moved to allow, workhorse tooling added,
  `chezmoi apply` ask→deny to match the house main-only rule, and the inline
  `autonomous` primary agent added with a complete self-contained map
  (404e0ff). The global template's bash map had the catch-all `*` last,
  which would have shadowed every rule to `ask` at the next restart — moved
  to first (b20e3bf). Verified: string-aware JSONC parse plus structural
  asserts. Fresh-session both-directions check owed at the next restart.
- **Documented the opencode permission layer in `docs/PERMISSIONS.md`**
  (cfe1823): the global template and project `.jsonc`, deep-merge /
  project-overrides ordering, last-match-wins catch-all-first, the autonomy
  dial, and the built-in `--auto` mode. Noted the agent does not widen
  `external_directory`/`read`/`edit`, so the file boundary holds.
- **Fixed stale Claude path rules and moved history rewriting to ask.**
  `Read(//Users/ben.davis/...)` named a different machine's macOS home, so
  the secret-path denies never matched here; replaced with `~` (8cc3845),
  the documented username-agnostic form. `filter-branch`/`filter-repo`
  flipped deny→ask in both opencode (2c93932) and Claude (9df508d) so the
  human sees the command and applies the spec.md ceremony per invocation;
  force-push stays deny.
- **Added `docs/LANGUAGES.md`** (275bf48): script-directory→language
  inventory and a per-language formatter/linter/typecheck/test/LSP table,
  recording that the LSP home decision (global template vs per-repo
  `opencode.jsonc`) stays with the queued LSP profile task.

## 2026-09-16

- **Fix the dependency check for topics requiring `homebrew` on Debian, and
  extract resolution into a testable role.** The resolver probed for a
  `homebrew` binary, but Homebrew's CLI is `brew` on every platform, so
  `opencode` failed with `[TOPIC_NOT_RUN]` on a Debian box where linuxbrew
  was present. Resolution moved out of `playbook.yaml` pre_tasks into
  `dotfiles/roles/topic-resolution/` (23c0f8c), which maps the `homebrew`
  token to `brew` (`dependency_probe_binary`) and fixes the `fail_msg` path
  that pointed at the nonexistent `apps/<topic>/meta/main.yml`. The same
  facts and tags are emitted; behaviour is otherwise unchanged.
- **Test the resolution under both OS families.** `tests/topic_resolution/`
  (266763e) drives the role through ansible-playbook; `test_states.py`
  reaches all three states and `test_opencode_both_os.py` runs the real
  `apps/*/topic.yml` under Darwin and Debian. Mutation-proven: removing the
  alias turns the Debian leg red. 7 passed.
- **Guard the opencode topic's CRUD against OS-specific drift.**
  `tests/topics/test_opencode_os_agnostic.py` (947641f) asserts no
  `os_family` branch, no hard-coded brew prefix, and install/remove via
  `community.general.homebrew` from the pinned tap, with a counterweight so
  it cannot pass vacuously. Mutation-proven.
