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
   `~/.local/share/zsh/completions/_herdr` (corrected post-entry:
   `~/.zfunc` — herdr's documented recipe — is on nobody's fpath here, see
   the topic CHANGELOG); gated intersection-only teardown ordered integrations →
   service → entry; upgrades route through `mise upgrade`, never the tool's
   self-updater. **Done:** topic + catalogue exist and the swarm suite is green
   (116 tests as of the same-day close, from 108 at this entry's writing)
   with mutations proven. The three passes RAN the same day under an
   author-directed apply override (`78c9e55`): pass 1 green — the
   `mise upgrade` predicate verified live and the launchd management moved
   to `community.general.launchd` after a converge-pass fact-semantics bug
   (`ansible_facts['user_id']` is the username); the remove pass died once
   on an ungated claimed-ids reference (fixed, `9646f0f`) and the
   re-converge died once on a misleading outdated raise over removed state
   (fixed — upgrade now probes and relents, `1336766`); then the topic was
   proven on this Mac (`20c7d20`). Post-entry corrections, all recorded in
   the topic CHANGELOG: raw launchctl → the launchd module; `systemctl cat`
   → `stat` (author-ratified ladder); the status grammar grew to
   `current (vN)`; a test now compiles the task YAML's own regex strings
   against the golden fixture (the double-escape class bit twice).
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

- **Pinned the ansible collections (O1 exact) — resolved via the research-swarm pilot.**
(ai-prompt-library
  `skills/research/pilots/2026-09-19-requirements-pin.md`): **O1 — exact
  pins** (`community.general 13.0.1`, `community.docker 5.2.1`, the graded
  versions) with the bump signal wired into `docs/REFERENCES.md`'s
  quarter-boundary habit; a bump is a deliberate re-grade (edit, commit,
  reinstall, re-run affected suites, re-stamp grades). **O4 (Renovate
  automation) deferred with a reopen trigger**: adopt when the collection
  set grows past a handful, a missed-update incident occurs, or the queued
  scheduled-runner service lands and wants a job. Landed in
  `dotfiles/requirements.yml` + the REFERENCES row.

## 2026-09-22

- **Shift-left testing study: comprehensive-and-immediate feedback for
  humans and agents, ordered by execution speed.** Full method run:
  a 4-agent read-only swarm inventoried current test/lint/hook mechanics
  (measured the suite at ~200s, not the stale 104s claim; found prek is
  the active hook runner, not the stale pipx pre-commit claim), mined
  journaled lessons, and mapped the queued-item landscape and the
  author's 5 questions to existing evidence/gaps. A fusion council (real
  mixed models — deepseek-pro + glm-5.3 + local olmo-3.1, MLX models
  found broken on this ollama server and substituted) turned the
  findings into a deep-research brief, shown to the author before it
  went out. Two deep researchers (opencode Task agents with web access)
  returned findings on 8 threads (changed-file selection, on-save
  triggering, mutation testing, coverage, `$HOME` sandboxing, parallel
  execution, pre-push gates, progressive trust). Three advisor voices
  (incrementalist, trust architect, agent-workflow specialist)
  converged on a speed-ordered recommendation set, delivered to the
  author with a compact critique/rejection list and open questions.
  Questioning-skill exchange with the author produced the session's
  most consequential finding: **trust attaches to the mechanism, not the
  commit** — a two-track model (deterministic checks graduate fast and
  stay graduated; judgment-based mechanisms graduate on a rolling
  correction-rate window) now settled into `TASKS.md`'s LEDGER item, with
  the global-vs-per-repo trust-scoping question routed to
  `ai-prompt-library`'s blocked agent→function graduation item rather
  than decided here. **Adopted and queued as their own tasks in
  `TASKS.md`:** the pre-commit/merge-gate three-tier design (§ Now,
  supersedes the old pre-commit/pre-push framing); the fast-test-loop
  sequencing (fix slow tests → `pytest-randomly` → `pytest-xdist`, not
  the reverse) plus a `collected == 0` tripwire; the `$HOME`-sandbox
  implementation pattern (autouse fixture, subprocess `env=`, named
  macOS escapes); machine-shaped gate outputs + a skip census
  (coverage % explicitly rejected as the quality-over-time metric); the
  two-track trust model. **Deferred:** an ollama model-health check
  (§ Planned, low priority). **Promoted:** the standing-red permissions
  test, § Planned → § Now. **Left open, recorded in § Decisions waiting
  on the author:** bypass legitimacy, who audits the author's own
  review, which tests may touch real `$HOME`, the minimum gate set per
  task class. **Rejected by the advisor council, unanimous:**
  pytest-testmon/pytest-picked (blind to this repo's shell/YAML change
  surface; picked exits green on zero tests), coverage % as a tracked
  metric, a full suite on pre-push, a local CI daemon, cosmic-ray,
  mutmut as standing practice.
