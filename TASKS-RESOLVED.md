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

## 2026-09-17

- **Brought the cursor topic to TOPICS.md conformance and verified it.**
  The topic already existed and was live (installed on this Mac, parent
  playbook discovers it); the residue was missing CHANGELOG.md, a
  template-boilerplate README, and a dead pre-role `tasks.yaml`. Added the
  dated CHANGELOG.md (antsibull categories; known-issues record the
  auto_updates cask drift, the not-yet-designed extension gap, and the
  OpenVSX marketplace difference), rewrote the README, removed `tasks.yaml`
  (grep-verified unreferenced) in b117f86. Evidence:
  `--syntax-check` clean; `--check --tags provision` converged
  (ok=2 changed=0 failed=0); `--check --tags remove` reported the expected
  would-change (changed=1 failed=0). Residue noted for others: `meld` and
  `rectangle` still carry their `tasks.yaml`; the queued per-topic-suite
  item owns cursor's tests when it lands.
- **Refreshed `vs_extensions.txt` and recorded why nothing kept it
  current.** Manifest was 18 entries against 40 actually installed
  (`code --list-extensions`, 2026-09-17). Captured the live list (verified
  identical by diff) in 8e25e32 and recorded the diagnosis in the vscode
  topic's new CHANGELOG.md: the topic installs cask-only, export/import are
  hand-run `.manual` scripts wired to nothing, so post-export installs stay
  invisible to the repo. Wiring a refresh in belongs to the downstream-IDE
  design item (still queued in § Now). Also recorded there: the `.manual`
  scripts exist twice (topic root and `files/`).
- **Ran the downstream-IDE advisor council; its owner-topic design was NOT
  adopted — superseded by the author's system-config subscription model.**
  Three advisors (architect, pragmatist, skeptic), two rounds with
  cross-questioning, converged on: a data-only owner topic owning the
  shared manifest, per-entry `editors:` scoping, dated add-time verdicts,
  collect-fail-once, consumers declaring `topic_downstream_of` and
  importing one shared loop, gated teardown before the cask, report-only
  GUI drift. Author rejected that shape (2026-09-17) and adopted instead:
  **topics never read topics** — shared truth lives in
  `dotfiles/config/<domain>.yaml` (file per domain, folder-isolated from
  playbook.yaml), a topic declares `topic_subscribes: [<catalogue>]` in
  topic.yml, the parent playbook validates the catalogue, resolves the
  subscriber's slice, and injects it; topics carry only thin
  install-and-report loops; unresolvable verdicts fail at the playbook
  layer before anything installs. What survived from the council into the
  adopted shape: the manifest schema (`id`/`why`/`editors:`), dated
  add-time verdicts, collect-then-fail-once, gated teardown ordering
  (extensions before the cask), `--update-extensions` currency, report-only
  drift, retiring the `.manual` scripts and `vs_extensions.txt`. What died:
  the owner topic, `topic_downstream_of`, cross-topic `import_role`.
  Empirical evidence recorded in `apps/cursor/CHANGELOG.md` known_issues:
  the Anysphere substitution probe (anysphere.cursorpyright installs
  unrequested alongside ms-python.python; machine restored to zero) and
  the CLI facts. Wiring queued on the adopted shape (config seed in § Now;
  machinery and both consumers in § Planned, gated on the topic spec).