- **Standing-red permissions test fixed — the ask-vs-deny call is ask.**
  Author decision 2026-09-22: `git filter-repo` follows the settings change
  (`9df508d`), not the reverted test expectation — `docs/PERMISSIONS.md` and
  `.claude/settings.json` already agreed on ask ("history rewriting —
  irreversible but legitimate") before this task started; the test was the
  only stale side. `tests/permissions/test_permission_tiers.py:57` updated;
  targeted test green (24 passed); full documented suite command re-run and
  confirmed **0 failed** (638 passed, 7 skipped, 7 deselected, 189.01s) —
  the mutation discipline's green baseline is restored.

## 2026-09-23

- **Captured the approved gita + machine-file-backup plan in a worktree
  handoff.** Outcome: `HANDOFF.md` on `agent/gita-plan`
  (`.worktrees/gita-plan`, commit 46042e9) carries the plan the author
  approved 2026-09-23 — 41 settled decisions with their evidence, items
  G0–G7 and BK1–BK4 with done-conditions and binding order, the six-critic
  council's accepted objections, and corrections to two earlier claims (gh
  here is installed by hand from GitHub's apt repo, not deb-get; the Linux
  keychain path is the GNOME keyring, since this box predates
  `systemd-creds`). Both done-conditions met: the handoff exists on the
  branch, and the gita row in § Picking this back up points at it and names
  G0 as the start. The durable record is the handoff until G0 transcribes
  it into `TASKS.md` and `PRD.md`; the branch is a record, not merge-bound.
- **Study gita across the machines and decide its topic's shape.** Design
  resolved by the author's approved 2026-09-23 plan, recorded in
  `agent/gita-plan:HANDOFF.md` (`46042e9`) and transcribed into `TASKS.md`
  § Gita and machine-file backup. Outcome: standalone `apps/gita`, a
  personal-repo catalogue, named sets selected locally, separate private/work
  files, and backups proven before real machine-file data is seeded. The
  git-config topic stays separate. G3 carries all five registration lessons:
  recursive registration, basename-collision detection with relative-path
  membership, `.venv` exclusion, word-counting `gita ls`, and adopting existing
  registrations. The original study's inventory and existing-config detection
  are not claimed complete: the second-machine inventory and G3 own them.
  The original baseline was recorded on the Mac in September 2026; the
  handoff's Linux attribution needs target-side verification, noted in G3.
- **G0a — independent PRD transcription review.** The fresh
  `gita-plan_sub_prd` session checked handoff decisions 33–41 against the
  draft and spec. Its two corrections landed in `dace703`: date later
  author-approved amendments in the introduction and retain the managed-device
  acceptable-use objection beside the rule. No design change or runtime
  verification was claimed. The orchestrator reconciled the review on main
  under the author's explicit G0 commit authorisation.
- **G0b — independent queue transcription review.** The fresh
  `gita-plan_sub_queue` session mapped all 41 handoff decisions to proposed
  task patches. After its sandbox could not read the temporary draft, it
  transcribed the handoff directly. The orchestrator reviewed and integrated
  the common order and each task separately (`6dd6820` through `32a94bf`),
  with `tests/tasks_doc` passing before each commit. The queue retains its
  implementation questions, permission-work allocation and target-specific
  baseline correction. No runtime behaviour was exercised.
- **Fold G0's uv side finding into the existing U1 task.** Another session
  queued § Now #1 (p) U1 while G0's transcription was in progress, including
  the same evidence and the author's system-pin decision. Removed the duplicate
  queued in `c94ed6f`; U1 remains the single open implementation task. This
  resolves duplicate tracking, not the installation mismatch.
- **G0 — record the approved gita and configuration-backup plan.** Resumed
  from `agent/gita-plan`'s `HANDOFF.md` (`46042e9`), with two fresh review
  agents in separate sub-worktrees. The author authorised orchestrator
  review and separate main-side commits for this transcription. `dace703`
  records the PRD rule with adjacent employer-risk dissent; `d60f984`
  resolves the gita study; `49aca09` through `5617e9c` queue G1–G7/BK1–BK4;
  `b1df9ad` and `32a94bf` queue the hostname and bundle findings. The uv
  finding has one home in U1 after `8d85f02`. `4e89860` revises the broader
  backup task without closing the employer-policy review. Each queue commit
  had a passing `tests/tasks_doc` run. This proves documentation structure,
  not gita or backup behaviour. The next work is G1, BK1 and Linux inventory;
  real machine files still wait for the complete BK2–BK4 restore gate.

## 2026-09-24

- **Evaluate Worktrunk against `mise run worktree-new`.**
  [agent: opencode-worktree-isolation] Tested Worktrunk 0.79.0 with mise
  2026.9.12 on macOS using an invented account in a disposable local clone.
  The mise wrapper already generates and checks a worktree-local denylist.
  Worktrunk can call those tasks from `pre-start`, but has no such hook
  configured today. Removing generation blocked the first launch; switching
  into the failed tree again skipped the creation hook. Explicit hook retry
  repaired it. A loopback-port probe confirmed shared networking; `HOME`
  remained shared too. Recommend Worktrunk for lifecycle management, mise for
  setup, and readiness checks on existing worktrees. Runtime isolation remains
  a separate requirement. Detailed findings are in the originating project's
  `docs/research/worktree-runtime-isolation.md`; trial files remain under
  `~/code/try/worktrunk-isolation-trial`. No live workflow configuration changed.

- **Research interchangeable agent-work components.**
  [agent: general/sandbox-components; coordinator: OpenCode, 2026-09-24]
  Completed the author-approved comparison of task sources, orchestration,
  session interfaces, workspace providers, environments and sandbox runtimes.
  Local implementations and proposals were checked alongside pinned upstream
  sources. Report: `.worktrees/wt-restart/.claude/RESEARCH-modular-agent-runtime.md`
  (local, uncommitted). It includes queue, sandbox and workspace swap traces;
  only the narrow SRT-to-mise filesystem substitution was exercised.
  Mac synthetic probes established allowed and denied operations and found
  lifecycle/network limits. Coordinator reruns confirmed SRT 0.0.77 reporting
  self-SIGTERM as exit 0, mise 2026.9.12 failing host-network exceptions, and
  both enforcing tested filesystem scopes. Debian, queue contention, session
  restore and full swaps remain unrun. Pilot selection remains in § Now;
  no live component was selected by the research report.

## 2026-09-28

- **Allow worktree creation and read-only `gh`; deny `--force-with-lease=`.**
  [agent: OpenCode restart-review] Landed as PR #8 (`5b62dfd`) in three
  commits, one per decision, plus the carried branch/worktree narrowing.
  `tests/permissions/test_opencode_tiers.py` now models opencode's
  last-match-wins tiers; four mutations were each caught. The Claude Code
  `gh` carve-out was left to the permission-rules review, because deny > ask
  > allow precedence cannot carve reads out of `Bash(gh *)`. Real enforcement
  in a fresh session was not verified.
- **Label meld's panes from sections git actually reads.** [agent: OpenCode
  restart-review] Landed as PR #10 (`caa041b`): `[mergetool "meld"]` and
  `[difftool "meld"]` carry the labels; a test renders the template and asks
  git what it resolves. Git now judges a merge by whether `$MERGED` changed.
  No live `git mergetool` session was run.