- **Seeded `dotfiles/config/editors.yaml` — the shared editor-extension
  catalogue.** The data half of the adopted model, first file under the
  new `config/` directory, in b4bc9db. Header states the subscription model, the four-part threshold for
  earning a new catalogue file, and the fold-back rule. 40 entries seeded
  from the live set, whys drafted for review with suspected overlaps
  flagged in place (two env managers, two Jinja, two TOML, and
  ktiays.aicursor's purpose unconfirmed). Verdicts dated from the
  2026-09-17 Open VSX sweep of all 40: 36 shared with cursor, 4
  vscode-only (pylance and the two closed-source Intellicodes as
  predicted; jinliming2.vscode-go-template the surprise 404 — flagged in
  its why for a drop-or-scope decision). The expected Anysphere extra
  (anysphere.cursorpyright, substituted) recorded under
  `editor_extensions_ignored`. Verified by a schema check: parse, count,
  id-set equal to the live manifest, why present on every entry, verdict
  dates present, 404-entries scoped. Note for the machinery task: plain
  YAML scalars cannot contain `: ` — the review marker is "Review —" for
  that reason.
- **Updated the visual-studio-code topic: conformance, retirement of the
  superseded record, and the interim catalogue wiring.** Author direction
  2026-09-17 ("update vscode topic while we're here" then "also wire
  now"). Three commits: the retirement (vs_extensions.txt and all four
  `.manual` copies deleted; `removed_features` entry records the why —
  the scripts were the drift mechanism — and notes the `files/` copies
  clear from the deployed tree on next apply); the wiring (install/
  remove/upgrade carry the interim direct-read contract — role-relative
  catalogue path, slice resolution with topic-local isolation, one
  verdict line per entry, fail-once naming unresolved ids, gated
  teardown before the cask, `--update-extensions` currency; guarded by
  the new `tests/config/test_editors_catalogue.py`, mutation-proven);
  the conformance (real README describing the wired topic, dead
  `tasks.yaml` out). Done-conditions met: retired files gone and
  unreferenced (grep-verified before deletion), `--syntax-check` clean,
  `--check --tags provision/install/upgrade` and `--tags remove` with the
  gate both off and on all `failed=0`, verdict lines print per entry,
  schema test red under mutation and green restored. Two bugs caught by
  the checks, fixed in the wiring commit: ansible's filter is `intersect`
  (not `intersection`), and the ignore-filter's Jinja precedence (filters
  bind tighter than `+`) needed the reject to wrap the whole sum. Queue
  revisions in the same session: the planned vscode task became the
  injection switch, and the cursor task notes the interim contract. The
  real convergence run (install as a no-op against the 40 already
  installed) is the author's apply.
- **Created the `herdr` topic, test-first, per the locked design.** Author
  design Q&A 2026-09-18/19; agent work 2026-09-19. Both OSes; the binary
  installs through mise with the topic owning the entry (probe-first
  `mise use -g herdr`, `mise unuse --global herdr` last; the entry is
  committed in `apps/mise/files/config.toml` as the capture); shared catalogue
  `dotfiles/config/agents.yaml` (opencode + claude wired, cursor
  skip-and-report, all 18 upstream ids wired-or-ignored); launchd gui-domain
  agent + systemd user unit at the stable shim path with health checks;
  minimal `~/.config/herdr/config.toml`; topic-owned zsh completion into
  `~/.zfunc/_herdr`; gated intersection-only teardown ordered integrations →
  service → entry; upgrades route through `mise upgrade`, never the tool's
  self-updater. **Done:** topic + catalogue exist and the swarm suite is green
  (108 tests) with six mutations proven; the author's three real passes
  (converge, second-run idempotence, remove) are QUEUED, not run — agents
  never apply; the `mise upgrade` output predicate and `launchctl enable`
  idempotence are recorded in the topic CHANGELOG as what those passes settle.
  Collision event recorded: the shared symlinked mise config was rewritten by
  another process mid-edit (entry removed and restored within a second) — the
  hazard TASKS.md documents for that file, now observed live.
- **Established the herdr test program: independent author-swarm + measured
  judge loop.** Author request 2026-09-19. Four fresh-context agents deduced
  the contract from written artifacts only and authored failing-first suites
  along lifecycle / catalogue+loop / user-acceptance / edge-stress dimensions;
  two test-fixture bugs and one suite regex bug were caught by first red runs
  and fixed in place. Judges calibrated against an injected-defect set
  (`tests/herdr/calibration/`, key kept out of the judge-facing dossier after
  run-1 contamination — one judge caught the leak unprompted); mid-round judge
  `~deepseek/deepseek-pro-latest` returned ITERATE (2 high, 3 medium, 1 low);
  all six triaged (two resolved with measured fixes — a golden transcript
  against the real binary caught the `letta (experimental)` wire variant, and
  the YAML-side grammar wiring exposed a latent double-escaping bug; one
  accepted with a named home in the repo-queued molecule adoption); final
  fusion panel (opus-4.7 + deepseek-pro + local qwen3.6:35b-mlx) returned SHIP
  unanimously, no new high-severity gaps. **Done:** rounds recorded in
  `tests/herdr/calibration/ROUNDS.md`; method + pool recommendation in
  `dotfiles/docs/JUDGE-SELECTION.md`; generalizations in
  `dotfiles/docs/TOPIC-RECIPES.md` for the next topic.