- **Document bucketing a task into PRs.** [agent: OpenCode restart-review]
  Landed as PR #13 (`1e5d099`): `docs/WORKTREES.md` § Bucketing, a Bucket
  lifecycle step, and reaping cherry-picked branches with `git cherry`.
- **Open pull requests only into `main`.** [agent: OpenCode restart-review]
  Began as a warning after PR #12 merged into its parent's branch and had to
  be re-landed as #15; the author replaced the warning with the rule. Landed
  as PR #23 (`7b855cd`) in `docs/WORKTREES.md` § Bucketing step 6 and
  AGENTS.md § Branches and integration.

## 2026-10-03

- **Open a review PR for the ollama manifest-scope work on
  `feat/ollama-manifest-scope`.** [agent: housekeeping / opencode] Rebased
  onto main (was 273 commits behind) and landed as PR #41 with three commits:
  c8cdc7c the comment-preserving manifest editor, 4f681da the gated `adopt`
  command, fb2d96b a YAML 1.1 fix the property tests caught (bare keys like
  `no` parse as booleans; `_yaml_safe_key` quotes them). ollama_models 74/74
  green, full suite 946 passed / 6 skipped. PR #41 awaits human review — the
  diff touches a deployed-tree file.
- **Build a machine-assisted merge-gate checker.** [agent: opencode] Landed
  as `scripts/check_merge_gates.py` (commits 220be02 claim, abb35bd stale
  citation fixes, 9cd0940 the script plus tests/merge_gates). Advisory-only
  per the author's 2026-10-03 decision; deliberately not a git hook.
  Deployed bucket reads real `chezmoi managed`; policy enumeration confirmed
  by inspection: `bin/executable_policy` (deployed+policy), `.claude/
  settings.json`, `opencode.jsonc` (deploy-ignored),
  `dot_config/opencode/opencode.jsonc.tmpl` (deployed+policy), glob
  `dotfiles/policy/*`; egress stays a printed reminder. Two mutations were
  each caught (policy never fires → 8 red; degraded fail-closed claims
  docs-only → 2 red). Real-run verification classified PR #41's branch
  diff correctly (README deployed+docs, role files deployed, tests other,
  verdict PR) and surfaced this observation: **dotfiles/docs/** is
  chezmoi-managed (16 paths as of 2026-10-03), so a "docs-only" diff inside
  dotfiles/docs is also a deployed-tree diff — the merge-gate prose in
  AGENTS.md treats "docs" and "deployed-tree" as separable, and for that
  subtree they are not.
- **Wire ruff's LSP into the repo-scoped opencode.jsonc, beside pyrefly.**
  [agent: opencode, author-directed] Landed in three commits (9ee9b41 task
  + claim, f12188f the wiring + pin, 59057cb stale-claim refresh): the
  `lsp` section gains `"ruff": { "command": ["ruff", "server"],
  "extensions": [".py", ".pyi"] }`, pinned by
  `tests/permissions/test_opencode_tiers.py::test_lsp_pins_the_python_servers`.
  Verified: JSONC parses; a full initialize/initialized handshake against
  `ruff server` returns capabilities (quickfix, fixAll.ruff,
  organizeImports). Mutation: ruff entry deleted → the pin test failed
  alone, 1 failed / 47 passed; restored green, 48 passed. docs/LANGUAGES.md
  and the queued opencode-LSP task no longer claim LSP is unwired; the
  global-vs-repo home decision and bash/yaml servers stay with the queued
  task. Takes effect on opencode restart.

  Second observation, recorded 2026-10-03 by the building session: the full
  suite run from any cwd under `~/.local/share/chezmoi` fails tests/policy
  19 times with a mise error naming an R toolchain; the identical suite
  passes (33 passed, 5 skipped) from a neutral cwd (`~/code/...`), and the
  identical failure set reproduces on `main` without this diff. The suite
  is cwd-sensitive, so full-suite results from the main checkout cannot be
  trusted as gate evidence until this is root-caused.

  Process note: commits 9cd0940 and 9181346 were landed in this worktree by
  a second session while the building session was verifying — a
  one-writer-per-worktree violation (docs/WORKTREES.md), reported by the
  author 2026-10-03. The building session verified both commits' content
  before merging: file sets correct, resolved entry accurate.

- **Root-cause the tests/policy cwd-sensitivity.** [agent: opencode]
  Landed as `3367a7f` (2026-10-03). The mechanism was the fixtures' PATH
  construction, not mise config discovery: `shutil.which("uv")` resolves to
  the mise shim or the real binary depending on how pytest was launched,
  and the shim re-entered mise under the stripped HOME, failed the trust
  check against the real global config, and exited 1 — DENIED on the
  resolver's scale, so deny-direction tests passed while the resolver
  never answered and only relent-direction tests failed. One shared
  helper (`policy_harness.uv_dir()`) now feeds all three fixtures. Full
  suite green from the main-checkout side for the first time (916 passed,
  0 failed); tests/policy green from both cwds. Mutation: `uv_dir` neutered
  — 22 red from the failing cwd.

- **Fail the per-GPU ollama check on a backend fallback.** [agent: opencode]
  Landed as `066e7c8` (2026-10-03). The confirm task now classifies the
  instance's own inference-compute line: `library=vulkan/cpu` or a
  "no compatible gpus" line fails red and non-fatally (`ignore_errors`;
  the per-instance report below still carries the FELL BACK/UNREAD line);
  a missing GPU line stays report-only, since a fresh server that has not
  loaded a model legitimately has none. Pinned by 12 tests in
  tests/ollama_gpu_confirm running the rendered script against a stubbed
  journalctl. Mutation: fallback verdict exits 0 — 4 red; no-compatible
  verdict exits 0 + UNREAD guard never fires — 2 red. Gates: 929 passed,
  ruff/pyrefly/skillet clean.

- **Teach `skill-trust` about foreign skill buckets.** [agent: opencode]
  Already landed on `main` when this closeout ran, 2026-10-03 — the § Now
  line still said "implemented, awaiting review" on the branch
  `skill-trust-foreign-buckets`, but the work merged as `27e9188` (external
  verdict, deny refused), `903541e` (guard flag plumbed) and `b26ca9c`
  (docs + status), with `eb0b4b2` the earlier licence-reporting half. The
  branch and its worktree were later deleted. Verified on `main` before
  closing: `guard_foreign_buckets: true` (roles/guards/defaults/main.yaml:81),
  `opencode_skill_foreign: true` (apps/opencode/defaults/main.yaml:95)
  plumbed at install.yaml:226, and the proprietary-licence reporting pinned
  in tools/skill-trust/tests. Still open, blocking nothing: a machine id
  that survives a rebuild for the Part 2 rules filename, and whether a
  fourth `blocked` verdict is worth having.

- **Make the test suite fast and model-safe.** [agent: opencode] Already
  landed on `main` when this closeout ran — merged as `118aaa6`
  (`test-perf-xdist`); the § Now line still said "awaiting author review".
  The done-conditions held on merge: one invocation collects every test
  directory, `addopts = ["-m", "not llm_judge"]` keeps real model calls out
  of the default run (both directions tested in tests/suite), and the xdist
  fast loop is measured at 170.7s → ~47s on this machine. Seven open
  author-decision items from the original entry survive here rather than in
  a § Now line: (1) judge/model ids absent on this machine
  (`qwen3.5:4b-mlx-bf16`, `devstral-small-2`, vendor-native
  `claude-4-sonnet`) — install, substitute, or skip-with-reason;
  (2) two `test_binned_cli` cases pass vacuously on a parse-error message;
  (3) source-vs-deployed testing is inconsistent across suites;
  (4) whether `tools` stays in `testpaths`; (5) `tests/clipped` clipboard
  cases are slow and order-dependent; (6) the "104s" suite figure is stale
  (170.7s measured 2026-09-23); (7) run one suite at a time — concurrent
  `uv run` invocations contend on the uv cache lock.


## 2026-10-11 closeout — opencode v2 migration units (PR #46 merged)

The three unit lines moved here from § Now; PR #46 merged 2026-10-11
(merge commit 0f7f32e) with the migration commits this branch produced.

- **opencode v2 migration — plan (apps/opencode v1 → v2).** [agent:
  orch_sub_oc2plan, worktree `.worktrees/orch_sub_oc2plan`] Research and
  write the migration plan. Verified 2026-10-06: v2 is 2.0.24; the same
  tap `anomalyco/tap` carries formula `opencode-v2`, which declares
  `conflicts_with "opencode"` and `depends_on "ripgrep"`; the author
  chose the brew-tap route over npm (npm is blocked on this box by a
  root-owned `/tmp/fslock` — standing machine issue, see § Cross-session
  hazards), wants the chezmoi config migrated in the same work item, and
  wants the mise-installed opencode 1.18 shadow (it outranks the brew
  binary on PATH) removed after the ansible migration is verified. Open
  research the plan must settle from v2 sources or release notes, not
  assumption: whether v2 parses v1's `permission` map schema at all (v2
  docs show only the ordered `permissions` array), and the exact v2
  syntax for bash rules and `external_directory` path rules. Plan lands
  at `dotfiles/docs/research/opencode-v2/PLAN.md`. Done when it names
  every file that changes (topic tasks/defaults/README/CHANGELOG plus
  the chezmoi config), the v1→v2 permission mapping, the brew v1
  formula removal, teardown updated in the same change, verification
  steps, and any open author decisions.

  Landed 2026-10-06 on `agent/orch` (merged from `orch_sub_oc2plan`):
  plan at `dotfiles/docs/research/opencode-v2/PLAN.md` (`5332d18`,
  rulings amendment `1d60ebb`). Awaiting the PR review; resolves when it
  merges.

- **opencode v2 migration — tests.** [agent: orch_sub_oc2test, worktree
  `.worktrees/orch_sub_oc2test`] From the plan, write the pytest
  coverage the implementation must satisfy before the implementation
  exists: extend `tests/topic_resolution/test_opencode_both_os.py`,
  `tests/topics/test_opencode_*.py` and the `tests/guards/` wiring
  tests as the plan directs, covering the v2 formula install, the
  conflicting v1 formula removal in the same run, teardown of
  everything the new install creates, and the migrated config schema
  rendered under both os_family values with StrictUndefined. Written
  before the migration lands — expected red against v1 state, green
  after. Done when every new test has been seen to fail (mutation and
  failing test named, recorded as trailers on the implementation
  commit) and the rest of the suite stays green.

  Landed 2026-10-06 on `agent/orch` (merged from `orch_sub_oc2test`):
  14 v2-targeted tests seen red against v1 state (`8050bd1`), plus a
  prerequisite hook fix for tests/ollama_models/conftest.py whose
  pre-existing pyrefly and W505 failures blocked every local
  Python-file commit (`1916084`). Green after the implementation
  commits.

- **opencode v2 migration — implement.** [agent: orch_sub_oc2mig,
  worktree `.worktrees/orch_sub_oc2mig`] Apply the plan and make the
  tests green: `apps/opencode` tasks install `anomalyco/tap/opencode-v2`
  and remove the conflicting v1 formula in the same run, teardown
  updated in the same change, `dot_config/opencode/opencode.jsonc.tmpl`
  migrated to the v2 permissions schema, README and CHANGELOG updated.
  Follow-up machine state is author-run, never agent: `chezmoi apply`,
  run-role for the topic (run-role.sh is cwd-dependent — run from
  `dotfiles/`, see the 2026-10-03 observation above), then removal of
  the mise-installed opencode 1.18 that shadows the brew binary. Done
  when the new tests pass, the topic renders under both os_family
  values, and the diff goes to the author for review (PR; deployed-tree
  paths are always human review per § Merge gates).

  Landed 2026-10-06 on `agent/orch` (merged from `orch_sub_oc2mig`):
  topic commit `9d448f5`, config commit `c26f4ac`; the 14 queued tests
  green (mutation evidence on the commits), full battery matches main
  except 13 pre-existing failures in clipped/restart_stale/herdr,
  reproduced on main's merge-base. PR opened to main; resolves when the
  author merges.
