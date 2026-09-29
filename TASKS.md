# TASKS.md

Shared work queue for this repo. Agent sessions keep their own in-memory task
lists, which fragment the moment more than one is running — this file is the
durable version. Read it at the start of a session; update it before you finish.

Keep it short. This tracks *open* work and cross-session hazards, not history —
`git log` already has history, and duplicating it here just creates drift.

## Conventions

- **Editing this file: bound deletions by section, not by item.** Removing a
  task by slicing from its start to the next line beginning `- ` has destroyed a
  whole section three times, because the task being removed was the last in its
  section and the next such line was in the following one. Bound by the next
  item **or** the next `## ` heading, whichever comes first, and check
  `tests/tasks_doc` before committing — it caught the third one and was ignored.
- **Three tiers, and the test between them.** If you can write "done when X" in
  one sentence it is a task; if you cannot, it is an idea and belongs in
  `ROADMAP.md`. Among tasks, **Now** is the handful actually next and **Planned**
  is everything else. Promote from Planned into Now rather than working straight
  out of Planned — if everything is Now, nothing is.
- **Task or roadmap item?** If you can write "done when X" in one sentence, it
  is a task and belongs here. If you cannot, it is direction and belongs in
  `ROADMAP.md`. Nothing else distinguishes them — not size, not importance, not
  how soon. An item here is finished when it moves to `TASKS-RESOLVED.md` — a stopgap until the process refactor lands; a roadmap item is never finished.
- One line per item, imperative, with enough context to pick it up cold.
- **Captures commit immediately.** Anything an agent queues here or captures
  for later gets its own commit on its own branch, the moment it is written —
  so it exits the conversation and cannot be lost to session context, even
  when nothing else will be done with it. Kept separate from in-flight work.
  **One task, one commit** — queueing two tasks is two commits, and amending a
  queued task is another, never a rewrite of the commit that added it. Merge
  the branch promptly: an unmerged capture is invisible to every other session,
  which is the cost this rule trades for not colliding on main. See
  `AGENTS.md` § Everything is branched.
- **Append at the end of a section; never reflow or reorder.** Two branches
  appending to different section ends merge cleanly. Two rewriting the same
  lines do not.
- Mark **[blocked: reason]** rather than deleting — a blocked item that vanishes
  gets rediscovered from scratch.
- Mark **[inferred]** for anything reconstructed from repo evidence rather than
  stated by the author. Those may be wrong; correct them rather than trusting them.
- When you claim an item, say so in the line. When you finish it, move the
  line to `TASKS-RESOLVED.md` with its outcome and evidence — a stopgap until
  the process refactor lands, after which this rule follows the design.
  Either way the commit is the record.
- **Work done by an agent or subagent gets its task written first.** Before the
  agent starts, the line says what it is doing and what done means. Fanning work
  out across several agents is several tasks, not one — an agent whose unit of
  work was never defined returns something plausible that nothing can check.
- Assigned work names its owner: `[agent: <who>]` for a subagent or named
  session, `[me]` for the author. An unassigned task is a backlog item, not
  work in flight.

## Claimed

Sessions run in parallel and cannot see each other. Add a line when you start on
anything that touches a file in **Cross-session hazards** below, or that will hold
a global resource (ollama, `chezmoi apply`) for more than a minute. Delete your
line when you stop — including when you stop without finishing.

Append; never reflow or reorder this section. Two sessions editing the same lines
is exactly the collision it exists to prevent.

Format: `- <UTC start> — <what> — <files or resource>`

A stale claim is not a lock. If a line looks abandoned, check `git log -3` on the
file and whether a process is still running before assuming it is safe — then
delete the line and say so in your commit.

- 2026-09-24T00:25Z — skill-trust foreign buckets (branch
  `skill-trust-foreign-buckets`, worktree
  `~/code/wt-skill-trust-foreign-buckets`) — `tools/skill-trust/**`,
  `dotfiles/apps/opencode/**`, `dotfiles/roles/guards/**`
- 2026-09-29T15:00Z — repo-manager orchestrator takeover — TASKS.md § Now
  repo-manager line, `dotfiles/docs/research/repo-manager/**` (branch
  `agent/repo-manager`, worktree `.worktrees/repo-manager`)


## Where things stand — 2026-09-23 (the session handoff)

A handoff snapshot. Delete and rewrite it rather than appending; a log of
snapshots is worse than none.

**The orchestrator instruction (most important).** The next agent will act
as the author's assistant and orchestrator. For each task, it will use a
separate agent (fresh session) working in its own sub-worktree. If tasks
can be paralleled within the orchestrator's worktree, it will reassign
agents accordingly. It will use the sub-worktree format
(`.worktrees/<sid>_sub_<slug>`, branch `agent/<sid>_sub_<slug>`) and will
ask the author using the interaction-questioning skill when unsure about
anything. Fresh sessions and agents for each task — no shared context
between task agents.

**Session plan.** The orchestrator works in `.worktrees/orch` on branch
`agent/orch`. For each task it:
1. Creates a sub-worktree: `git worktree add .worktrees/orch_sub_<slug> -b agent/orch_sub_<slug> agent/orch`
2. Spawns a fresh Task agent with the task brief and the sub-worktree path
3. The sub-agent works in the sub-worktree (absolute paths + bash `workdir`)
4. The orchestrator collects results and merges serially (inert → behaviour → activating)
5. Deletes the sub-worktree after `merge-base --is-ancestor` proves the work landed

Tasks that touch TASKS.md or governance docs (spec.md, PRD.md, AGENTS.md)
are main-only — they cannot go in sub-worktrees. Tasks that need machine
state (`chezmoi apply`, package installs, deployed tree) are serial and
need the author's involvement.

**Objective.** Build a multi-agent coordination layer: an orchestrator
decomposes tasks, fans out parallel sub-agents that write in isolation,
consolidates their work without corrupting git history, and escalates to
the human only when necessary. Bootstrap here, extract to a copier
template later.

**What landed 2026-09-23.** Phase 1 items 2–14 of the multi-agent
handoff, each its own commit to main:

| SHA | What |
|---|---|
| `b0a1b08` | Sub-items (h)–(n) into § Now #1 |
| `ba50e33` | spec § Writing: plain English binds conversation |
| `b28dfca` | spec § Writing: calibration rule |
| `7a9fed9` | spec § Dependencies: referenced skill is declared |
| `69b3107` | spec § Writing: glossary linking rule |
| `a475a2b` | docs/GLOSSARY.md |
| `995cbc3` | .worktrees/ in tracked .gitignore |
| `033fd40` | docs/WORKTREES.md |
| `6ed496c` | Phase 2 experiments as sub-item (o) |
| `bdab641` | dotagents vetting line in install.yaml |
| `d0ea6be` | Task: author explain-calibration |
| `ac19f2d` | Task: author feynman-explanation |
| `5725275` | Task: declare both skills as agentic dependencies |
| `cf1d61a` | Handoff annotation with SHAs |
| `e9359b2` | Task: permission-rules review |

**Worktree status.** This session worked in the main checkout on `main`.
`test-perf-xdist` (`.worktrees/test-perf`) branches from `d0ea6be`, one of
this session's commits — so "moving" this session's work off main is not
possible without breaking that branch. The 13 commits stay on main. The
next session works in `.worktrees/orch` on `agent/orch`. Two additional
worktrees appeared mid-session from other sessions: `.worktrees/pyproject`
on `agent/pyproject` and `.worktrees/test-perf` (moved to `a58e710`).

**Sub-worktree conflict scan (2026-09-23).** Only 9 of 139 open tasks are
fully sub-worktree-safe. Finishable without an author answer:
- zshrc `/home/bdavis` sweep (TASKS.md:858) — one file
- bin/triage tests (TASKS.md:1797) — new test dir
- Bundle schema (TASKS.md:2010) — collides with task 547 on TOPICS.md
- OpenTypeless (TASKS.md:1690) — research only

70 items need global/deployed state (class C); 105 are owned or routed
elsewhere (class E). Key hazards: shared `.git/hooks` (one hooks directory
for all worktrees), tests that check main's tree instead of the worktree's,
and the default suite calling real models until the pytest.ini change lands.

**New task queued 2026-09-23.** Permission rules review: a subagent
reviews help menus and manuals for all tools the repo's agents invoke,
derives minimal allow/ask/deny rules, and writes them into `opencode.jsonc`,
`.claude/settings.json`, and Cursor's config. Goal: fewer prompts without
weakening the deny tier. Known gaps: `env *` is an arbitrary-exec wrapper
in the allow tier; `sed -i`/`awk system()`/`rg --pre` can execute code;
`git checkout .`/`git restore .` destroy uncommitted work; `git -C`
bypasses subcommand-level rules.

**Verified facts.**

| Fact | Evidence |
|---|---|
| `test-perf-xdist` branches from `d0ea6be` | `git merge-base` |
| `fix/apt-lock-and-trust` branches from `5a4c25a` | `git merge-base` |
| § Claimed is empty despite four active worktrees | `TASKS.md` |
| `env *` in allow tier — arbitrary-exec wrapper | `opencode.jsonc:109` |
| `sed -i`, `awk system()`, `rg --pre` can execute code | `opencode.jsonc:97-98,94` |
| `git checkout .` / `git restore .` destroy uncommitted work | `opencode.jsonc:40-41` |
| No Cursor permission config exists | `dotfiles/apps/cursor/` |
| `chezmoi *` bare allow would let `chezmoi apply` through | `tests/permissions/test_permission_tiers.py:91-95` |

**Settled decisions** (carried forward from 2026-09-22, still in force):
1–33 as recorded in the previous handoff (`git show 5ae9cc3:TASKS.md`).
Key ones for the orchestrator: worktrees in-tree at `.worktrees/` (1),
flat naming (2), one writer per worktree (5), sub-worktrees branch off
parent (4), serial merge with suite after each (16), never `git branch -D`
until `merge-base --is-ancestor` (h).

**Corrections to earlier claims.**
- The 2026-09-22 handoff's Phase 0 claim "no worktrees" is stale — four
  worktrees now exist (`.worktrees/apt-trust`, `.worktrees/orch`,
  `.worktrees/pyproject`, `.worktrees/test-perf`).
- The claim "Three files remain modified by another session" is stale —
  the working tree is clean as of 2026-09-23.

**Gotchas.**
- `git commit -o` for TASKS.md; `git add -p` + bare commit when co-editing
- Agents never run `chezmoi apply`
- `ollama ps` before benchmarking
- `tests/tasks_doc` guards TASKS.md section boundaries
- `chezmoi add` on a `.tmpl` can overwrite `{{ }}` with literals
- Permission configs load at session start and do not reload
- `git -C` bypasses subcommand-level permission rules
- The `autonomous` agent allows `git push` — sub-agents must not push
- `git worktree add` requires `ask` permission (not in any allow list)

## Picking this back up

Say any of these and the thread resumes where it stopped:

| Say this | Resumes |
|---|---|
| **"layout"** / **"standardization"** | `docs/LAYOUT.md` plan — next is the second-machine inventory, then its migration |
| **"topical"** or **"A9"** | The next build step: the manager-aware generator reading `managers.yaml` |
| **"the template work"** | Same as A9 — that is what it refers to now |
| **"voice typing"** / **"openwhispr"** | The voice topics; architecture is settled, `.deb` via `ansible.builtin.apt` |
| **"claude-code topic"** | Extending it to Debian via the signed apt repo |
| **"the sunset plan"** / **"A10"** | Retiring the six `~/bin` names, blocked on the dispatcher working |
| **"ansible user"** | The privileged-update service, scope the sudoers grant first |
| **"llocallabs"** | The anchor repo and strategy/policy agent — the collection consolidating the AI work |
| **"sandboxing"** | The two-phase agent-sandboxing research project |
| **"session management"** / **"handoff protocol"** | The research feeding the TASKS.md process design; advisor review of handoffs is part of it |
| **"rag"** / **"knowledge graphs"** | Preprocessed agent-context research |
| **"gita"** | G0 recorded the approved plan in PRD and § Gita and machine-file backup; next are G1, BK1 and the Linux inventory. Original handoff: `.worktrees/gita-plan/HANDOFF.md` on `agent/gita-plan` |
| **"metamorphic"** | The metamorphic-testing research for the test suites |
| **"pkgup"** | The Debian package-updater study, blocked on become privileges |
| **"r&d factory"** | The llocallabs exploratory pipeline — scratchpad experiments promoted by test suites, not vibes |
| **"multiagent"** / **"coordination"** / **"worktrees"** | § Now #1 — bootstrap the multi-agent coordination layer (worktree-per-agent, frozen leases, `--no-ff` per item); handoff at § Where things stand — 2026-09-22 |

The design decisions behind all of it are in `dotfiles/docs/ROADMAP-topic-cli.md`
§ Amendment — read that before writing any `topical` code, since several of them
reversed earlier positions on purpose.

## Now

The handful actually next. Keep this short — if everything is Now,
nothing is.

- **Evaluate interchangeable components for agent work.**
  [handoff ready, unclaimed; initial comparison complete, container setup
  assessment pending; 2026-09-24] The author approved the expanded brief. Task queues,
  orchestration, workspace creation, sandbox runtimes,
  and environment setup must be independently replaceable or removable.
  Include Backlog.md, workmux, herdr, and other relevant options; verify each
  tool's actual role instead of assuming all are queue managers. Compare
  Sandcastle (`mattpocock/sandcastle`), `anthropics/sandbox-runtime`, and
  maintained bubblewrap/Seatbelt consumers on macOS and Debian. Worktrunk and
  mise are the baseline, not mandatory dependencies; include a workspace
  alternative that does not require Git worktrees. Use local repositories,
  prior research and queued decisions alongside upstream docs, source and
  practitioner reports. This feeds the existing sandboxing and coordination
  items. Done when an evidenced report identifies replaceable boundaries,
  ownership and lifecycle contracts, ranks compatible combinations, records
  rejected options and platform gaps, and is reviewed with the author.

  Author clarification, 2026-09-24: non-root containers, including Sandcastle's
  approach, are first-class candidates when applying them requires very little
  configuration. Native execution is a workload capability, not a universal
  selection requirement. Compare host prerequisites, fresh-project setup,
  required files/settings/commands, reusable images or templates, credential
  wiring, and ongoing configuration maintenance. Preserve independent task,
  workspace and runtime choices. Next evidence needed: a low-configuration
  Sandcastle/container walkthrough against the native-wrapper baseline.

  Report: `.worktrees/wt-restart/.claude/RESEARCH-modular-agent-runtime.md`
  (local, uncommitted). The research agent mapped local prior work, verified
  queue/runtime interfaces, and ran macOS synthetic probes. Coordinator review
  reproduced SRT 0.0.77's false-success signal exit and mise 2026.9.12's failed
  host-network exception, alongside successful filesystem restrictions.
  Queue and workspace substitutions are interface-supported proposals;
  Debian and end-to-end swaps remain unrun. Decide next: serialized versus
  autonomous claims, worker commit authority, required network/IPC controls,
  and resume/retention ownership. The completed research unit is archived in
  `TASKS-RESOLVED.md`; implementation remains a separate decision.

  **Pickup:** `.worktrees/wt-restart/.claude/HANDOFF-modular-agent-runtime.md`
  on `review/topic-restart-stale`. The initial research and coordinator review
  are complete; no research agent remains running. The author clarified that
  low-configuration non-root containers are primary options. Next: compare
  Sandcastle's shipped container setup, workmux's container workflow and a
  native wrapper. The handoff and sibling report are local, uncommitted files.
  They retain the latest requirements and evidence where this queue's older
  research text differs.

- **Review the automatic restart topics on `feat/topic-restart-stale`.**
  [PR #5 open; resolving with the author in-session] User approved automatic restarts for stale services
  and GUI apps, plus topic-owned installation of the 1Password GUI. Review the
  shared role and both callers, reproduce any defects with tests, and prepare
  the change for human review under the deployed-file merge gate. Done when
  focused tests and topic validation pass, with deployment limits and remaining
  failures recorded. Worktree: `.worktrees/wt-restart` inside the main chezmoi
  source; no live restart or cask adoption during review.
  Review completed 2026-09-23 at `79f6f0f`: quit and reopen target the same
  bundle, and process-probe errors no longer count as a stopped app. Four
  regression cases failed before the fix; removing the exit-error guard killed
  both probe-error tests. Focused suite: 53 passed. Non-model repo suite:
  695 passed, 7 skipped, 7 deselected with all seven documented dependencies.
  Parent/topic syntax checks, 1Password metadata and `skillet validate .` pass.
  Scoped ansible-lint: 44 findings versus 42 on main (three path-role imports
  added, one lowercase task name removed). Debian live restarts, actual cask
  adoption and GUI Automation permission remain unverified. Per-GPU Ollama
  units remain outside the check. 1Password installs through brew but updates
  through its own updater; a disabled self-updater still needs an update path.
  Published [PR #5](https://github.com/bengineerdavis/dotfiles/pull/5) from
  `review/topic-restart-stale`, based on `origin/main`, with only the four
  restart commits. The author requested that it be resolved in-session after
  creation. The remote-base non-model suite is 690 passed, 1 failed, 7 skipped,
  7 deselected: the failure is the unchanged `git filter-repo` permissions
  expectation, already corrected by local-main commit `1e7899b`. No CI checks
  are configured on this PR. Complete the repo's author design check before
  merging; deployment is still separate.
  Worktree relocation complete [agent: OpenCode restart-review]: Git registers
  the new path at the same HEAD. Both existing local files had identical
  content hashes before and immediately after the move; the handoff paths
  were then updated. `git check-ignore` confirms the Git exclusion, and
  `chezmoi managed` lists 1,015 entries with none under `.worktrees/`.
  Split 2026-09-24 at the author's direction, because PR #5 bundled two
  topics under one title: the role plus its first caller, ollama, is branch
  `restart_stale_role_ollama` (worktree of the same name); the 1Password
  desktop app is `onepassword_desktop_app`, stacked on it. PR #5 is closed
  with pointers. The author's design review continues on the role PR from
  the PEP 8 question; see `.worktrees/wt-restart/.claude/HANDOFF-restart-review.md`.

- **Build a machine-assisted merge-gate checker — turn the diff-derived
  design in `AGENTS.md` § Merge gates (2026-09-22, fusion council) into a
  real, runnable tool instead of prose a human or agent applies by
  judgment.** [handoff, unclaimed — written 2026-09-22 for a fresh session
  to pick up cold; no prior conversation context needed to execute this]

  **Where things stand today, verified by direct inspection, not memory:**
  nothing computes this automatically. `.pre-commit-config.yaml` has
  exactly three hooks (shellcheck, bats-on-staged-scripts,
  commit-proportionality) and none of them know about diff buckets. The
  gate design exists only as prose in `AGENTS.md`. Two scripts already
  establish the house pattern to follow: `scripts/run-bats.sh` computes
  `git diff --cached --name-only --diff-filter=ACM` and acts only on what
  changed; `scripts/check_commit_proportionality.py` is a small,
  stdlib-only Python script wired into prek as a `local` hook, exiting
  nonzero on failure. Model the new script on both — this is
  configuration-and-scripting for this repo's own governance, not a
  bespoke external tool, so it belongs here per the AGENTS.md build ladder,
  same as those two.

  **(a) The classifier — mostly solved already, verified 2026-09-22.**
  Compute the diff (`git diff --name-only <merge-base>..HEAD` or against
  `--cached` depending on when it's invoked — decide which per (d) below)
  and sort every changed path into exactly one of three buckets:
  - **deployed-tree**: **fully mechanical, zero judgment call needed.**
    `chezmoi managed --path-style=source-relative` prints every
    `.chezmoiignore`-aware deployed source path (verified: it correctly
    excludes `AGENTS.md` and includes `bin/executable_policy`,
    `dotfiles/policy/*.yaml`). A changed path is deployed-tree if and only
    if it appears in that list. No enumeration to maintain by hand.
  - **policy**: not yet enumerated anywhere — this is the one real gap.
    Strong candidates, found by inspection: `bin/executable_policy`,
    `dotfiles/policy/**` (currently `ethics.yaml`, `personal.yaml`), and
    `.claude/settings.json` (confirmed repo-native, **not**
    chezmoi-managed — it lands in this bucket for being policy, not for
    being deployed, a different reason than the bucket above). Confirm
    this list is complete before shipping v1; it's a short, low-risk
    enumeration task, not a deep research question.
  - **egress**: genuinely unsolved and likely stays a judgment call — it's
    about what a change *enables at runtime* (a new network call, a new
    `curl`/`llm`/`ollama` invocation site), not a file-path pattern a diff
    can mechanically reveal. Don't force a mechanical answer here; a
    self-reported flag the agent sets, checked against nothing, is more
    honest than a false sense of automation.
  - **docs**: everything else that's markdown/comments/non-executable
    metadata — this bucket needs its own small, editable pattern list
    (e.g. `*.md`, `docs/**`) since "non-executable metadata" is currently
    only prose too.
  - Anything not caught by the three special buckets falls through to
    **"everything else"** — the existing full gate, unchanged.

  **(b) The check runner.** Given a bucket, either just *report* which
  gates apply (advisory) or actually *run* them and report pass/fail
  (enforcing) — see (c). Machine-readable output matters here specifically
  because an agent, not just a human, consumes it: exit code +
  `file:line`-shaped findings + one JSON artifact, same shape already
  queued in the shift-left study's "machine-shaped gate outputs" task
  (§ Now, "Machine-shaped gate outputs, and a skip census instead of
  coverage %" — cross-reference it, don't re-derive the format).
  If that task's `pytest-json-report` wiring lands first, this script
  should *consume* that JSON rather than re-parsing pytest's text output.

  **(c) Enforce or advise — an open sub-decision, not mine to make
  silently.** Recommendation: **start advisory-only.** Three independent
  reasons converged on this same session: the two-track trust model
  (`AGENTS.md`, LEDGER item) says a new deterministic mechanism earns
  trust through a seen-to-fail entry gate plus a streak, not by starting
  maximal; the author's own stated principle is "start with least
  privilege... once we can repeat a defined success condition, then we
  improve" — this script hasn't repeated anything yet; and the exact same
  gate-vs-report question is already open and deliberately unresolved for
  `ty` (§ Now, "Install `ty` and typecheck") — treat both consistently
  rather than deciding this one differently by accident. Tighten to
  enforcing only after it's been run for real for a while and shown
  correct.

  **(d) Wiring point — deliberately NOT a blocking git hook.** This
  session's own pytest-plugin research found the concrete failure mode: a
  200s pre-push hook gets bypassed by habit within a week, and
  `--no-verify` silently kills whatever else shares that stage — "a gate
  you must bypass to work is a gate you've lost." Self-merging is a
  deliberate act here (there's no server-side CI to enforce anything
  regardless), so the natural integration point is a script the agent (or
  human) *chooses* to run as part of its own "am I allowed to self-merge"
  reasoning per § Merge gates — not an automatic hook that blocks
  `git merge` itself. Once the LEDGER (§ Planned, "Build the LEDGER for the
  trust ladder" — not yet built) exists, this
  script is the natural thing that *writes* a ledger line — producer and
  consumer, designed together rather than bolted on later.

  **Done when:** the classifier correctly sorts a deliberately-constructed
  three-file diff (one docs, one policy, one code) into the right buckets,
  verified by direct inspection not assertion; the deployed-tree bucket is
  proven against a real `chezmoi managed` diff, not a hand-written list;
  the policy-path list is confirmed complete or corrected; the
  enforce/advise call is made explicit in the script's own help text, not
  left implicit; and running it against a real recent commit in this repo
  produces output an agent could act on without a human translating it.
  [unclaimed]

- **Repo-manager research: find or compose the repository-fleet manager, then
  decide Path A (Ansible now + upstream contributions until the tool absorbs
  the work) vs Path B (our own tool in a new repo).** The approved plan is
  written in full at `dotfiles/docs/research/repo-manager/PLAN.md` on branch
  `agent/repo-manager` (worktree `.worktrees/repo-manager`, based on main at
  `1e5d099`) — read it before starting. `HANDOFF.md` in the same directory is
  the session entry point and states the orchestrator authority. Supersedes
  the tool-choice half of G1 below; G1's comparison report is an input (a
  durable copy lives in the same directory). Council: 4 critics + a recruiter
  persona-scout, Round 0 before any sonar spend, $5 critic cap plus a separate
  $5 recruiter cap. Done when: REQUIREMENTS.md R1–R11 is finalized after
  Round 0; the sonar deep-research run is saved and source-verified into
  SOURCES.md; the combination ledger and Path A/B cost sketch exist; the
  author records the decision with dissent notes; TASKS.md/ROADMAP.md are
  updated; and Path B queues a new-repo bootstrap outside this repo.
  [agent: repo-manager / OpenCode — orchestrator session] [blocked: OpenRouter key for sonar + hosted council]

- **G1 — find a maintainable existing repository manager before selecting
  the Gita/Ansible path.** After G0, alongside BK1 and the existing
  second-machine inventory, compare established multi-repository tools and
  Ansible modules, roles and collections against the approved workflow.
  Evaluate human-facing workflow and interface simplicity, current and
  usable documentation, and fit to the handoff's machine selection, GitHub
  discovery, remote matching, fetch-safe sync, per-repository verdicts,
  non-aborting report, and freshness requirements. Include the preliminary
  Gita/ghorg/Ansible research in
  `.worktrees/gita-plan_sub_g1/dotfiles/docs/GITA-RESEARCH.md`, but widen
  its candidate set before recommending. Follow
  `dotfiles/docs/TOPIC-RECIPES.md`'s docs-and-Galaxy-first rule. If no
  existing tool meets the need, specify the smallest Ansible-module/role
  composition that could, what it still cannot do, and any contract or
  ownership decisions needed; do not design a bespoke engine or implement
  it here. Done when a sourced comparison ranks the existing options,
  records rejections, recommends a path that minimizes customer-maintained
  logic, and the author records the choice. The result hands the discovery
  and sync mechanisms to G2/G3/G4/G7. The expanded report is prepared at
  `.worktrees/gita-plan_sub_g1/dotfiles/docs/GITA-RESEARCH.md`. The author
  accepted task-level Ansible orchestration as the fallback on 2026-09-24,
  and asked for the complete workflow and candidate links before choosing
  the final tool split. No tool has been adopted yet. [agent: gita-plan / OpenCode]

- **BK1 — decide the backup host, installation and recovery-key design.**
  After G0, alongside G1 and the second-machine inventory, research an
  append-only borg host over SSH, borg/borgmatic installation on both OSes,
  and the support grade of available Galaxy roles. Borg 1.4.x with
  borgmatic is already chosen: pin 1.4.x, not borg 2 beta. The handoff's
  upstream check on 2026-09-23 found stable borg 1.4.5, released 2026-07-18,
  and borg 2 beta's warning against production backup repositories. A
  commented `pipx:borgbackup` entry and stale inactive borg shim do not
  establish an installation owner; the installation mechanism is this item.
  Carry the borg FAQ rules checked that day: one repository per machine
  per destination; redundancy is a second independent repository with its
  own `borg create`, never copying/syncing a live repository or putting it
  in a cloud-sync folder. Using a repository and its copy risks data loss
  and AES-counter reuse. After machine loss, restore from the old repo,
  then start a new one for future backups. The host copy is append-only;
  occasional prune/compact uses a separate key with delete rights.
  Keep an independent `borg key export` recovery copy and passphrases in
  the secrets manager: Bitwarden for personal machines, 1Password for work.
  Scheduled runtime passphrases come from the OS keychain: macOS Keychain
  or GNOME keyring via `secret-tool` on the home Linux target, not its
  unavailable `systemd-creds`. Borgmatic supplies config-driven repositories,
  retention/checks and `config bootstrap` recovery. The handoff records
  once-per-run `encryption_passcommand` in 1.9.9+, external credentials
  including 1Password CLI/systemd credentials in 1.9.10+, and no built-in
  Bitwarden hook; a passcommand works while that vault is unlocked.
  Set owner = the backup topic and choose bounded retention that keeps the
  newest archive and never prunes it, before any archive exists. Live
  machine-file retention remains until the machine is decommissioned.
  Decide key organisation in Bitwarden and check whether the work org
  permits a 1Password service account. The work Mac uses work 1Password
  only, with no borg; the both-OS installation research does not override
  that rule. Done when the design, evidence and author's decisions are
  recorded. G2 receives the ownership/retention contract; BK2–BK4 receive
  the chosen host, install and credential design.
  Research report prepared at
  `.worktrees/gita-plan_sub_bk1/dotfiles/docs/BACKUP-RESEARCH.md`; no target
  install, account or backup was exercised. Awaiting author decisions on the
  remote host, retention/cadence, recovery-key access and whether a personal
  macOS install path is needed; work 1Password automation remains subject to
  work-owner approval. Spending ceiling: recommend on merits; no purchase
  authorized. [agent: gita-plan / OpenCode]

- **Bootstrap the multi-agent coordination layer — worktrees, frozen leases,
  risk-tiered merge gates — then extract it to the copier template.** [#1,
  reordered ahead of the governance consolidation by the author 2026-09-20]
  Design settled this session with the author and a three-model council.
  Structure: one worktree per agent session (its own index — the actual fix
  for the `b3ad740`/`5692a86` mixed commits), one branch per task with
  subtasks as *commits* rather than sub-branches, `.git` read-only inside
  worktrees (Codex forces this; worktrees share `.git`, so a stray `gc` or a
  `.git/hooks` write hits every agent), `rerere` on globally, and a
  protected-ref deny so nothing irreversible lands unreviewed. Leases stack
  rather than compete: the resolver *authors* an expansion from `topic.yml`
  declarations, which is then **frozen** to a literal path list plus the
  metadata commit hash, resolver version and a TTL — enforcement reads the
  frozen artifact and never calls the resolver, which removes the TOCTOU hole
  where a lease silently widens when someone else's merge lands. Bounds:
  computation may only narrow (`effective = computed ∩ reviewed envelope ∩
  policy`); dependency edges grant **read**, not write (transitive closure is
  the canonical over-broadness bug); a commit may not widen the lease it was
  made under; and a literal deny-list — policy paths, egress paths, secrets,
  the deployed tree, resolver code, the lease store — outranks everything and
  *is* the mechanical definition of the always-human-review tier. Conflict
  detection is mechanical first (trial-merge plus duplicate `provides`, unmet
  `requires` and cycles as hard errors on the **merged** tree, which no
  per-branch gate can see), semantic later. **Measure merged-items-per-hour at
  2, 3 and 5 agents before building anything for 10** — throughput in agent
  count is plausibly non-monotonic, and if the curve flattens at 4 then most
  of the machinery is solving a chosen problem rather than a real one. Done
  when: worktree-per-agent is in use with `.git` read-only and `rerere` on; a
  push-time path gate rejects out-of-lease paths and **has been seen to fail**
  against a deliberately out-of-scope commit; the resolver rejects a
  duplicate-`provides` merged tree; provenance trailers record
  session/agent/model per commit; and the measured throughput curve is
  recorded. [me]

  Sub-items, settled with the author and a three-model council 2026-09-20:

  - **(a) Swarm shape inside one worktree: many readers, one writer.** A
    worktree is one index plus one mutable filesystem, so N writers in it is
    shared-memory concurrency with no memory model. The first thing lost is not
    commit correctness but the ability of any worker to *verify its own
    change* — the suite runs against a tree someone else is mutating, so green
    and red are both unattributable. That is the ledger's Class B (corrupted
    evidence) arriving structurally rather than by misconduct. So: fan out
    read-only subagents freely inside one worktree (search, analysis, review,
    "does this claim hold across the 40 topic files"), and give every *writer*
    its own worktree. Patch-producing writers are a trap — a diff is good
    transport and a bad execution environment; the moment a worker must test,
    it needs a tree, and a tree wants a branch. Patches are right only for a
    read-only subagent proposing an edit it never ran. Done when the roles are
    written down, the read/write split is enforced, and a deliberately
    concurrent write is shown to be rejected rather than merged.
  - **(b) Deterministic index, via git's own primitives.** Commit
    construction becomes a pure function of (base tree, file contents) with
    `GIT_INDEX_FILE` pointing at a private index plus plumbing —
    `hash-object -w`, `update-index`, `write-tree`, `commit-tree`,
    `update-ref` — needing no working tree and no shared lock. Claims belong
    in refs, not prose: `git update-ref refs/claims/<item> <sha> ""` fails if
    the ref already exists, which is an atomic compare-and-swap and therefore
    a real mutex, unlike a § Claimed line two sessions can both believe they
    won. Two traps: `index.lock` failures look transient so agents retry, and
    a retried `git add` after a partially applied operation stages a
    *different* set — the retry is the bug, not the lock; and hook frameworks
    that stash unstaged changes can eat or resurrect a concurrent writer's
    work in the same tree (benign here, since this repo's hooks only check,
    but not in ai-prompt-library where formatters run).
  - **(c) The real parallel ceiling is the machine, not git.** A worktree
    virtualizes the source, not the host. Anything touching `$HOME` is
    unparallelizable regardless of git — and in a dotfiles repo that is most
    of it: the deployed tree, `~/bin`, `~/.binned/config.toml`, apt/brew
    locks, mise, ollama's global model memory. True parallel width is the
    number of in-flight tasks needing no global resource; model each global as
    a semaphore. Estimated real ceiling here is 2–3 writers — **flagged by the
    shift-left study's fusion council as circular: estimated from a $HOME-touch
    audit that doesn't exist yet, and hermetic HOME may dissolve the ceiling
    rather than just unblock xdist.** Prerequisite for any parallelism: sandbox
    the tests that touch `$HOME` (`HOME=$(mktemp -d)`, chezmoi
    `--source`/`--destination`, `--dry-run`). **Implementation pattern
    researched 2026-09-22:** an autouse conftest fixture pointing
    `HOME`/`XDG_*` at `tmp_path` via `monkeypatch.setenv` (auto-reverts, no
    manual teardown); the trap is modules that cache `os.path.expanduser("~")`
    at import time — those must be invoked as subprocesses with an explicit
    `env=` dict built from `tmp_path`, monkeypatching `os.environ` alone does
    not reach them. macOS-specific escapes to name and exclude, not silently
    tolerate: the system keychain and `dscl` ignore `$HOME`, and a subprocess
    that re-execs a login shell (`zsh -l`) re-sources zprofile and escapes the
    sandbox — a live Class-B channel (test passes while touching real state).
    chezmoi's own upstream suite isolates at the layer that resolves the path
    (in-process VFS + `testscript` txtar synthetic homes) rather than via env
    vars — same principle, different mechanism, worth the comparison before
    building. ~~Until this holds, `pytest-xdist` is off the table.~~ **Corrected
    2026-09-23:** the `$HOME` sandboxing is already done — policy, quarantine,
    binned and clipped all redirect via fixtures — and `pytest-xdist` is now
    measured working here (170s → 47s, `-n auto --dist worksteal`, same two
    pre-existing failures). The "2–3 writers" ceiling is about agents sharing
    `$HOME` resources and does not apply to tests, which are read-only apart
    from tmp dirs. The remaining shared resource is the uv cache lock, not
    `$HOME`.
  - **(d) The subtask dependency graph is deferred, with the condition for
    revisiting it stated.** Graphs work where they are *derived and enforced*
    and fail where they are *authored and trusted*: Bazel/Buck/Nix are
    trustworthy because a sandboxed action physically cannot read an
    undeclared input, and an agent that reads the whole repo violates
    hermeticity by construction — so a hand-drawn agent DAG is advisory only,
    never proof of independence. Snakemake and Nextflow derive their DAGs from
    declared file patterns; Airflow bolted on dynamic task mapping in 2.3,
    Prefect 2 dropped static DAGs, and Temporal's position is that the
    workflow *is* code and the graph is discovered by executing it. Closest
    transferable prior art is Git's own "What's cooking" — a human-curated
    queue of topic branches that scales with no scheduler at all, i.e. this
    file. Conditions for it to beat a lock and a list: sustained parallel
    width ≥ 2 *on the critical path* (decision-led work is a chain, and § How
    work runs here pushes it further that way by leading with deciding
    items); node duration ≫ integration cost; cheap per-node verification;
    nodes that genuinely partition files; and a human who is expensive to
    consult, which one developer at this machine is not. Note also that
    building a scheduler here would be a **build, not configuration** — per
    the AGENTS.md ladder it belongs in ai-prompt-library or nowhere. Order:
    shrink suite runtime and conflict rate first. [blocked: instrument the
    four numbers in (f) first]
  - **(e) Commit granularity: keep the rule, add the prohibition, and let a
    merge carry both views.** "One reviewable decision" is scale-relative and
    therefore nearly unfalsifiable — a Debian systemd-timer choice is a
    decision and so is a variable name inside it, so nesting lets the rule
    justify any split. It also loses outright on large mechanical changes: a
    rename across 40 files plus a behavior change is *one* decision that must
    become three commits (add new, migrate callers, delete old) because the
    intermediate states must work — and that split criterion is mechanical,
    not semantic. The resolution: **bisect wants fine, revert wants coarse,
    and a `--no-ff` merge per work item gives both** — fine granularity
    inside, one `git revert -m 1` handle outside, and `git log --first-parent`
    as the clean history on demand. Require "every intermediate state works"
    of first-parent commits only; branch-internal commits need merely not be
    broken on purpose, which legitimizes the WIP checkpoint commits agents
    need anyway when they die of context exhaustion mid-task. Criteria become:
    revertible alone with a coherent result; passes the suite; the why fits in
    ~2 sentences (measured — 232-word median against a house 114); and **never
    mix mechanical and semantic change in one commit**, ordered mechanical
    first (Beck's "tidy first", Fowler's preparatory refactoring). That last
    rule is mechanically checkable and does more for blame, review and
    conflict rate than any theory of decisions. Whose decision is a commit
    when agents run in parallel: **the branch, not the subagent** — subagent
    boundaries are an artifact of how the work was parallelized, which is
    exactly what history should not preserve. Also adopt
    `.git-blame-ignore-revs` with `blame.ignoreRevsFile` so mechanical churn
    is skippable.
  - **(f) Instrument four numbers before building any of it.** Suite
    wall-clock, conflict rate, rebases per merged item, and author review
    minutes per item. Every question above resolves differently depending on
    them, and none are currently measured. Review is the likely bottleneck
    rather than generation: with one reviewer, agents past ~3 queue in front
    of the human and their branches rot — raising WIP without raising review
    throughput raises latency, and latency becomes staleness, rebases, and
    void test evidence. Cheapest controls, needing no code: an explicit WIP
    cap, and a max branch age (a branch older than a day has void test
    evidence — rebase or abandon).
  - **(g) Make the "seen to fail" evidence mechanical.** Commit trailers
    (`Mutation:`, `Failing-test:`) via `git interpret-trailers` are greppable
    and auditable; prose in a commit body is not. The highest-severity
    incident class in the trust ladder is currently detectable only by a human
    redoing the work. Related: the mutation state that proves a test must
    never be committed, so the evidence can only ever live beside the commit,
    not in it. [done `a92489b` 2026-09-22]
  - **(h) Lifecycle: spawn, fan-out, provision, collect, reap.** Every
    worktree and branch passes through one lifecycle, so a wedged session is
    recoverable by inspection rather than archaeology. Merging uses an
    ephemeral scratch worktree `.worktrees/<sid>_merge_<n>`, recreated per
    attempt from (base + input SHAs) — re-running `git merge` in a conflicted
    tree is not idempotent, rebuilding from SHAs is (the Zuul/bors/merge-queue
    pattern). Merges are serial with the suite after each — batching destroys
    attribution — ordered inert → behaviour → activating. A failed wave is
    bisected, not retried wholesale; green/green/red is a finding recorded
    against the fan-out, evidence the decomposition was wrong. Retries follow
    the table: infra 2–3 with full jitter under a retry budget;
    rebase-and-retest 1–2; deterministic never retried unchanged; LLM
    regeneration once carrying the failure evidence, then escalate.
    Classification is mechanical — re-run the identical artifact in a fresh
    scratch worktree: same failure is deterministic, different failure is a
    flake, quarantined rather than retried into green. A branch is never
    `git branch -D`'d until `merge-base --is-ancestor` proves the work
    landed; crash recovery is `git worktree remove --force` plus
    `git worktree prune`. Escalation reports to the orchestrator freely and
    to the human at the retry cap, with a deadman timeout.
  - **(i) Declaration merge policy: regenerate, never hand-merge.** Venvs
    never merge — only declarations do (pyproject.toml, uv.lock). A lockfile
    conflict is resolved by merging pyproject.toml and re-running `uv lock`,
    never by editing the lock; `.gitattributes` carries `uv.lock merge=binary`
    so git never attempts a textual merge of it. uv is pinned at the system
    layer (`bootstrap.sh`), not mise — the lockfile carries a format
    revision, and version skew churns it. pyproject.toml and uv.lock are
    registered as hot files in § Cross-session hazards.
    **Not true yet, 2026-09-23:** the uv that runs is mise's
    `uv = "latest"`, not the bootstrap pin — (p) U1 fixes it.
  - **(j) Three coupling channels, and one unconditional gate.** Coupling
    between parallel workers travels exactly three ways: writes, caught by
    path-intersection at fan-out; reads, structurally isolated by worktrees;
    semantics, caught only by the merged-state suite — the irreducible
    channel, and the reason merges are serial with the suite after each.
    Over all three sits one unconditional gate: no agent diff may touch the
    gating tests or the policy code, because a worker that can edit its own
    verifier can pass anything. That is a correctness requirement, not a
    trust one.
  - **(k) Capability manifest per subtask.** Every subtask declares a
    manifest — paths, refs, commands, egress, secrets, limits, runtime —
    because "read/write/both" is too coarse to enforce and too coarse to
    audit. Enforcement is three layers: declare (the manifest), sandbox (what
    the environment permits), gate (what the merge refuses). Manifests are
    logged via git notes, so the audit trail travels with the refs.
  - **(l) Contracts-first.** Interoperating pairs land their interface
    before fan-out. The interface is a decision item — cheap to land, and
    unblocking; fanning out before it exists charges every downstream branch
    a rebase each time it changes.
  - **(m) Verifier health first.** The suite's flake rate and mutation
    sensitivity are measured before the orchestrator builds on it. An
    orchestrator multiplies whatever the verifier is, and a verifier that
    passes without exercising what it claims turns the merged-state gate
    into Class B evidence at scale. Builds on (f)'s instrumentation and
    (g)'s mutation trailers.
    Exhibit, 2026-09-23: `tests/chezmoi/test_governance_not_deployed.py:55`
    runs `chezmoi managed` without `-S`, and chezmoi's source directory is
    fixed, so from a worktree the guard checks main's source — a broken
    ignore list in the worktree cannot turn it red. Found by reading the
    code; (p) P2a proves it with a mutation and fixes it.
  - **(n) Irreversible agent effects.** A change that reaches the deployed
    tree (`~/bin`, `~/dotfiles`) cannot be undone by `git revert` — the
    revert restores the source, not the machine. Scope is agent-concurrency
    only: what the coordination layer must guarantee about effects it cannot
    take back. Ansible plan-vs-apply drift is explicitly out.
  - **(o) Phase 2 experiments — the design seen to work, in sequence.**
    Choose the order; each is evidence, not ceremony. **Happy path:** two
    disjoint sub-agents, simultaneous suites, prove the offline run works —
    then `uv cache clean` one package and confirm the offline run fails.
    **The guard seen to fail:** a path overlap refused at fan-out, then the
    check disabled to confirm it was the guard that caught it; extended with
    two sub-agents adding the same `topic_provides` from different files —
    path intersection empty, so the resolver must reject the merged tree.
    **Provisioner path:** `uv add`, merge back, re-lock; then two
    provisioners refused.
  - **(p) Make the repo a Python project: one root `pyproject.toml`, one
    committed `uv.lock`, the test environment rebuilt offline.** [agent:
    pyproject session, `.worktrees/pyproject` on `agent/pyproject`] Author
    request 2026-09-23: follow current PyPA/PEP practice, research first,
    critique by a council, propose any structural change before making it.
    The research ran before this line existed; it is recorded late rather
    than backdated. Decided with the author 2026-09-23: a root project that
    is never built or installed (no `[build-system]`, `[tool.uv] package =
    false`, PEP 735 dependency groups for the test deps), root-only
    `.chezmoiignore` entries, and a governance guard that works from
    worktrees; the `.chezmoiroot` move is a separate `ROADMAP.md` decision;
    uv's version authority is the bootstrap pin (U1). Rule-outs: nothing new
    in `$HOME`, deployed scripts run unchanged, frozen offline runs work,
    `tools/skill-trust` keeps its own lock. Rejected: packaging the repo
    (scripts must stay standalone), a uv workspace with skill-trust, a
    subdirectory `pyproject.toml` (tools look at the root), `pylock.toml` or
    requirements files (no `--frozen`, no groups), keeping the `--with` flags
    (nothing locked). Order: council C1–C5; then PR 1 — P1 docs
    (`docs/PYTHON.md`, `REFERENCES.md`, `LANGUAGES.md`), P2 baseline counts
    per test directory, P2a guard uses `chezmoi -S`, P2b one commit adding
    `pyproject.toml`, `uv.lock`, ignore entries, guard lists and
    `.gitattributes`; then PR 2 after `test-perf-xdist` merges — P3
    `pytest.ini` into `[tool.pytest]`, P4 `AGENTS.md` § Commands, changelog,
    hot-file registration. P1 shares `docs/PYTHON.md` with `test-perf-xdist`
    (its dependency paragraph) — rebase whichever lands second. Open for the
    author at P2b: `requires-python` `>=3.14` or `>=3.11`; ruff/ty pinned in
    lock groups or in mise. Done when `UV_OFFLINE=1 uv run --frozen pytest`
    reproduces the baseline recorded first — the same passes, and only the
    known failures, each named (author, 2026-09-23) — so (o) can use it as
    its consumer path.
    **Council verdicts 2026-09-23** (C1–C4 returned; C5 skipped, Exa key
    absent). Author decisions: `requires-python = ">=3.14"`; ruff/ty in
    lockfile dependency groups (lint/format libs in the lock); committed
    `uv.lock` yes; split P2b into two commits (deploy-hygiene vs project
    adoption); U1 step 1 before `uv lock` (lock format is uv-version-
    sensitive). Corrections: `test-perf-xdist` is merged (`118aaa6`) — PR 2
    no longer waits and the worktree needs rebasing; `tests/` has 44
    `test_*.py` not 40; `slow` marker does not exist; `GOVERNANCE_DIRS =
    []` makes one guard test dead code; `required-version` ships post-U1
    not in PR 1; P4 (AGENTS.md commands) moves to PR 1 tail. Full
    critiques in `.worktrees/pyproject/.council/`.
    **Landed 2026-09-25:** PR #17 (guard fix + leak cleanup), #18/#19
    (project: `pyproject.toml` + `uv.lock` + docs + commands) and #22 (P3:
    pytest config into `pyproject.toml`, `pytest.ini` deleted). P1–P4 done.
    Frozen run verified from main: `UV_OFFLINE=1 uv run --frozen pytest`
    resolves from the lockfile — the done-condition is met. Remaining: U1
    (author on both machines), C5 (blocked on the Exa key), strict-markers
    and `importlib` import mode (separate decisions, not started).
    - **(p) C1 — architect advisor.** [agent: fresh-context read-only
      subagent] Critiques the (p) brief on layering (chezmoi/Ansible/zsh),
      the `PRD.md` provision-versus-logic rule, `.chezmoiroot` versus the
      ignore list, and fit with this coordination work and Refactor B. Done
      when it returns agree/disagree per decision, risks missed and what
      would change its mind, then a round-2 reply to the other critiques.
    - **(p) C2 — pragmatist advisor.** [agent: fresh-context read-only
      subagent] Critiques daily workflow, the clash with `test-perf-xdist`,
      order of work and what breaks first. Done as C1.
    - **(p) C3 — skeptic advisor.** [agent: fresh-context read-only
      subagent] Attacks every claim in the brief with file:line evidence,
      hunts for tests that pass without checking anything, and asks whether
      a lockfile is needed at all. Done as C1.
    - **(p) C4 — second model, another vendor.** [agent: `ask-research
      --no-online --model openrouter/google/gemini-3.1-pro-preview`] Same
      brief, both rounds, zero-data-retention routing, web search off so
      nothing repo-derived reaches a search provider. The brief carries
      repo-relative paths only — no home paths, employer strings or usage
      numbers. The content is not work-tagged, so the author's go-ahead is
      the permission; record `policy explain
      boundaries.llm_processing.remote_model_allowed` with the run. Done as
      C1, with cost recorded; C4 and C5 together stay under $5 (author,
      2026-09-23).
    - **(p) C5 — practitioner survey.** [agent: `ask-research`, web search
      on] Public question only: how do public chezmoi repositories host
      Python tooling? Skipped, and the skip recorded, if the Exa key is not
      set. Shares C4's $5 cap. Done when a sourced answer or a recorded skip
      exists.
    - **(p) U1 — make the uv pin real.** [me — both machines] `bootstrap.sh`
      pins uv 0.12.17, but `apps/mise/files/config.toml:82` has
      `uv = "latest"` right under a comment (lines 77–81, `2f13ed2`) saying
      uv is not mise-managed; merge `57dd1dd` (2026-08-06) put the line
      back. On the Linux box, 2026-09-23, the `uv` on PATH is mise's
      (0.12.17) and no system uv exists, so bootstrap's `command -v uv`
      check passes and its pin never installs. Mac not checked. Order, so
      no machine is left without uv: (1) install system uv 0.12.17 on each
      machine, as `bootstrap.sh` does; (2) then claim `config.toml` in
      § Claimed and remove the mise line, fixing the comment or the line —
      the file is symlinked from `~/.config/mise/config.toml`, so the edit
      is live at once; (3) last, add `required-version = "==0.12.17"` to
      `[tool.uv]` — earlier, a mise uv floating to 0.13 fails every uv
      command here. The gita-plan session found the same mismatch (its G0
      side finding 1); this is the one task for it. Done when `command -v
      uv` is the system install on both machines, mise declares no uv, and
      `required-version` enforces the pin.
      **2026-09-28:** done on Linux — PR #25 merged, then `chezmoi init` +
      `mise reshim`; fresh shells resolve `uv` to system 0.12.17 and the
      `required-version` pin holds. The Mac's uv state is still unverified;
      it needs the same install-and-reshim. The stale mise uv installs
      (0.12.5, 0.12.18) remain orphaned on disk — `mise gc` could clear
      them, left as-is for now.

- **Consolidate the governance docs — PRD as the constitution, spec as the
  derived statutes, conventions as the how-to.** [#2, was #1 until the author
  reordered the multiagent work ahead of it 2026-09-20] Decided with the author
  2026-09-16: PRD states each requirement once; spec derives its testable
  SHALL/BDD form and cites the principle back; AGENTS-referenced convention
  docs explain how to comply. The four docs are currently peers with no stated
  precedence, and PRD has smuggled constraints (the provision-vs-logic rule,
  the verification governor) that belong in spec — the drift behind the
  changelog "discipline gap" (d1f10ff). Items, in order: (1) derivation-graph
  inventory — map every spec.md behavior to its PRD.md principle and back,
  marking orphans and unstatuted principles; (2) write the precedence rule into
  the docs; (3) prune the drift — move smuggled statutes into spec with
  citations; (4) retire the stale root docs/ tree (edit dotfiles/docs/ only);
  (5) review TASKS.md § Now/Planned against the consolidated requirements.
  Done when every spec behavior cites a PRD principle, PRD holds no testable
  statutes, one maintained copy of each doc exists, and the open task list has
  been re-reviewed. [me]

- **Switch the hook runner to prek and retire the pipx pre-commit.** Verified
  2026-09-20: prek's unstaged-change mechanism is patch-to-cache, not
  `git stash`. `crates/prek/src/cli/run/keeper.rs` captures unstaged work with
  `git write-tree` + `git diff-index --binary`, writes it to
  `~/.cache/prek/.../patches/{millis}-{pid}.patch` in a `0700` directory,
  cleans the tree, runs hooks, then `git apply`s it back on drop — reverting
  the hook's own changes first if they conflict, and restoring from a ctrl-C
  cleanup handler. Neither `git.rs` nor `keeper.rs` contains `git stash`, so
  the switch does not put hook runs on the shared `refs/stash` that already
  holds two orphaned autostash entries — the one risk that gated this. prek
  also disables `core.fsmonitor` for its own git calls and handles
  `GIT_DIR`/`GIT_COMMON_DIR` worktree separation, which is useful precedent
  for the coordination work. **Correction 2026-09-22 (shift-left swarm,
  file read + `prek run --dry-run`): the "State today" below was already
  stale when written — both hook files say "File generated by prek" and
  prek is the active runner; pipx pre-commit 4.6.2 is installed but not
  wired.** Done when one runner is uninstalled and the other removed from
  the docs, and a run against a tree with unstaged edits prints prek's
  "Temporarily saving them to" line while `git stash list` stays unchanged —
  the mechanism was verified against `master`, not the installed 0.5.3, so
  that check is the confirmation. [me]

- **Input to the normative topic spec: lift the settled herdr decisions from
  `dotfiles/docs/TOPIC-RECIPES.md` and `dotfiles/apps/herdr/README.md`.**
  Queued 2026-09-19: the spec session should absorb the install-mechanism
  chooser, the catalogue pattern (with its skip-vs-raise doctrine), the
  service-ownership rules and the test-first swarm recipe from those two docs
  rather than re-deriving them; `dotfiles/docs/JUDGE-SELECTION.md` feeds the
  panel-of-judges measurement item. Done when the spec either expresses these
  or records a reasoned rejection. [me]

- **Write the normative spec for topics — a `spec.md` for the topic unit.
  More urgent than the design work below it.** Queued 2026-09-17 ahead of
  the downstream-IDE wiring so that work lands against a settled constraint
  layer rather than after it. House spec form (SHALL/MUST with BDD
  scenarios, skillet-validatable, carrying its `skillet-version` comment),
  a sibling to the root `spec.md`: what a topic is and must remain — the
  lifecycle contract, the CRUD ownership invariant, `topic.yml` as the
  schema of record, template conformance, shared-dep teardown rules, the
  guard doctrine. `TOPICS.md` then reduces to plain explanation that links
  to the spec for binding wording — two normative statements of one rule
  drift; an explanation plus a link does not. **Input to the spec, by the
  author 2026-09-17:** the vscode↔cursor downstream-IDE design below is a
  deliberate probe of how upstream/downstream relationships between topics
  should be declared and governed — its settled outcome normalizes "topics
  as a format" and must be expressible in the spec's terms. Done when the
  spec exists, `skillet validate` passes on it, `TOPICS.md` cites it
  instead of restating its SHALLs, and the author's adopt call is
  recorded. **In progress elsewhere** (author, 2026-09-17) — do not start
  from another session. [me]
- **Design the cadence by which topics pull in and refresh official
  upstream references, so topics track their tools proactively.** Queued
  2026-09-17 by the author: topics bind to external tools whose docs,
  changelogs and release feeds move, and today the repo learns of upstream
  change only reactively — the skillet pin needed a changelog read before
  moving, `docs/REFERENCES.md` records "when last checked" by hand, and
  cursor/vscode extension availability is being verified per editor only
  because something broke. The design must settle: what each topic declares
  about its upstream (a source list in the topic — docs URL, changelog or
  release feed, the `REFERENCES.md` row it feeds); what cadence means here
  (per-topic intervals, one repo-level sweep tied to `--tags upgrade`, or a
  machine timer — noting launchd on macOS and the systemd *user* timer rule
  on Debian); where fetched deltas land so they become work (a queue line,
  a report, a drift subcommand in the topical CLI) rather than vanishing;
  and how it composes with the extension-manifest design above, whose
  per-extension availability verdicts are the first instance of this same
  problem. **The cadence fetcher is a build** — the AGENTS.md ladder
  applies: route it (ai-prompt-library, llocallabs, or the topical CLI
  work) before any code is written here; machine-side wiring such as a
  timer is the only part that provisions. Done when a written design
  answers those questions with the destination decided through the ladder,
  and the wiring lands as queued tasks. [me]
- **Spec the zsh tooling standard — author interview first, then a
  review-best-practices pass, then council critique.** Queued by the author
  2026-09-16, from the LANGUAGES.md zsh row: ~90 `.zsh` files are zsh
  lifecycle fragments, the extension marks how a file is used rather than a
  distinct language, and the bash standard already applies de facto — the
  pre-commit shellcheck hook matches `types: [shell]` and identify tags
  `.zsh` as `shell`. Interview first: fragment-vs-script semantics, which
  bash tools are trusted on zsh, tolerance for zsh-specific false positives
  (shellcheck does not support zsh — `typeset`, `${~spec}`, `=cmd` are known
  mismatch classes), whether `zsh -n` should gate commits, and where the spec
  lives (a `docs/LANGUAGES.md` row vs a new `docs/ZSH.md`). Then a research
  pass verifies the "zsh can use bash tools" claim rather than assumes it,
  with ranked options and rejections recorded. Then fresh-context subagents
  red-team the draft (the panel-of-judges question is itself unsettled; using
  the pattern here is the author's call). Done when a written recommendation
  exists with rejections recorded, the author's adopt/adapt/reject decision
  is recorded, and any wiring lands as queued tasks. [me]
- **Extract the incoming-changes review into a reusable agent capability,
  with a specification.** High priority, queued by the author 2026-09-15,
  from this session's review pattern: on `git fetch`, before any merge, the
  agent verifies the incoming claims against this machine (`chezmoi status`,
  `ollama list`, path existence), classifies findings as blocking /
  question / nit with file-and-line evidence, and recommends resolutions.
  Routing: with no blocking findings, pass the changes in (fast-forward
  merge); with any, hand the merge to a human via **meld** — `git
  mergetool` or merge-with-conflicts opened in meld — and report the
  finding list for them to resolve. The specification (SHALL/MUST + BDD
  scenarios, house spec style) must fix: the trigger point (post-fetch,
  pre-merge); the verification classes; the conflict taxonomy and what
  counts as blocking versus advisory; the human-handoff via meld and how a
  run resumes after the human resolves; idempotency on repeated runs; and
  the pass-through policy — which gates turn a question into a block.
  Destination per the AGENTS.md ladder (likely a skill/spec in
  ai-prompt-library or llocallabs); any machine-side wiring here is
  provisioning. Done when the spec is written and validated, and the
  capability runs end-to-end against both a deliberately conflicting merge
  (hands to meld) and a clean one (passes through).
- **Inventory the second machine's divergent trees for the layout
  migration.** Queued by the author 2026-09-15 (standardization interview):
  the migration plan must not guess what the other machine holds. On the
  next session there, inventory `~/code/projects/personal/` (at least
  `llocallabs-capture`), `~/code/try/` (copier-stamps, git-ai-plugin,
  openrouter-tools per the merged queue), and any other dir outside this
  Mac's layout; record each with its proposed type under the standard
  (work/personal/try/captures/templates/forks/archive). Done when the
  inventory is written into the migration section of the layout plan and
  every divergent path has a destination type. [agent: second-machine
  session]
- **Handle machine-specific directory exceptions and their state backup in
  the layout standard.** Deferred by the author 2026-09-15 from the
  standardization interview: some directories will exist on one machine
  only, yet their state should still be backed up to config. Design how the
  standard declares a per-machine exception without breaking sameness
  elsewhere, and how the exception trees' state plugs into the
  backup-design item in § Planned. Deferred deliberately so the interview
  can settle the shared-layout core first.
- **Research when LSP servers earn their keep with opencode — a deeper
  answer than the docs' best-practices page gives.** High priority, queued
  by the author 2026-09-15. The page (https://opencode.ai/docs/lsp/, fetched
  2026-09-15) says LSP is disabled by default, lists 30+ built-in servers
  that auto-start on matching extensions, and concludes that lint/typecheck
  CLIs documented in AGENTS.md or skills often beat language-server
  feedback. That is the hypothesis to test, not to accept. The research must
  settle: per-language payoff (pyright wants a project dep, several
  auto-install, `OPENCODE_DISABLE_LSP_DOWNLOAD` gates downloads); the real
  cost terms (memory, version skew, out-of-sync servers) weighed against
  agent-loop value; where `lsp` config should live per repo and per topic
  here; and which repos actually earn enablement. Route it as a
  review-best-practices pass — what exists, what practitioners do, ranked
  options with rejections recorded — and it feeds the llocallabs topic
  design. Done when a written recommendation says when LSP earns its keep
  here, per language, and the author has made the adopt/adapt/reject call.
  [me]
- **Configure opencode LSP profiles for Python and Bash projects — ty or
  pyrefly alongside ruff and the other servers that matter — if we are not
  doing that already.** Queued by the author 2026-09-15; the concrete
  follow-on to the research task directly above — that one settles WHEN
  LSP earns its keep with opencode, this one settles WHICH servers for
  Python/Bash and wires them. Verified 2026-09-15: we are not doing it
  already — neither `dot_config/opencode/opencode.jsonc.tmpl` nor the
  project `opencode.json` has an `lsp` section (rg finds none), so LSP is
  disabled-by-omission; ruff is mise-managed (`ruff = "latest"`) but wired
  to nothing per docs/REFERENCES.md; `ty` and `pyrefly` are both absent
  from the mise config (a § Later task queues installing `ty`); bash
  linting today is shellcheck in pre-commit. The docs
  (https://opencode.ai/docs/lsp/, fetched 2026-09-15) say `lsp: true`
  enables all 30+ built-ins and the object form configures per-server
  `command`/`extensions`/`disabled`/`env`/`initialization`; built-ins
  relevant here: pyright (.py, wants a project dep), bash (auto-installs
  bash-language-server), yaml-ls (auto-installs);
  `OPENCODE_DISABLE_LSP_DOWNLOAD=true` gates the auto-downloads. The work:
  decide ty vs pyrefly — pick one, not both (ty is pre-1.0 but the house
  toolchain names it; the queued install task owns the install, this owns
  the LSP wiring); decide where the profile lives — the chezmoi-managed
  global template (all projects, effective on apply + restart) versus
  per-repo `opencode.json`; and decide whether server downloads are
  permitted given bash-language-server and yaml-ls auto-install. Done when
  the chosen servers are configured in the chosen location, an opencode
  session on this repo shows Python and Bash server feedback, and the
  download policy is recorded. [me]
- **Create the first llocallabs.ai repository — the collection that will
  consolidate the author's AI tooling and agent projects.** The milestone
  (2026-09-14): AI research, testing and benchmarking move out of this
  repo — it carries the machine trunk and is overloaded with strategy work
  that wants isolation. The first repo anchors the collection: document set
  first (PRD what-for, spec, ROADMAP, TASKS, AGENTS — the separation this
  repo runs on), then it queues its own move-manifest work. Two questions
  settle at creation: scaffold by hand versus the general copier template
  queued in § Planned (llocallabs would be its first real consumer — that
  coupling may be the reason to build the template now), and where it lives
  (`~/code/personal/` beside ai-prompt-library and impromptu is
  the precedent — verified on this Mac 2026-09-15; the
  `~/code/projects/personal/` form in 984df10 was the author's other-machine
  path, incorrect here, and the author confirmed reverting it). This repo's recently-queued research (sandboxing, session
  management, metamorphic testing) and the benchmarking tooling
  (`bin/model-bench`, `bin/binned`, the eval harness) are candidates for
  the move manifest — nothing moves until that manifest lands. Done when
  the repo exists, carries the document set, passes `skillet validate`, and
  its TASKS.md queues the move-manifest and strategy-agent work. [me]
- **Stand up the llocallabs strategy/policy agent.** At least one separate
  agent that works on tooling and decisions about the author's personal AI
  strategy and policy — the role this repo was never meant to play (PRD:
  provisioning is the trunk; strategy is a branch). Its definition, context
  and tooling live in llocallabs, not here; the machine-side part —
  registering it in opencode/claude config, its permissions — is a follow-on
  task here once the definition exists. It consumes the research projects
  this repo queued (sandboxing, session-management handoff, metamorphic
  testing) as strategy inputs, and its policy decisions feed back through
  the over-arching-policy contract in ROADMAP.md. Done when the agent
  answers a real strategy question with a recommendation and rejected
  alternatives, running from its own repo rather than this one. [me]
- **Build the llocallabs R&D factory — an exploratory pipeline from
  scratchpad experiments to durable, reusable elements, in service of the
  long horizon: autonomous knowledge projects.** The author's recurring
  trouble, named 2026-09-14: classifying the different modes of research
  (ideation, brainstorming, stress-testing, fact-checking — not
  exhaustive), recruiting the right experts for each, and trying out
  agents, skills and workflows in a low-stakes environment where useful
  experiments become durable quickly and dead ones cost nothing. First
  evidence of the friction, same day: the author's Google AI research on
  Caliber lived only in a conversation until captured by hand to
  `~/code/personal/llocallabs-capture/` — and `~/code/try/` already
  holds the author's ad-hoc experiments (copier-stamps, git-ai-plugin,
  openrouter-tools), making it the embryonic scratchpad; research captures
  route to the capture store beside the personal projects until the
  factory's own pipeline exists. This task
  is stage one, **gated on the anchor repo existing** — the factory belongs
  to the collection, not here. Stage one classifies: inventory the author's
  actual research modes from what the queues already show (the
  council-pattern deep-research projects, the eval-gate doctrine, the
  `agentic-context-engineer` role), map each mode to the agents, skills and
  workflows it needs, and record which experts — human or model — belong to
  which mode. Stage two, queued by stage one's output, is the scratchpad:
  disposable environments where an experiment runs with a lightweight eval,
  and the promotion gate into a durable element (a skill, an agent, a
  workflow) is a passing test suite — never vibes. Done when stage one's
  classification exists, the author has corrected it, and the
  scratchpad/promotion stages are queued in llocallabs with their own
  gates. [me]
- **Research metamorphic testing for this repo — generally and against our
  actual suites — and decide whether it complements or should refactor the
  current test tooling.** Run it as a review-best-practices pass (what exists,
  what practitioners do, ranked options with rejections recorded), questioning
  the author liberally before scope settles. Anchors: the property suites
  (`tests/ollama_evals`, `tests/binned`), hand-rolled mutation checks
  (AGENTS.md § Prove the test fails), the fuzz guidance (§ Properties and
  fuzzing), and relations already in place unnamed — `nudge_whitespace`
  preserving content under spacing perturbation is one. Candidate seams: the
  model-output boundary, case-YAML ingestion, the policy layers. Done when a
  written recommendation exists — which seams fit, which do not, what adoption
  would refactor, and the author's adopt/adapt/reject call. [me]
- **Close out the 12 environmental suite failures — the pii half is now
  diagnosed.** The advisor pass found what this queue called undiagnosed:
  the two `tests/pii_redactor` llm failures are model-absence, named by the
  error itself — the conftest (`tests/pii_redactor/conftest.py:29`) requests
  `qwen3.5:4b-mlx-bf16` through the real `llm` CLI and gets
  `Unknown model`; no qwen3.5 model is installed. The snapshot's "runs
  against a mock" claim was wrong for these two tests and is corrected.
  **Machine-stamped:** the absence is the second machine's, 2026-09-14 —
  this Mac HAS the tag (`ollama list`, 2026-09-15), so here the diagnosis
  is unconfirmed until the two tests are re-run.
  Remediation is the author's call: install that model (space
  consideration) or make the conftest skip-with-reason when the integration
  model is absent. The 10 `tests/clipped` failures remain clipboard/TTY —
  each gets an environment skip naming the missing capability or a fix if
  the test is wrong. Run clipped and pii_redactor in SEPARATE pytest
  invocations: one invocation aborts at collection (conftest name
  collision, `from conftest import CLIPBOARD_CONTENT`). Done when a
  headless full run reports zero failed with skips named, and a capable run
  still exercises what was skipped. [me]
- **Give topics an integrations phase, and make `apps/opencode` own its
  OpenRouter wiring as the first case.** `dot_config/opencode/opencode.jsonc`
  already points `model` at `openrouter/z-ai/glm-5.3-flash` and `small_model`
  at `ollama/qwen3:8b`, while `apps/opencode` declares `topic_requires:
  [homebrew, node]` and checks neither provider — auth is a manual `opencode
  auth login` that the README leaves to the reader. A freshly provisioned
  machine therefore deploys a config whose default model cannot answer, and
  nothing in the run says so. The convention to write into `docs/TOPICS.md`:
  when a tool needs a provider or CLI at **runtime** rather than to install
  (openrouter, ollama), the tool's own topic decides on it and acts — it checks
  whether the dependency is reachable and owns the logic to add the integration
  and to take it back out, rather than delegating either to the provider's
  topic. Integrations stay separate from installation: they run only **after**
  the tool is installed, and are skipped and reported — never failed — when the
  tool is absent or the user declined it. That ordering is why this is a phase
  of its own and not more `install.yaml`. Go through **`ori`** rather than
  hand-rolling provider config: `ori opencode` is OpenRouter's own supported
  path for pointing opencode at its models, and `apps/ori` already declares
  `topic_provides: [ori]`, so the integration can require it through the
  existing dependency graph instead of a PATH probe. The two failure modes are
  deliberately not the same: a missing or declined **opencode** is a skip, while
  a missing `ori`, or an `ori` that runs and cannot complete the integration, is
  **raised** — the run fails with the named fix, or the agent surfaces it, rather
  than leaving a half-wired provider behind. Mind the auth constraint the ori
  README already records: `ori login` is interactive and deliberately not
  automated, and an inherited `OPENROUTER_API_KEY` beats whatever it stores — so
  the integration must work from that key and fail loudly, naming it, when
  neither is present. Done when `apps/opencode` wires OpenRouter through `ori`,
  confirms it with a check whose pass/fail the run reports (`opencode auth list`
  at minimum, a one-token completion if that proves too weak), skips cleanly
  where opencode was never installed, raises rather than skips when `ori` is
  absent or fails, takes the integration back out under `--tags remove`, and
  `docs/TOPICS.md` states the convention so the next tool follows it without
  re-deciding.
- **Prove topic idempotency with a second-run check, and make `--check` work
  again first.** Measured 2026-09-14 by dry-running
  `--tags "upgrade,install,minimal"`: `ok=104 changed=6 failed=1`. The good
  news is that **no package install task reported changed** — `state: present`
  converges as advertised, so adding `install` to `./update`'s tags would add
  missing topics without reinstalling present ones. The six that did change:
  two are the homebrew upgrade tasks doing their job; `apps/ollama` "Download
  latest Ollama Zsh completion to temporary path" fetches to a fresh tempfile
  every run and so reports changed forever; and three script/agent installs
  (`ollama` launchd agent, `clamav` daily script, `lynis` monthly script) need
  checking for real drift versus a check-mode artifact. The blocker is
  `failed=1`: `roles/guards/tasks/dotagents-approved-sources.yaml:59` dies under
  `--check` because the `tempfile` task above it is skipped, leaving
  `guard_trust_config` a dict with no `.path` — so the repo cannot currently be
  dry-run at all. `check_mode: false` is the fix and the repo already uses it
  four times (`apps/homebrew/tasks/upgrade.yaml:19` is the precedent). The
  standard for the test itself is molecule's `idempotence` action — run converge
  twice, fail if the second reports changed — which needs no molecule adoption
  to copy. Done when `--check` completes clean across all topics, a second
  consecutive real run reports `changed=0`, and the check runs per topic so a
  failure names which one. Pairs with the per-topic suite task below.
- **Adopt molecule for topic testing, with the vagrant driver where macOS is
  required.** Approved 2026-09-14. Molecule is the standard Ansible role test
  harness and its `idempotence` action is precisely the converge-twice check the
  task above wants, so this supersedes hand-rolling one. It also fits two
  decisions already made: scenarios live at `apps/<topic>/molecule/default/`,
  inside the topic, matching the co-location rule; and molecule is the
  conventional harness for collections, which is the direction the portability
  research points. Split the drivers by what they can actually reach — measured
  from `topic_os`: **19 topics are `[Darwin]`-only, 6 are both, 2 are
  `[Debian]`-only.** The docker/podman drivers are Linux containers and cover
  the 8 Debian-capable topics cheaply; the 19 Darwin-only ones — casks, launchd
  agents, `monitorcontrol`, `rancher-desktop` — cannot be containerised at all
  and need vagrant against a macOS VM. Unknowns to settle first, because they
  decide whether the Darwin half is affordable: which vagrant provider works on
  Apple Silicon (tart, UTM, Parallels — VirtualBox does not), image size, and
  Apple's licensing limit of two macOS VMs per host. Do not convert all 27 at
  once. Done when one Debian topic and one Darwin topic each have a scenario
  that converges and passes `molecule test`'s idempotence step. **herdr is
  the named first consumer** (judge round 1's accepted high gap: no
  automated converge; its pytest suite already covers everything molecule
  does not), the per-driver
  choice is written into `docs/TOPICS.md`, and the pytest suite still owns
  everything molecule does not — molecule tests convergence on a machine, not
  the repo's own logic. [blocked: needs the `--check` fix above, since a run
  that cannot dry-run cannot be trusted to converge twice either]
  **Plugin choices — corrected 2026-09-22, superseding the same-day note
  below it.** The first pass recommended `pytest-molecule` on PyPI metadata
  alone (Production/Stable classifier); checking its actual GitHub repo
  caught what the classifier hid: **archived 2023**, own notice says
  "functionality merged into pytest-ansible, switch there." Followed that
  chain and it dead-ends: pytest-ansible has *also* deprecated the same
  molecule-via-pytest integration and is itself EOL December 2026 (its
  README's own migration table, fetched directly). The stated reason is
  architectural, not fashion — wrapping each scenario as one
  `molecule test -s <scenario>` subprocess cannot support Molecule's own
  `shared_state` (create once in the default scenario, run component
  scenarios, destroy once) or `--workers` concurrency; those need
  Molecule's native multi-scenario orchestration. **Corrected choice: run
  `molecule test --all --workers 4` directly, no pytest wrapper** — this is
  also pytest-ansible's own recommended replacement for exactly this use.
  `pytest-testinfra` is unaffected by any of this (it's the verifier
  molecule scenarios call, not a molecule-orchestration plugin) and stays
  the choice for translating the herdr-style Python assertions
  (`host.file(...)`, `host.service(...)`) against post-converge state.
  `pytest-ansible` stays rejected, now with the sharper reason: not just
  the earlier self-deprecation quote, but a concrete EOL date and a
  published migration table (ADE for collection unit tests, tox-ansible for
  CI matrices, `ansible-inventory --list` + `pytest.mark.parametrize` for
  host iteration — none of which this repo currently uses pytest-ansible
  for, confirmed by grep, so there is nothing here to migrate, only
  something to not adopt).
- **Sweep the remaining hardcoded `/home/bdavis` paths out of
  `dot_zshrc.tmpl`.** Four of them, all inside the `{{ if eq .chezmoi.os
  "linux" }}` block (lines 69–459), so none render on macOS and none are broken
  today — they are correct only because the Debian box's username happens to be
  `bdavis`, which is precisely the failure the new convention in `AGENTS.md`
  § "Machine-specific values are resolved, never written out" exists to stop.
  Lines 331 and 355 both prepend `/home/bdavis/.local/bin` to `PATH` and can
  simply go: `~/.local/bin` is already on `PATH` via `zsh/path.zsh`, verified on
  this Mac. Line 381 sources the broot launcher by absolute path and needs
  `{{ .chezmoi.homeDir }}` or `$HOME`. Lines 89 and 267 are cosmetic — a
  compinstall marker and a shellcheck `source=` hint — and the real `source` on
  267 already uses `~`. Cannot be verified from this Mac: the block only renders
  on Debian, so `chezmoi execute-template` with a forced OS, or a check on the
  box itself, is the proof. Done when no `/home/` literal remains in the
  template and the rendered Debian output still sources broot and resolves
  `~/.local/bin`.
- **Give every topic a TDD-style test suite, and make editing a topic require
  its tests.** `tests/topics/` holds exactly one file — `test_zsh_layout.py`,
  about zsh fragment placement — against the 27 topics under `dotfiles/apps/`,
  so nothing tests what a topic's lifecycle actually does: that every state
  install creates has a teardown in remove (the CRUD invariant `docs/TOPICS.md`
  asserts but nothing checks), that `topic_os` and `topic_requires` match what
  the tasks really use, that `--tags upgrade` touches what it claims and no
  more. Nothing links a topic edit to tests either — the `bats` pre-commit hook
  matches `^(bin|scripts)/` shell scripts only, so changing a topic's YAML runs
  nothing and prompts nothing. **A topic's tests live with the topic** —
  `dotfiles/apps/<topic>/tests/`, not a central `tests/topics/` — so a topic
  stays portable: copy or extract the directory and its tests come with it,
  which is also what makes the `ai-strategy` bundle and the Refactor B
  extraction below movable rather than a re-write. Three things that costs, all
  of which the implementation has to answer: `pytest.ini` sets
  `testpaths = tests tools`, so topic-local suites are not collected today and a
  bare `pytest` would silently pass while testing none of them; `.chezmoiignore`
  ignores a bare `tests/`, so confirm whether that already excludes topic-local
  test dirs from the deployed tree and decide whether it should, since
  portability argues for shipping them so a provisioned machine can verify
  itself; and `dotfiles/template_dir/` has no `tests/`, so the scaffold must
  grow one or topic 28 starts untested by default. Tests first on the next topic
  changed, per the pytest doctrine in `AGENTS.md` and `docs/PYTHON.md`, then
  backfill rather than pausing to write 27 suites up front. **herdr is the
  proven instance** (2026-09-19): full test-first via the author-swarm +
  judge loop, 116 tests in central `tests/herdr/` — the destination stays
  topic-local suites over a shared harness, and the enforcement gate (a
  topic edit forces its tests) is the unlanded half. Done when a
  per-topic suite lives beside its topic over a shared harness (so topic 28
  inherits it instead of re-inventing it), collection reaches those suites, a
  staged change under `dotfiles/apps/<topic>/` runs that topic's tests and fails
  the commit when they are red or absent, and the tap-trust fix in `e60982c`
  has the regression test it went in without — trust-before-tap ordering, and a
  teardown that clears both the tap and the formula trust entry.
- **Build a `dotfiles-triage` agent and the skill set it loads, so a failing
  `chezmoi apply` / `ansible-playbook` / `update.sh` run goes straight into
  troubleshooting instead of stopping at "non-zero return code".** The
  `apps/opencode` skill-sync failure on 2026-09-12 is the motivating case and the
  first eval fixture: Ansible reported a return code and nothing else, because
  the task read `.stdout` while dotagents writes errors to `.stderr` — finding
  the cause took reading the `@sentry/dotagents` source. The agent's first job is
  the cheap one: name which stream the message went to, which lifecycle tag and
  topic failed, and whether the deployed tree matches the chezmoi source. Then it
  works the known failure classes, one skill each, added as they are met —
  unmigratable state at a destination (`roles/guards/`), a missing dependency, a
  pinned ref that moved (`apps/chrome`), a source edited but never applied. Done
  when a deliberately broken topic run yields a named cause and a next action
  without a human opening task YAML. [me]
- **Extend `dotfiles-triage` from naming a cause to proposing the fix, as a
  guarded PR.** Build on the public, vendor-neutral prior art, not on Sentry's
  Seer: `getsentry/seer` is `visibility: internal` (confirmed 2026-09-12 via
  `gh api repos/getsentry/seer`), so it is not a source this repo may read from,
  and nothing about the pattern requires it. The documented loop is older and
  plainer than any product — fail, halt, investigate, produce an RCA, open a PR
  carrying the RCA as its description, let a human merge. Target CARM L3
  (diagnose + propose) and stop there: **never self-apply**, which is the same
  never-auto-repair rule `roles/guards/` already follows and for the same reason.
  Every guard in `roles/guards/` is a detector that already knows its own fix
  text, so they are the natural first inputs. Done when a deliberately broken
  topic run produces a branch and a PR whose description is the RCA, and no run
  can mutate the machine without a human merging.
  **Three controls make this safe enough to run on a work machine, and they are
  cheap.** (1) A source-provenance note per design decision, naming the public
  page it came from — the tractable half of clean-room, minus the pretence that
  one person can staff two teams. (2) An explicit read-exclusion list, not one
  path: `~/code/work/sentry/` (a Seer clone sits at
  `~/code/work/sentry/what-would-kobby-do/seer`) **and** the unlicensed internal
  skills now sitting in the user-global skill path. "Do not consult it" has to be
  a rule the tool enforces, not an intention. (3) The existing fail-closed
  resolver (`bin/policy`, ethics > company > personal) gates anything that
  matters off this machine: remote model calls, log bodies, reading outside an
  allowlist. Nothing new is invented for safety; it is provenance plus the gate
  already built and tested. [me]
- **Install `tools/skill-trust` from a topic instead of by hand.** The guard in
  `roles/guards/` now shells out to it, so a machine without it provisions no
  further — correct, but the fix is currently a human running
  `uv tool install <chezmoi source>/tools/skill-trust`. That is the bootstrapping
  shape `apps/opencode`'s brew check already has: a topic should own it, and
  `tools/` will grow more inhabitants with the same need. Decide whether that is
  a `tools` topic installing everything under `tools/`, or each consumer
  declaring what it needs. Note where it lands: `tools/` sits at the chezmoi *source root*, so it
  deploys to `~/tools/`, not to `~/dotfiles/tools/` beside the Ansible tree —
  a topic would install from `~/tools/skill-trust`. Worth deciding whether it
  should deploy at all: if the tool is installed rather than cloned, the copy
  in `$HOME` is redundant and `.chezmoiignore` should skip it. Done when a fresh
  machine gets skill-trust without anyone typing a uv command. [me]
- **Render `support-escalation`'s SKILL.md, or retire it.** Moving it into
  `ai-prompt-library` on 2026-09-12 revealed it had never been a working skill:
  spec.md, 5 eval fixtures and a legacy `.skillet.yaml`, but no SKILL.md, so
  nothing could load it — it sat in the user-global path for two weeks doing
  nothing. `skillet status skills/support-escalation` will report the legacy
  format first; migrate that before rendering. Until a SKILL.md exists dotagents
  cannot discover it, which is the correct state for something unfinished. Done
  when `skillet validate` passes and it installs from the wildcard, or the
  directory is deleted and this line with it. [me]
- **Make the commit-proportionality escape graduated instead of binary.**
  `Proportionality:` currently short-circuits `verdict()` before the budget is
  computed, so it does not tolerate variance — it switches the check off for that
  commit, permanently and invisibly. The evidence that this is the wrong shape is
  the usage record: **one use in 449 commits, and that one was unnecessary** —
  193 words against a 220 budget on 10ccccd, added pre-emptively after the
  previous commit was rejected. An escape easier than thinking gets used without
  thinking. Three changes, in this order:
  (1) **Bound it.** A trailer grants a multiplier on the budget, not exemption —
  and a hard ceiling no trailer can exceed, so an essay still fails.
  (2) **Type it.** A small vocabulary — `security`, `deletion`, `migration` —
  each with its own multiplier, free text after the category. That makes the
  *why* greppable, which is what turns the escape into something auditable rather
  than a hole. An unrecognised category earns no bonus, so the choice is a known
  reason or a split.
  (3) **Close the loop.** Report at commit time when an escape was not needed
  ("this would have passed with 27 words to spare"). Nothing today can notice a
  false positive, which is exactly why the only one went unnoticed.
  Deliberately **not** doing diff-derived modifiers (test ratio, additions vs
  deletions) yet: they sound the most contextual and are the most likely to be
  wrong. A test-ratio bonus would have penalised this session's best commits,
  which were mostly tests, and it is trivially gamed. Add derived signals only if
  the audit from (2) shows a category is systematically mis-sized. Use the
  existing `--calibrate` mode to check any multiplier against history before
  adopting it — and heed the script's own warning that fitting to the corpus
  encodes the habit as the standard. Done when a message over budget with a typed
  reason passes within its multiplier, the same message without one fails, an
  essay fails either way, and an unnecessary escape is reported as such. [me]
- **Define an `agentic-context-engineer` role and add it to the ai library.**
  A role, not a skill: it is invoked deliberately for open design questions,
  wants its own context, and returns a considered answer — where a skill changes
  how the current work is done. Distribute it as a `[[subagents]]` entry rather
  than hand-placing a file in `~/.claude/agents`, so it installs the same way the
  skills do and survives a rebuild (dotagents projects subagents to
  `~/.claude/agents/*.md` at user scope; confirmed 2026-09-12). The role must
  **compose** the existing method skills — `review-best-practices`,
  `interaction-questioning`, `no-ai-slop` — and add only framing and judgement on
  top; a persona that restates method it could have loaded is the failure mode
  here. Done when `/agentic-context-engineer` answers an open question with a
  recommendation and its rejected alternatives, and the definition installs from
  `ai-prompt-library` on a fresh machine. [me]
- **[4] Fill `~/.local/state/ai-policy/company.yaml`'s 22 TODO fields.** Decided:
  proceed top-down as proposed — `device.approved` gates the rest. Machine-local
  and unversioned, so it cannot be tracked here beyond this pointer. Agent-unreadable on this machine (permission rules) — existence is the author's to verify; do not treat as done-or-lost. Until it is
  filled, `fail_closed` means the company layer denies everything it is asked,
  which is safe and useless.
- **Work out why `fabric` on `$PATH` is 1.4.459, then retire that install.** The
  orphaned `v1.4.478` tree is gone (72M reclaimed, `mise` took its `v1`/`v1.4`/
  `vlatest` symlinks with it), leaving `1.4.459` beside the current `1.4.478`.
  `1.4.459` is not safe to remove yet: it is the copy on `$PATH` in at least one
  running shell, even though `mise which`, `mise env` and `mise ls` all agree on
  1.4.478 and nothing in this repo writes the stale entry. Looks like
  session-inherited env rather than config, but that was **not** confirmed — a
  clean shell had no fabric on `PATH` at all, so the test proved nothing. Done
  when a brand-new terminal is checked: if it reports 1.4.478 this was stale env
  and `mise uninstall github:danielmiessler/fabric@1.4.459` closes it out; if it
  reports 1.4.459 something is writing that path and the uninstall would break
  a working command.
- **Drop the `npm:@sentry/skillet` pin in `apps/mise/files/config.toml` to
  `latest`.** The pin sat at 1.7.0 since 2026-09-11 because mise's npm resolver
  (aube) could not fetch vite's 39 MB packument through
  `sfw.security.sentry.io` — `curl` and `npm` both can, so it is a mise-side
  limit, not registry or auth. **Resolved 2026-09-14: 1.8.0 verified working
  here** (`skillet validate .` exits 0; 1.8.0 was already installed, and `mise
  install` pruned 1.7.0 — reinstall it via
  `mise install npm:@sentry/skillet@1.7.0` if ever needed), committed as
  ee09e38. What remains before the pin drops to `latest`: the
  `apps/mise/tasks/upgrade.yaml` pin-print must follow the version, decide
  whether the four `npx @sentry/skillet@latest` task aliases stay floating
  (they align once the pin is `latest`), and `spec.md`'s 1.7.0 pin plus the
  `docs/REFERENCES.md` row need aligning — that alignment is queued there
  already. Done when the config says `latest`, the pin-print tells the truth,
  and the spec/REFERENCES rows agree with it. **Changelog-read blocker,
  recorded 2026-09-15:** the REFERENCES standard (read the 1.7.0→1.8.0
  changes before moving the pin) cannot currently be satisfied from this
  machine — the source repo is not accessible (the getsentry org is
  SAML-blocked; npm metadata carries no repository URL) — so the pin stands
  on local evidence only and the read must happen from a machine with
  access. **Read DONE 2026-09-15, on this Mac after all** — the block was
  the second machine's. The 1.7.0→1.8.0 compare (5 commits) shows grammar
  and exit codes untouched; the change is diagnostics (the no-eval-case
  warning was deleted) and the authoring workflow (evals opt-in). Pin
  aligned at 1.8.0 across `config.toml` and the spec footer (94389a5);
  REFERENCES records the read. What remains of this task: the
  `apps/mise/tasks/upgrade.yaml` pin-print must follow the version, and the
  four `npx @sentry/skillet@latest` aliases need a float-vs-pin decision.
- Install `ty` and typecheck the Python. Named in the house toolchain and
  currently absent — not installed, zero references in the repo. 42 test files
  and 22 Python scripts are unchecked (counted 2026-09-23: 13 `uv run
  --script`, one the stray `bin/executable_archive.bk`; 9 `python3` — the
  earlier "32" and "36" were stale). `bin/executable_scanfiles` has a
  `# /// script` block under a `python3` shebang: inert, as it declares no
  dependencies, but against the `docs/PYTHON.md` rule. Note `ty` is
  pre-1.0; decide whether it
  gates commits or just reports before wiring it into `prek`.
- Wire `ruff` into `.pre-commit-config.yaml`. It is installed and the toolchain
  names it, but the hook config runs shellcheck and bats only, so no Python file
  in this repo is linted on commit. Settle the ruleset first — 22 scripts written
  before any linter will not pass a default config cleanly.
  mise also declares ruff twice — `ruff` (`apps/mise/files/config.toml:147`)
  and `pipx:ruff` (line 186) — so pick one first; § Now #1 (p) may pin it in
  a lock group instead.
- Integrate `xdoctest` and make illustrative examples a tested part of the
  docs. Docstring examples in the 22 Python scripts and any Python modules
  run under pytest via the xdoctest plugin; docs (`dotfiles/docs/`, READMEs)
  carry code examples where they clarify, verified rather than trusted —
  written for humans first, machines as the proof they still work. Survey the
  ecosystem before building anything: xdoctest for docstrings, and for fenced
  blocks in markdown weigh sybil / pytest-examples / a pytest-markdown runner
  before hand-rolling one. Done when: xdoctest is in the documented pytest
  command (AGENTS.md § Commands), docstring examples in `bin/` are collected
  and green, `docs/PYTHON.md` records the convention (what must carry
  examples, how to write and run them), and a markdown-example mechanism is
  either adopted or consciously rejected with the reason recorded. Pairs
  with the plain-language standard item — examples are prose too.
- Make test conftests skip rather than error on a missing optional dependency.
  `tests/ollama_evals/conftest.py` loads the eval harness as a module, and the
  harness imports Pillow at module level, so without `--with pillow` the whole
  directory produces 53 collection errors instead of 52 passes — the suite
  aborts instead of running what it can. Same class as the hypothesis guard
  fixed today, one layer deeper: the import happens before pytest can skip
  anything. `pytest.importorskip` in the conftest is the likely fix, but check
  what else the harness pulls in at import time first.
- Check AGENTS.md and CONTRIBUTING.md for places the agent→function
  graduation policy should apply, and reference the policy artifact from
  `ai-prompt-library` once it exists. The bias: prefer a trusted function
  over agent judgment where the task is mechanical; agents stay for
  adaptability and interpretation (high-context tasks — deciding what to do,
  how to succeed). **[blocked: the threshold research and council decision
  are owned in ai-prompt-library's TASKS.md — no text lands here until the
  artifact exists.]** Same artifact the shift-left study's two-track trust
  model (§ Now, "Build the LEDGER") routes its global-vs-per-repo,
  skill-portability question to — one open question, two entry points here.
- Sweep committed machine-adjacent strings, per the audit in
  `dotfiles/docs/MULTI-MACHINE.md` (2026-09-12). The audit found: employer-
  adjacent paths (`~/code/work/sentry/`, `sfw.security.sentry.io`), the §
  Private tasks section describing the work it points to (obfuscation that
  signals itself), environment mentions ("work machine", "the second
  machine", "a Seer clone", "the work workspace"), and session-claim
  provenance narration. Rewrites generalize to environment-neutral classes;
  the purge of employer strings itself stays under § Private tasks. Done
  when a grep over the committed tree for the audit's patterns comes back
  clean and the MULTI-MACHINE design's generalization test is applied to
  every rewritten line. **Wait for the council verdict first** — the council
  may change what "bounded pointer" means before the sweep rewrites
  pointers.
- Decide when `scriv collect` runs. The changelog exists and fragments
  accumulate, but nothing says what a "release" is for a dotfiles repo that does
  not release. Candidates: on a cadence, at each machine rebuild, or never —
  leaving everything under Unreleased, which is legitimate and costs nothing.
  Until this is settled the changelog grows one section and is still readable.
- **Machine-shaped gate outputs, and a skip census instead of coverage %.**
  From the shift-left study's advisor council: every gate (prek, pytest,
  `skillet validate`) should emit exit code + `file:line` citations + one
  JSON artifact (`pytest-json-report`) — a check without a
  machine-consumable output does not exist for an agent to act on without
  narrative. Pair it with a skip/xfail-count trend (JSONL, one line per
  run): coverage % was researched and explicitly rejected as the
  quality-over-time metric — it measures execution, not verification, and a
  `pytest.mark.skip` body counts as "covered," so a healthy-looking percentage
  can coexist with this repo's actual failure mode (tests that pass while
  testing nothing). A rising skip count is the early-warning analog of that
  failure and is the one metric the study found that directly measures it.
  **Conditional on the author actually reading the trend** — a trend file
  nobody opens within two weeks is exactly the kind of mechanism that
  shouldn't exist (PRD.md's verification-effort-scales-with-blast-radius
  governor). Done when a run emits the JSON artifact, the skip count is
  appended to a trend file, and the author has used it at least once to make
  a decision.
- **Teach `skill-trust` about foreign skill buckets, so a third party's sync
  stops failing provisioning.** [unclaimed — written 2026-09-23, cold-readable;
  no prior conversation context needed]

  **The problem, verified by direct inspection 2026-09-23.** Claude Code's
  cloud sync writes `synced/<org>_<user>/` into `~/.agents/skills`, because
  `~/.claude/skills` is a dotagents-made symlink to it. `cmd_audit`
  (`tools/skill-trust/skill_trust/cli.py:118`) iterates top-level directories,
  finds `synced` undeclared and carrying no licence of its own, and returns
  DENIED, which `roles/guards/tasks/dotagents-approved-sources.yaml:99` turns
  into a failed run. The bucket holds 10 skills: 4 Anthropic proprietary
  (`LICENSE.txt` forbids retaining copies outside their services), 4 with no
  licence, 2 MIT.

  **Measured behaviour of that bucket — tested, not inferred (2026-09-23).**
  Sync runs at Claude Code session start; there is no daemon and no launchd
  job. It is suppressed entirely when `ANTHROPIC_API_KEY` is set, because the
  API key outranks the claude.ai login. Sync does **not** prune directories it
  does not own — a probe directory survived two syncs and never entered
  `manifest.json`. A deleted skill is **recreated byte-identical** on the next
  session (deleted `adhd`, re-synced, `cmp` identical). `manifest.json` carries
  no content hashes, only timestamps, and the bucket mutates on its own
  (`docx` updated upstream mid-test). Therefore **`deny` is not implementable
  against a foreign bucket** — deletion loops forever — and the tool must say
  so rather than attempt it.

  Done when: a bucket carrying all three pieces of evidence (path
  `<store>/synced/<id>/`, sibling marker `synced/.bucket-<id>`, a parsing
  `manifest.json` with a `skills[]` array) resolves to a recorded `external`
  verdict carrying a date and a reason, instead of a denial; a directory merely
  *named* like a bucket without that evidence still fails closed; `deny` on a
  foreign bucket is refused with the churn-loop reason rather than attempted;
  buckets carry a human alias (deduced by default, e.g. `claude-sync`) that is
  display-only, with rules keyed on the bucket id so renaming an alias cannot
  change what is approved; the guard runs as the last task in `apps/opencode`
  so unrelated topics converge before the gate can fail; `discover.py:32`
  reports `license: Proprietary. LICENSE.txt has complete terms` as proprietary
  rather than "no licence found"; and every new test has been seen to fail with
  its mutation recorded in the commit message.

  Deliberately **not** in scope, queued separately: the interactive consent
  system (review queue, batch approval, export/import for machine rebuilds,
  agent JSON protocol). Physical separation of the two stores is **rejected on
  evidence** — dotagents only ever makes whole-directory symlinks
  (`dist/symlinks/manager.js:15-82`), its `symlinks.targets` key is
  project-scope only (`dist/config/schema.js:89`), so the only lever is
  dropping `claude`/`cursor` from its `agents` list, which would mean
  hand-managing per-skill links. The author declined that.

  **Status 2026-09-23 — half landed, rest claimed in a worktree.** `eb0b4b2`
  did the licence-reporting half: `discover.py` reads a prose `license:` field
  (Anthropic's `Proprietary. LICENSE.txt has complete terms` previously matched
  nothing and reported as carrying no licence at all) and a PROPRIETARY tier
  reports it as declared rather than unknown. Both mutations were run and each
  caught only its intended tests; suite green at 38.

  Remaining work is on branch `skill-trust-foreign-buckets`, worktree
  `~/code/wt-skill-trust-foreign-buckets`, cut from `eb0b4b2`: `buckets.py`
  with the three-part evidence detection and deduced aliases; the `external`
  verdict; `deny` refused for foreign buckets carrying the churn-loop reason;
  the `guard_foreign_buckets` and `opencode_skill_foreign` config keys; and
  moving the guard to the last task in `apps/opencode`. Two questions are open
  and block none of it: a machine id that survives a rebuild, for the Part 2
  rules filename (hostname does not), and whether a fourth `blocked` verdict is
  worth having so "unsolved" can be said without faking a refusal.

  One process note for whoever picks this up: the commit that first added this
  task (`80d8f27`) was made by a different session and swept this text in
  alongside its own. That session recorded the scope error in a git note rather
  than rewriting history — push `refs/notes/commits` when publishing.

  **Status 2026-09-24 — implemented, awaiting review.** The remaining work
  landed on the branch as four commits: `buckets.py` with three-part evidence
  detection and deduced aliases; the `external` verdict with a date and reason;
  `deny` refused for foreign buckets (loud, run proceeds, per the author's call);
  the `guard_foreign_buckets` / `opencode_skill_foreign` keys (both default
  on); and the guard moved to the last task in `apps/opencode`. Every mutation
  named in the commit messages was seen to fail its intended test first. The
  `user.email`/`user.name` in `dot_gitconfig.tmpl` are now parameterized off
  `.email`/`.name` and prompt for a first-time machine, so the personal address
  no longer follows the file onto a work machine unattended. The two open
  questions (machine id, `blocked` verdict) remain open and still block
  nothing; the vestigial `[mergetool ""]`/`[difftool ""]` were confirmed dead
  — git never consults an empty subsection name — and deleted on main.
- **Make the test suite fast and model-safe: fix the conftest collision, keep
  model calls out of the default run, and wire pytest-xdist as an opt-in fast
  loop.** [me] Done on branch `test-perf-xdist` (31d532d, fa25f20, 7908b50,
  41bcc41, a58e710, 1ef7c86, 6c9de21) — awaiting author review, not merged.
  Council study 2026-09-23 (three explore agents + xdist docs). **Correction
  to the original brief:** the claim that "two unmarked `test_binned_cli`
  cases make real model calls" is WRONG and is retracted. Measured on this
  machine: `binned --auto "echo hello"` exits 2 in 0.26s with `No such command
  'echo hello'` (typer rejects the free-text as a subcommand), `ollama ps`
  unchanged — no model call happens, in the source *or* the deployed copy. The
  real defect is worse: `test_explicit_command_enters_generate` and
  `test_command_with_embedded_flags` pass **vacuously**, on a parse-error
  message that happens to echo the command string. Their docstring claim ("We
  do NOT make real LLM calls") is accidentally true, not for its stated
  reason. Also corrected: slowness is **not** dominated by model calls (7
  tests, now opt-in) but by per-test subprocess startup — ansible-playbook and
  `uv run --script` at 3–13s each. Done when one invocation collects every
  test directory without ImportError, a bare `pytest` makes zero real model
  calls, and the xdist fast loop is green with a mutation check recorded —
  all three now hold (210 collected clean across the four collided
  directories; `addopts = -m "not llm_judge"` with both directions tested in
  `tests/suite`; 170.7s → 46.75s measured 2026-09-23, 32 cores, 641 passed /
  2 pre-existing failures / 8 skipped, no new failures).

  **Open, for the author** (found while working, not decided):

  1. **Judge/model ids do not exist on this machine.** `ollama list` has
     `gemma3:12b`, `qwen3:8b`, `gpt-oss:20b`, `qwen3:30b`,
     `qwen25-14b-opt:latest`, `qwen2.5:14b`, `mistral:7b` — and nothing else.
     So `tests/pii_redactor`'s `INTEGRATION_MODEL = "qwen3.5:4b-mlx-bf16"` is
     absent (the known "Unknown model" item), and `test_binned_llm_judge`'s
     default judges `devstral-small-2, qwen3.5, claude-4-sonnet` are all
     unavailable: two not pulled, and `claude-4-sonnet` is a vendor-native id
     which resolves to nothing under the llm environment (AGENTS.md § Models —
     use `openrouter/anthropic/...`). Install, substitute, or skip-with-reason
     is the author's call, and substituting changes what is being measured so
     it must not be done silently.
  2. **Two `test_binned_cli` cases are vacuous** (above). Fixing them means
     deciding what the free-text routing should do, which may be a binned CLI
     question rather than a test question.
  3. **Source vs deployed is inconsistent.** `policy` and `quarantine` test
     the chezmoi *source*; `clipped`, `pii_redactor` and `binned` test
     `~/bin`, so a green run can be against a stale binary. Note
     `bin/executable_pii-redactor` and `bin/executable_binned` are **not** +x
     while `bin/executable_policy` is — switching needs an invocation change
     (quarantine uses `python3 SCRIPT`) as well as a path change.
  4. **`testpaths = tests tools`.** The previously documented `pytest tests`
     silently skipped `tools/skill-trust`; the documented command now says
     `pytest tests tools`. Whether `tools` stays in `testpaths` is undecided —
     it pulls a second packaged project into every run.
  5. **`tests/clipped`'s clipboard cases are slow and order-dependent** — in
     sequence they fail and burn `run_clipped`'s 60s timeout each, so the
     suite cannot complete quickly until they get an environment skip or a
     fix. Pre-existing and tracked by the "12 environmental suite failures"
     item; not touched here.
  6. **The recorded "104s" suite figure is stale.** Measured 2026-09-23:
     170.7s for everything but `tests/clipped`, `-m "not llm_judge"`. Several
     places still quote 104s.
  7. **Run one suite at a time.** Two concurrent `uv run` invocations contend
     on the `~/.cache/uv` lock and Hypothesis then reports deadline failures
     that are CPU starvation, not bugs — corrupted evidence rather than a
     clean skip. The fast-loop note in AGENTS.md § Commands records this.

- **Derive minimal permission rules from tool manuals for all three agent
  surfaces.** Queued by the author 2026-09-23: a subagent reviews the full
  help menus and manuals for every tool the repo's agents invoke — git,
  chezmoi, uv, pytest, mise, and the rest — classifies each subcommand and
  flag as safe (allow), irreversible (ask), or dangerous (deny), and writes
  the result into the three permission configs: `opencode.jsonc` (opencode),
  `.claude/settings.json` (Claude Code), and Cursor's `cli.json`. The goal
  is fewer approval prompts without weakening the deny tier. Known gaps to
  close: `env *` is an arbitrary-exec wrapper in the allow tier;
  `sed -i`/`awk system()`/`rg --pre` can execute code; `git checkout .`/
  `git restore .` destroy uncommitted work; `git -C` bypasses
  subcommand-level rules. Done when all three configs carry rules derived
  from the tools' own documentation, the deny tier still blocks
  `chezmoi apply`, force-push, and credential paths, and a deliberately
  dangerous command has been seen to prompt. [agent: sub]

- **Allow worktree creation and read-only `gh`; close the `--force-with-lease=`
  deny gap.** [agent: OpenCode restart-review, 2026-09-24; author-requested]
  In `opencode.jsonc` (both bash blocks) and `.claude/settings.json`:
  `git worktree add` allowed, every other worktree mutation asks; read-only
  `gh` subcommands (pr/issue/run/release/repo/workflow list-view, search,
  status, and GET-only `gh api`) allowed, anything that writes still asks;
  `git push --force-with-lease=*` denied — found live when an `=`-form
  force-push matched no deny rule. Carries the restart-review worktree's
  uncommitted permission edit as its own commit. Done when the tier tests
  cover each new rule, have been seen to fail without it, and a PR is open
  (policy path: human review). Branch and worktree
  `perms_gh_read_worktree_add`. Feeds the permission-rules review above.
  Revised 2026-09-24: the read-only `gh` carve-out landed in opencode only.
  Claude Code resolves deny > ask > allow regardless of order, so no allow
  can carve reads out of its `Bash(gh *)` ask; splitting that rule is left
  to the permission-rules review above.

- **Document bucketing a task into PRs.** [agent: OpenCode restart-review,
  2026-09-24; author-requested] `docs/WORKTREES.md` gains a Bucket lifecycle
  step and § Bucketing: the one-sentence-without-"and" test, dependency
  ordering, one branch per bucket, each checked alone and all checked
  together, then publish and supersede; reaping cherry-picked branches uses
  `git cherry`. AGENTS.md § Decomposing points to it for tasks that need more
  merges than planned. Done when the docs gate passes and a PR is open.
  Branch and worktree `docs_bucketing`.
- **Label meld's panes from sections git actually reads.** [agent: OpenCode
  restart-review, 2026-09-24; author-requested] The deployed `~/.gitconfig`
  carried pane labels in `[mergetool ""]`/`[difftool ""]`, which git never
  consults. Move them into `[mergetool "meld"]` and `[difftool "meld"]` in
  `dot_gitconfig.tmpl`. Done when a test renders the template and git itself
  resolves both labelled commands, seen failing first, and a PR is open
  (deployed file: human review). Branch and worktree `gitconfig_meld_labels`.

- **Define "outcome" — the unit a bucket, a task and a PR each carry.**
  [question for the author, 2026-09-24 — no session holds it] Ask: adopt the
  definition drafted since in another of the author's repositories (local,
  unpublished; it grew out of the council below), and if so, share it or
  keep a local copy here? That draft settles "outcome" as the part of the
  work a reviewer accepts or rejects for one reason, with everything needed
  to judge it (split rule, join rule, the "and" sentence as a smell), and
  adds riders, merge-gate classes and a task/change nesting. Review it
  against the verdicts below before recording anything.
  `docs/WORKTREES.md` § Bucketing says a bucket is one outcome, tested by a one-sentence
  description without "and", but never says what an outcome is. Gather the
  leading candidates, put them to an advisor council (sub-items below), and
  bring a recommendation to the author, who has a candidate of their own.
  Done when the author has chosen a definition and it is recorded — in
  `docs/GLOSSARY.md` and § Bucketing — with the council's dissent kept beside
  it. Branch and worktree `outcome_definition`, stacked on `docs_bucketing`.
  - **O1 — domain-modelling advisor.** [agent: general/outcome-o1] Judge the
    candidates through bounded contexts and aggregates, mapped onto this
    repo's topics and roles. Research only; done when a written verdict names
    a preferred definition, its failure cases, and what it rejects.
  - **O2 — revert-and-history advisor.** [agent: general/outcome-o2] Judge
    the candidates by what history needs: revert, bisect, cherry-pick,
    changelog. Research only; same done-condition as O1.
  - **O3 — reviewer advisor.** [agent: general/outcome-o3] Judge the
    candidates by what a reviewer who was not in the session can hold and
    decide on. Research only; same done-condition as O1.
  - **O4 — agent-operability advisor.** [agent: general/outcome-o4] Judge
    whether an agent can apply each candidate consistently, and what a
    mechanical check (a future determinant function) could and could not
    decide. Research only; same done-condition as O1.
  - **O5 — skeptic.** [agent: general/outcome-o5] Argue against every
    candidate: solo-developer cost, messy existing history, the transition
    period, where each definition over- or under-splits. Research only; same
    done-condition as O1.

  **Council verdicts, 2026-09-24** (five `general` subagents, one model, five
  lenses — not a mixed-model council):
  - *Agreed by all five:* tests, TASKS.md lines, handoff pointers, changelog
    fragments and review fixups ride with their outcome and never count as
    one. #11 is one outcome, since a role with no caller cannot be judged, so
    it joins its first caller. #8 was three or four outcomes. #10 is one.
    Rejected: entity+verb alone (the component cut AGENTS.md forbids; #8 passes
    it with several decisions in one file); owner-facing capability (excludes
    refactors, docs, governance); done-condition alone (circular).
  - *Mostly agreed:* #9 is one (O4: two). #12 is two, kept together by the
    author's choice (O1, O3, O4, O5). "One sentence without 'and'" is gameable
    by abstraction ("tighten git permissions" hides #8), so it is a smell, not
    a gate: write it at the level where a rejection would be stated.
  - *Against the coordinator's composite:* "one owner" rejects #11 and renames
    (O2, O5). "One check can prove" invites ceremony tests for docs, which is
    Class B evidence (O3, O4, O5); if kept, the check must be named before the
    work (O4). Revert independence only needs to hold one way (O2).
  - *O1 domain:* owner = whoever must undo it (a topic's remove.yaml); proof
    sits inside that boundary. Define the nesting: a commit is one decision,
    an outcome is one or more decisions, a task delivers one outcome.
  - *O2 history:* merge commits make the PR the outcome at `--first-parent`
    level and the commit the decision; cherry-picked buckets lose original
    SHAs, so one changelog fragment per bucket becomes the history record.
  - *O3 reviewer:* split by reasons to reject; join by evidence needed to
    judge. The quiz before merge should need one question.
  - *O4 agent operability:* mechanical census of owners and merge-gate classes
    surfaces "probably several outcomes", never blocks; bucketing by gate
    class first keeps self-mergeable parts self-mergeable and is the only
    split that comes out the same every session.
  - *O5 skeptic:* do not define tightly; the cost of splitting lands on the
    one human reviewer, so split hardest where a wrong merge cannot be undone
    (policy, deployed files) and loosest where it can (docs, TASKS.md); apply
    to new buckets only, never rewrite merged history.

- **Warn that a stacked PR can merge into its parent's branch.** [agent:
  OpenCode restart-review, 2026-09-24] PR #12 merged into
  `restart_stale_role_ollama` after #11 had landed, so `main` never got it
  (re-landed as #15). `docs/WORKTREES.md` § Bucketing step 6 now says to
  check that a stacked PR's base is `main` before merging it. Open question
  for the author: turn on `delete_branch_on_merge`, which makes GitHub
  retarget children automatically. Done when the docs gate passes and a PR is
  open. Branch and worktree `docs_stacked_pr_base`.
  Revised 2026-09-24 by the author: rather than warn, open pull requests only
  into `main`. Feature branches may still stack and take commits from each
  other with no PR; a child opens its PR after its parent merges and it is
  rebased onto `main`. The `delete_branch_on_merge` question is moot, since
  no PR targets a branch that could be deleted.

## Planned


- **Grow a dotfiles agent + skill set — an additive agentic layer that
  compounds one capture per session, over the unchanged determinant layer.**
  [me] `spec.md`/`AGENTS.md`/the guards keep constraining; this adds skills
  and agents that encode the reusable capability each session produces, so
  working here gets faster rather than more constrained. A skill captures a
  method (first candidate: the council critique — fresh advisors plus a
  second-vendor model, disagreements to the author), an agent a role; the
  `description` in each is the progressive-disclosure trigger. Sync with
  ai-prompt-library is bidirectional: a generally-useful skill developed here
  is pushed upstream, while a library skill that applies here is vendored in
  (copy + attribution + license) so the repo stays self-contained and
  upgrades happen here. Classify each capture with one question — does this
  help in a repo that is not dotfiles? — and record the answer when it lands:
  general pushes upstream, repo-local vendors in. Declared and installed via
  dotagents (`agents.toml` + `agents.lock`); facts stay in `docs/`. Done when
  the process is written, the first skill — the council critique — lands and
  is declared, and the `AGENTS.md` ladder is amended to permit vendoring
  (authoring goes out; a finished, applicable skill may be copied in).

- **Add a `uv` topic — the astral-installed runtime-manager mise consumes.**
  [agent: pyproject] `topic_name: uv`, `topic_provides: [uv]`, `topic_os:
  [Darwin, Debian]`, `topic_tier: runtime-manager`. install/upgrade run the
  astral installer at latest by default (a `uv_version` variable pins); remove
  deletes `~/.local/bin/uv` and `~/.local/bin/uvx`. Decision (author,
  2026-09-28): uv is system-level and latest at the user/global level;
  projects pin their own version and mise syncs to it. Done when a fresh run
  installs uv idempotently and remove tears it down.

- **Make mise declare `topic_requires: [uv]` and add an idempotent `mise
  reshim`.** Decision (author, 2026-09-28): a runtime tool mise calls is a
  declared dependency of the mise topic. The reshim lands after "Materialize
  mise-managed tools" so stale shims (the U1 edge case) self-heal on every
  provision. Done when mise resolves uv first in the dependency graph and a
  stale-shim machine converges to system uv on a normal run.

- **Shift Python ownership from mise to uv, mise syncing.** Decision
  (author, 2026-09-28): uv is the better Python env manager. `uv python
  install X` installs, `mise sync python --uv` shares it, `mise use -g
  python@X` selects it; mise runs uv beneath and integrates Python with the
  other runtimes. Today `python = "3.14"` is mise-managed and mise
  `topic_provides: [python]`. Also set `python.uv_venv_auto = "source"` — the
  cookbook's non-deprecated form, which clears the stray deprecation warning
  (traced to `pypi.uvx = true`, not a config key). Done when Python installs
  via uv, is available to mise via sync, and the two no longer fight over the
  version. [blocked: the uv topic lands first]

- **Move the bootstrap into chezmoi — a minimal `curl | sh` fetches chezmoi,
  and chezmoi runs the rest.** Decision (author, 2026-09-28):
  `dotfiles/bootstrap/bootstrap.sh`'s install chain becomes chezmoi
  run-once / `.pre-apply` hooks so `chezmoi apply` drives Homebrew, uv, and
  the rest. The only step outside chezmoi is fetching the chezmoi binary
  itself. Done when a fresh machine starts from a minimal chezmoi install and
  chezmoi runs the full provision chain.

- **Add a chezmoi topic so Ansible updates chezmoi post-bootstrap.**
  Decision (author, 2026-09-28): bootstrap uses chezmoi to pull and begin the
  install; Ansible then maintains chezmoi through its own topic. Done when a
  `--tags upgrade` run bumps chezmoi and the topic's remove is defined.

- **Watch the `pytest-agent-*` ecosystem — reopen trigger, not a standing
  task.** `pytest-agentkit`, `pytest-agentprobe`, `pytest-agent-eval`,
  `pytest-agent-health` verified real on PyPI 2026-09-22 but too immature to
  adopt (1-3 releases, weeks to months old, Alpha, no adoption evidence).
  Author: keep them on watch for when this repo (or a similar one) moves
  toward a more heavily agent-integrated testing environment — the function
  they aim at (agent regression testing, threshold pass/fail, catching
  silent agent failures) is real and only getting more relevant here, just
  not served by any of these four yet. Reopen when: one of them ships a
  second year of releases with real adoption evidence (stars, dependents,
  a case study), or this repo's own herdr-style judge-panel method stops
  being sufficient for a concrete new need. Until then the herdr
  judge-panel/fusion-council calibration method remains the house answer.

- **Revisit the `$HOME`-exception list — reopen trigger, not a standing task.**
  Author decision 2026-09-22: no test may touch real `$HOME` for now (find a
  workaround — mock the keychain, avoid `zsh -l` — for every case rather than
  naming exceptions), because the actual edge cases aren't known yet. Reopen
  when: the `$HOME`-sandbox fixture (§ Now, the xdist sub-item) is built and a
  real case resists sandboxing, or a second such case appears. Same shape as
  the O4/Renovate reopen trigger already used in this file — decide when the
  problem is real, not before.

- **Add an ollama model-health check for every model project tooling invokes.**
  Author queued 2026-09-22, deferred — lower priority, no action taken in the
  shift-left study. Trigger: the shift-left fusion council found every MLX
  model on ollama fails at call time (`mlx runner exited unexpectedly`,
  exit status 2/500 — verified 2026-09-22 on qwen3.6:35b-mlx and
  gemma4:12b-mlx; GGUF olmo-3.1:32b works), and `tests/pii_redactor/conftest.py:29`
  requests `qwen3.5:4b-mlx-bf16` by exact tag, failing into test failure when
  absent. Principle from the author: any model a tool or test calls must be
  verified to exist and respond — model availability becomes a tested
  property, not an assumption. Done when a check (test or preflight) confirms
  each invoked model id exists in `ollama list` and answers a call, and
  tooling that depends on a missing/broken model skips-with-reason instead of
  failing. [me]
  *Evidence 2026-09-22 evening:* a restart of `com.ollama.server` fixed it —
  `gemma4:12b-mlx` and `qwen3.8:27b-mlx` answered afterwards. The cause is not
  established. The server process had run since 2026-09-12 on 0.33.3, and brew
  installed 0.34.3 at 17:52 PDT without restarting it, so by evening client and
  server disagreed. But the 09:32 failure predates that upgrade, so the mismatch
  cannot explain it; a fresh process and a new version arrived together and
  this evidence cannot separate them. The upgrade path not restarting the
  server is its own defect regardless.

- **Author the `explain-calibration` skill — whether and how much to
  explain.** Queued from the 2026-09-22 handoff (decisions 25, 31–33). Lives
  in ai-prompt-library, authored with skillet-authoring — this line tracks it
  here because spec.md § Writing now binds the outcome and references the
  skill for the method. The skill carries the method the spec defers: ask the
  question that sits under the most terms, not the term in front of you; ask
  a reasoning question, not a vocabulary one; infer down and verify cheaply
  with one gloss — being wrong costs one parenthesis. Compactness method:
  conclusion in one sentence, plain meaning in one clause, the consequence
  that makes it matter, evidence only if load-bearing. Optional-dependency
  discovery (decision 27): it looks for feynman-explanation and, if absent,
  asks permission to probe for an installer, else asks the user's preference;
  no preferences saved by default. Done when the skill exists in
  ai-prompt-library, passes `skillet validate` and its own evals, and is
  installed here through the machine's skill manager.

- **Author the `feynman-explanation` skill — how to explain from first
  principles.** Queued from the 2026-09-22 handoff (decisions 25–26), the
  companion to explain-calibration (which decides *whether/how much*; this
  one is *how*). Lives in ai-prompt-library, authored with skillet-authoring.
  Activation is inferred from signals, never user-invoked: domain rated
  new/general-principles; "what is X"; the same concept asked twice; "plain
  english"/"ELI25"; a decision hinging on a term the user hasn't used;
  undefined density. Internal self-check: would the explanation survive being
  repeated back? Done when the skill exists in ai-prompt-library, passes
  `skillet validate` and its own evals, and is installed here through the
  machine's skill manager.

- **Declare `explain-calibration` and `feynman-explanation` as agentic
  dependencies.** [blocked: until the two skills exist — see the authoring
  tasks above] spec.md § Dependencies makes a referenced skill a project
  dependency: declared where the machine's skill manager installs and keeps
  it current, skill-trust passing. spec.md § Writing already references
  explain-calibration, so the declaration is owed the moment the skill
  exists. Done when both skills are declared, installed via the skill
  manager, and the declaration names the references that pull them in.

- Migrate the mise `python.uv_venv_auto` setting before mise 2027.7.0 removes
  it — mise warned the deprecation during the herdr work (2026-09-19:
  `python.uv_venv_auto=true` must become `python.uv_venv_auto="create|source"`
  or `"source"` in `apps/mise/files/config.toml`).
  **Premise suspect, 2026-09-23; refined 2026-09-28:** the key is in no
  tracked file, and `mise settings get python.uv_venv_auto` returns `false`
  on the Linux box — yet `mise ls` and `mise settings` DO still emit the
  `python.uv_venv_auto=true is deprecated` warning. So the `true` value is
  injected from somewhere unseen (a settings file, env var, or default),
  while `settings get` reads a different layer. Track down the source before
  acting.

- **Stop repo tooling leaking into `$HOME`.** `chezmoi managed
  --include=files` on 2026-09-23 (700 paths) lists `docs/LANGUAGES.md`,
  `docs/GLOSSARY.md` and `docs/WORKTREES.md` (→ `~/docs/`); `scripts/`, 3
  hook scripts (→ `~/scripts/`); and two `bin/` strays,
  `executable_archive.bk` and `executable_READMD.archive.md`. `tools/` (9
  files → `~/tools/`) belongs to the skill-trust install task. The guard's
  `GOVERNANCE_FILES_IN_DOCS` also omits `docs/LAYOUT.md`, ignored in
  `851a419` but unguarded. `docs/ARCHITECTURE.md` and `docs/USAGE.md`
  deploy on purpose. Until the guard sees worktrees (§ Now #1 (p) P2a),
  check fixes from the main checkout. Done when each leak is ignored,
  deleted or recorded as deliberate, and the guard lists every ignored
  convention doc. The `.chezmoiroot` item in `ROADMAP.md` would end this
  class of leak.

- **Build the subscription machinery: `topic_subscribes` + playbook
  resolution + injection.** The mechanism half of the adopted system-config
  model (resolved council entry, `TASKS-RESOLVED.md` 2026-09-17): a topic
  declares `topic_subscribes: [<catalogue>]` in `topic.yml`; the parent
  playbook validates each subscribed catalogue exists as
  `dotfiles/config/<catalogue>.yaml` (unknown catalogue fails loudly naming
  both sides), resolves each subscriber's slice — entries matching that
  consumer, availability verdicts applied — and injects it as a var;
  topics carry only a thin install-and-report loop over the list they were
  handed, so unresolvable verdicts fail at the playbook layer before
  anything installs. Resolution lives in `roles/`, per the
  `roles/topic-resolution` precedent (playbook pre_task logic extracted
  2026-09-15 so the playbook stays readable and the logic is testable —
  `tests/topic_resolution/` is the shape to follow). **Gated on the
  normative topic spec landing first** — the subscribes key is `topic.yml`
  schema the spec governs — and on the catalogue seed in § Now. Tests
  first and mutation-proven per `spec.md` § Verification; the resolution
  filter is pure set/merge logic, so it takes a property test. Done when
  resolution is tested, the playbook fails loudly on an unknown catalogue
  or an unresolvable verdict, and the injected-var contract is documented
  in `dotfiles/docs/TOPICS.md`. [me]
- **Switch the visual-studio-code topic from the interim direct read to
  playbook injection.** The topic is already wired (2026-09-17, § Now):
  install/remove/upgrade consume `config/editors.yaml` through a
  role-relative direct read with the thin loop and gated teardown. When
  the subscription machinery above lands, replace the direct read with
  `topic_subscribes` + the injected slice — behavior must not change, and
  the switch is proven by being a no-op on the converged machine. Done
  when the direct read is gone, `--check --tags provision` still converges
  (changed=0), and the topic's CHANGELOG records the switch. [me]
- **Wire the cursor topic and align it with the catalogue contract.** Same
  contract as vscode: thin loop, gated `cursor_remove_extensions`,
  currency — wired interim by direct read like vscode, switching to
  injection when the machinery lands. The first real run settles the
  pylance-class verdicts live and exercises the `substituted` tolerance
  for `anysphere.cursorpyright` (probe evidence in the topic's CHANGELOG;
  its catalogue entry sits in `editor_extensions_ignored`). Done when
  `run-role.sh cursor` converges from the catalogue (author applies),
  verdict lines print per entry, and the topic's CHANGELOG records the
  contract. [me]

- **Decide whether to add the `opencode-sentry-monitor` plugin to the
  `apps/opencode` topic, and if so how.** Queued 2026-09-16 from the author's
  request, which the agent stopped on. The npm package (MIT, v0.1.7,
  `opencode-sentry-monitor`, by Scott Tolinski) is an OpenCode plugin that
  captures session lifecycle, tool-execution spans, and token usage, and by
  default also tool inputs/outputs and model request/response text
  (`recordInputs`/`recordOutputs` default `true`), then ships them to a Sentry
  project. That is an egress path, and `dotfiles/policy/ethics.yaml` forbids
  egress that is automated end-to-end or bypasses human review
  (`egress.may_be_automated_end_to_end: false`,
  `egress.may_bypass_human_review: false`) while `spec.md` § Policy requires
  every sending tool to consult `policy check` and treat unknown as denied. A
  third-party plugin cannot call the resolver. **Do not add it without the
  author's explicit decision — the telemetry is the whole question.** If
  approved, the shape is an npm entry in `apps/mise/files/config.toml` plus a
  `plugin` entry in `dot_config/opencode/opencode.jsonc.tmpl`, with the egress
  override recorded as an author decision and the recording flags settled.
  Done when the author has answered and the answer is recorded or the plugin
  is wired. [me]
- **Make opencode permission rules deterministically editable, per config
  (project or global).** Queued 2026-09-16 as the other half of the
  permission fix. Hand-editing the JSONC is error-prone in a specific,
  demonstrated way: opencode matches the **last** rule (`evaluate` uses
  `findLast`; `fromConfig` keeps declaration order), so a trailing
  `"*": "ask"` silently shadows every allow above it and every `deny`
  carve-out anchored below it. The global config shipped that bug until
  2026-09-16 — `git`, `find`, `wc` and `echo` were declared but inert, and
  `find . -delete` fell through to `ask` instead of the intended `deny`. The
  tool must read and write JSONC without dropping comments or reordering
  keys; set or update a rule in a named config (a project `opencode.json`, or
  the global `~/.config/opencode/opencode.jsonc`, which here is a chezmoi
  templated source); normalise the ordering invariant (catch-all first,
  carve-outs after the allow they narrow); and report the merged effect of
  global + project rules for a command, since the scopes deep-merge and the
  project scope wins. **Not the right place to build this now.** It is a tool
  build (AGENTS.md ladder, so route before writing code), it belongs with
  `topical` — the CLI the ROADMAP gives the "abstracts configuration
  management and updates" job, itself scheduled A1–A7 and unlanded — and it
  depends on `apps/opencode` owning its own config (the integrations-phase
  task in § Now) and on the tooling destination (ai-prompt-library /
  llocallabs, per the move manifest). If that route is declined, say so in
  this line rather than starting a script here. Done when the destination is
  decided and a command idempotently updates a named opencode config's
  permission rules, preserves the file's comments and key order, enforces the
  ordering invariant, and is proven by a test that catches a reintroduced
  trailing catch-all. [me]
- **Design the replacement for the TASKS.md state-and-handoff process.** The
  queue has become a second codebase: a handoff snapshot two machines rewrite
  under each other (the 2026-09-14 merge conflict was predicted and then real),
  resolved tasks with no home (the stopgap `TASKS-RESOLVED.md` exists for
  exactly that), claims, hazards, standing reminders, and five governance docs
  all pointing at each other. Design what replaces it — what state lives
  where, how two machines merge without hand-reconciling prose, how resolution
  is recorded without growing a second file — and get the author's approval
  before cutting TASKS.md to match. Done when a written design exists, the
  author has approved it, and the re-cut file (or its successor) passes
  `tests/tasks_doc` with the resolved-tasks stopgap retired. Handoffs get an
  advisor review before taking effect — the 2026-09-14 review ran with the
  producing agent alone, exactly the self-certification the panel-of-judges
  item warns about — so the design must make the advisor pass real rather
  than optional. **Advisor pass v1 has now run** (2026-09-15): three
  fresh-context subagents — records auditor, red-team critic, cold-start
  usability — reviewed the session's records and decisions; intra-model by
  weights, independent by context and brief, and it caught real errors the
  self-review missed (a wrong diagnosis, an asymmetric routing test, a
  bypassed verification standard). Findings are applied or queued in this
  file. The design must still supply an independent-model pass and must NOT
  pre-commit whether multi-agent review beats self-review — that is the
  panel-of-judges research's measured question. [me]
- **Research agent sandboxing for projects and user tasks on this machine —
  deep research, debated with a council of advisors, delivered as a two-phase
  project with a spec binding them.** The permission tiers in
  `docs/PERMISSIONS.md` gate what tools agents may run but do not isolate
  what a permitted tool can touch — sandboxing is the layer they cannot
  provide. **Phase 1 — requirements.** Write the spec: what is being
  sandboxed (agents working in project directories, agent-driven user tasks
  on the machine), against which threats (egress, writes outside declared
  scope, credential access, machine-config mutation), under which constraints
  (macOS and Debian targets, one machine-management repo, the existing
  `bin/policy` boundary model, agents never applying chezmoi). Debated with
  the council before the author approves it. **Phase 2 — apply.** Update the
  spec with what the research taught and land the background knowledge where
  it is consumed: `bin/policy` boundary keys, the agent permission layers,
  and topic/machine configuration — as queued tasks citing the spec, never
  implemented silently. Initial leads, author-provided 2026-09-14, fetched
  and verified that day: wincent's "Coding Agent Sandboxes — Comprehensive
  List", a taxonomy from OS primitives to policy layers
  (https://gist.github.com/wincent/2752d8d97727577050c043e4ff9e386e);
  "Sandboxing AI coding agents with Lima", VM-grade isolation with
  near-native UX, naming egress and forwarded secrets as the unsolved gaps
  (https://bogoyavlensky.com/blog/sandboxing-ai-coding-agents-with-lima/);
  and `nono`, least-privilege per-agent and per-tool sandboxes with a
  credential proxy and L7 filtering, Apache-2.0, from the Sigstore team
  (https://github.com/nolabs-ai/nono). The council debate pairs with the
  panel-of-judges item below — settle that first or borrow its method.
  Lead from the second research capture (2026-09-14,
  `~/code/personal/llocallabs-capture/`): Omnigent —
  **[verified]** Apache-2.0 and active — claims bubblewrap (Linux) /
  Seatbelt (macOS) sandboxing with cost tracking across agent CLIs.
  **A lead, not a selection** — the capture's other options were routed by
  subject and verification: nono and Lima remain the primary leads
  (capture #1); Caliber generates config rather than sandboxing (its own
  evaluation task); AgentMD is a claimed-frozen spec; OpenCtx is archived
  in favour of MCP; ctx-open is unlicensed and stale (reference only);
  Backlog.md and `handoff` are session-state tools (routed to the
  session-management research); Podman-on-macOS is a constraint input, not
  a candidate. Verification so far is first-order only — existence,
  licence, activity; Omnigent's enforcement claims and its claimed
  Databricks backing are UNVERIFIED and come from the same AI-generated
  source that produced the Caliber npm-scope discrepancy.
  **Post-advisor demotion:** the routing test was applied asymmetrically —
  Omnigent's own description is orchestration-first with sandboxing as one
  feature, so it fails the same subject test that excluded Caliber. Treat
  it as contextual reference for the debate, not a peer lead, and note the
  lead-admission bar silently moved from author-provided to capture-sourced:
  capture-sourced leads need deeper verification before entering the
  council debate. The Podman-on-macOS constraints (hidden Linux VM, nested-virtualization
  limits, network rules applied inside the machine rather than the host)
  still stand as phase-1 requirements for the macOS target. Lead from the
  author 2026-09-15, verified same day: `opencodebox`
  (https://github.com/fityannugroho/opencodebox) — MIT, a bash wrapper
  running opencode inside a bubblewrap sandbox with namespace isolation,
  read-only system mounts, per-project read-write binds, a seccomp filter
  for recent socket CVEs, and refusal to run from sensitive dirs.
  **Linux-only** (bubblewrap needs Linux namespaces), so it is a Debian-side
  candidate, not a macOS answer — and a concrete reference for the
  per-project bind-mount shape on that target. Small and new (3 stars, 34
  commits): first-order verification only, like the other capture-sourced
  leads. Done
  when the phase-1 spec exists, the council debate is recorded, the author
  has approved the requirements, and phase 2's changes are queued rather
  than imagined. [me]
- **Research agent session management and inter-session handoff — deep
  research with expert involvement at both ends: shaping the questions, then
  debating, reviewing and critiquing the author's ideas.** The motivation is
  this repo's own pain: a handoff snapshot two machines rewrite under each
  other, sessions keeping private in-memory queues, a stopgap archive for
  resolved work, and the TASKS.md process-refactor design queued above —
  this research feeds that design. Author-provided starting point
  (2026-09-14, verified): the video "/handoff is my new favourite skill"
  (https://www.youtube.com/watch?v=dtAJ2dOd3ko); the author's accompanying
  skills links were shared as a YouTube redirect to
  `https://aihero.dev/s/YL1zWx`, which 404s — re-fetch or re-share before
  relying on it. A second research capture the same day supplies candidate
  tools to evaluate rather than rediscover: Backlog.md (**[verified]** MIT,
  active — git-native tasks with a drafts→tasks promotion flow and MCP
  exposure), the `handoff` CLI's six-file `.handoff/` session-state layout,
  the `.context/` directory convention, and ctx-open (**[verified]**
  unlicensed and four months stale — design reference only under
  absent-is-not-permissive); raw material in
  `~/code/personal/llocallabs-capture/2026-09-14-agent-tooling-research.md`. The
  research learns the process and approaches first; the
  council's role is two-sided: weigh in on WHAT the deep research should
  ask, then debate, review and challenge the author's candidate ideas with
  critique before any task is cut. Done when the findings exist, the
  council's question-shaping and critique rounds are recorded, and — with
  the author — a decision is made whether to queue configuration tasks for
  AI and agents here, which would touch AGENTS.md § Working alongside other
  sessions and the TASKS.md process design. [me]
- **Research RAG and knowledge graphs for preprocessed agent context —
  deep research with expert involvement at both ends, same pattern as the
  sandboxing and session-management projects.** The problem: knowledge the
  agents rely on — this repo's governance docs, the policy layers,
  dependency research, eval histories — is reprocessed from raw tokens
  fresh in every session, expensive and bounded by context limits.
  Preprocessing it into well-structured, fetchable context (retrieval,
  graphs, or whatever the research supports) trades a one-time build cost
  for a per-session saving. Learn the approaches first; the council shapes
  what the deep research asks, then debates and critiques candidate designs
  before anything is built. Any build is a llocallabs candidate — it is AI
  tooling — while the consumption points are here and in the llocallabs
  agent. Pairs with the `agentic-context-engineer` role queued in § Now,
  the hand-rolled ancestor of the same idea. Done when findings exist, the
  council rounds are recorded, and — with the author — a decision lands:
  adopt, adapt, or reject, with any follow-on tasks queued citing the
  findings. [me]
- **Verify and evaluate Caliber (`caliber-ai-org/ai-setup`) as an
  agent-config generator.** Lead from the author's research capture,
  2026-09-14, raw paste preserved at
  `~/code/personal/llocallabs-capture/2026-09-14-caliber-ai-setup.md`: a
  MIT-licensed CLI that scans a codebase locally and generates agent config
  files (AGENTS.md, .cursor/rules, CLAUDE.md), claiming a generic mode,
  BYO-key deep generation, and opencode/dotagents compatibility. The
  capture is an AI-generated summary — **UNVERIFIED**, and the
  load-bearing claims are exactly what `review-best-practices` exists to
  check: the local-vs-API split, the npm scope (`@rely-ai/caliber` in the
  paste vs `caliber-ai-org` on GitHub — one is wrong), the claimed
  `.skill.md` export for dotagents, and — decisive for this repo — whether
  it overwrites or respects an existing hand-maintained AGENTS.md, which
  would disqualify it here while leaving llocallabs's scaffold as a
  legitimate consumer. Second capture, same day: the npm scope is explained
  as the **for-profit entity behind the tool** (`@rely-ai`, enterprise
  portal at trycaliber.ai with a sales desk) — so the scope mismatch is an
  open-core-trajectory question to track, not just a typo; `caliber
  refresh` drift protection via pre-commit hooks and MCP recommendations
  are further claims to check. **[verified 2026-09-14 via `gh api`: MIT,
  not archived, but last push 2026-07-26 — ~7 weeks stale by the 30–45-day
  maintainership criterion.]** Coupling: the general copier template queued
  below generates the same class of files, so this evaluation answers for
  both. Done when the claims are checked against the actual repo, a
  use/don't-use decision is recorded with the author, and any adoption is
  queued as tasks. [me]
- **Create a `git` topic that owns git config and extensions; git-ai is its
  first extension.** Git config is not managed at all today — no
  `dot_gitconfig` in the source, no `apps/git` topic — and the git-ai
  installer's edits are hand-placed: a `~/.gitconfig` written 2026-09-13
  (plain file, unmanaged), the `~/.git-ai/bin` PATH export appended to
  `~/.zshrc` (the one two-way-drifted file), plus any hooks or bin entries it
  installed. **Machine-stamped:** that installer ran on the *second machine*
  — this Mac has no `~/.git-ai` and no git-ai block in `~/.zshrc`
  (verified 2026-09-15), so the audit starts there, not here. Audit everything the installer touched first, then build
  `dotfiles/apps/git/`: it owns the gitconfig as a chezmoi template where
  machine-specific, installs extensions as declared dependencies rather than
  curl-installers, and carries the shell integration the installers keep
  hand-appending — the PATH line moves into the topic's shell-integration
  fragment (or `zsh/path.zsh` if it stays a zsh concern), never the deploy
  target. This supersedes the earlier zsh-fragment framing: git-ai is a git
  extension and belongs beside git config, not scattered into zsh.
  **Open research question — settle before writing install tasks:** is git-ai
  provisioned machine-globally, or per project? Per-project config on this
  machine lives exclusively in the mise `config.toml` files at each project
  root, so a per-project answer must route through that file (mise
  `[tools]`/env/tasks) rather than a global gitconfig hook. Research what
  git-ai actually scopes — global hook, per-repo config, PATH shim — and what
  mise's per-project config can express, then take the decision to the author.
  The answer decides what replaces the installer's hand edits. Until it
  lands, a full `chezmoi apply` would delete the installer's lines from
  `~/.zshrc`, so apply everything else selectively (`chezmoi apply ~/dotfiles
  ~/.config/opencode ~/tools`) and leave `~/.zshrc` out. Done when `apps/git`
  installs cleanly on this machine, git-ai works from a fresh shell with no
  hand-edited line left in `~/.zshrc`, `diff <(chezmoi cat ~/.zshrc) ~/.zshrc`
   no longer shows the git-ai block, and the live `~/.gitconfig` is the one the
   topic owns. [me]
- **Study `pkgup` and turn its migration to the topic format into a queued
  collection of tasks.** The script is not in this repo — it is the Debian
  box's package updater (nothing named `pkgup` in the source, `~/bin`, or the
  zsh fragments on this Mac; the macOS sibling here is `~/bin/upgrade-all.sh`,
  which orchestrates `softwareupdate` and `brewup.sh`). The study is the
  initial task: read the script where it lives, inventory every package
  manager it drives, compare each against the existing topics (`apps/apt`
  exists; brew's upgrade path lives in the homebrew topic), then queue one
  migration task per manager or coherent clump — each in the topic format
  with `topic.yml`, the install/upgrade/remove lifecycle, and a per-topic
  test suite. **[blocked: root-level become permissions — an unattended
  topic cannot run apt until the dedicated-ansible-user task's sudoers grant
  enumerates the package-manager commands; do that privilege work first.]**
  Done when the collection is queued in TASKS.md, each task names its
  manager, its topic home and its teardown, and any non-manager logic left
  in the script has an owner or a retirement note alongside A10's `~/bin`
  sunset. [me]
- **Harden cosine beyond the subnormal guard: the overflow tail and scale
  invariance.** The advisor pass found what 6c3079b's guard missed. Two
  tails: an overflow tail where sums overflow to inf and the quotient
  becomes NaN — and the coverage classifier counts NaN as classified
  (`nan < args.min_margin` is False), the exact "unknown becomes a claim"
  shape; and the guard breaks scale invariance (parallel tiny vectors score
  0.0), which no property test pins and which the centroid classifier hits
  for near-centroid prompts by construction. Candidate fix: max-abs
  pre-scaling (preserves invariance, fixes both tails), plus a
  scale-invariance property, a NaN-cannot-classify assertion, and an eval
  case pinning near-centroid behavior. Done when the properties exist, the
  counterexamples are pinned, and the mutation check shows the old guard
  failing them. [me]
- **Decide the capture-store contract: private/shareable separation,
  versioning, retention.** The llocallabs capture store
  (`~/code/personal/llocallabs-capture/`) is cited by five tasks as
  evidence, is unversioned and single-machine, and sits in one directory
  with private career notes — one careless copy puts private content in
  files future sessions are instructed to read. Decide: separation (a
  private/ subtree or a separate store), versioning or sync for cross-machine
  cluster work, retention and backup (feeds the backup-design item). Done
  when the contract is written, the author has approved it, and the store is
  reorganized to match. [me]
- **Run the lessons-learned advisor pass — captured 2026-09-15, deliberately
  not run to completion in its originating session.** The question: how to
  capture lessons from sessions, author-side (decisions, corrections, the
  30–60 second capture problem) and agent-side (the primary session and its
  advisor roles), such that they survive and become durable mechanisms. The
  complete advisor tasking — the ask plus two verbatim briefs (a designer
  and a red-team critic) and launch instructions — is preserved at
  `~/code/personal/llocallabs-capture/2026-09-15-lessons-learned-advisor-briefs.md`.
  A prior same-day run exists beside it as two per-brief files
  (`...prior-run-designer.md`, `...prior-run-redteam.md`, written by the
  advisors themselves): the re-running session runs the briefs FRESH and may
  use the prior output for comparison or ignore it — never as an anchor.
  Triage every finding through AGENTS.md § Observations are deliverables:
  edit the mechanism, queue a task with a done-condition, or drop. Feeds
  the R&D factory stage one and the session-management research — do not
  build a parallel system beside them. Done when both briefs have been
  re-run fresh, the findings are triaged with the author, and any mechanism
  edits are queued or landed. [me]
- **Extend `tests/tasks_doc` to fail on referenced paths that do not exist.**
  The advisor pass found dangling references a validator would catch
  mechanically: `run-role.sh` unprefixed in AGENTS.md, `machines.yml`
  described as existing when it was a design, `.chezmoiignore` line-number
  decay, a task line naming one file twice where two were meant. Scope:
  parse backtick-quoted repo-relative paths and check existence; fail on
  section-heading mismatches. Done when the validator catches a deliberately
  planted dangling path (mutation-checked). [me]
- **Bring the portable half of `~/.claude/` under chezmoi.** Deferred from the
  claude-code topic (`c988fef`), which owns the binaries and deliberately left
  config alone. Nothing there is versioned today, so user-global settings do not
  survive a machine. The work is the split, not the plumbing: `settings.json`,
  `CLAUDE.md`, `agents/` and `commands/` are portable, while `history.jsonl`,
  `projects/`, `session-env/`, `daemon/`, `backups/`, `file-history/` and
  `~/.claude.json` are machine-local and must never be committed — the last of
  those holds credentials. chezmoi owns the files once split, per the layering
  rule in `AGENTS.md`; the topic does not template them. Two hazards worth
  knowing before starting: the VS Code extension, the JetBrains plugin and the
  desktop app all write `~/.claude/`, so the directory is not Claude Code's
  alone; and `apps/opencode` already owns `~/.agents/skills` via dotagents,
  which Claude auto-loads, so nothing here may write skills. Done when the
  portable files deploy from the chezmoi source on a fresh machine, `chezmoi
  status` is clean afterwards, and no machine-local state or credential has
  entered git.

- **Extend `apps/claude-code` to Debian via the signed apt repository.** The
  topic is `topic_os: [Darwin]` because Homebrew casks are macOS-only, so the
  Debian box has no managed Claude Code at all. Upstream publishes a signed apt
  repo rather than expecting the native installer: keyring at
  `/etc/apt/keyrings/claude-code.asc`, fingerprint
  `31DDDE24DDFAB679F42D7BD2BAA929FF1A7ECACE`, and — the part that bites — both
  the URL path *and* the suite name change between channels
  (`.../apt/stable stable main` versus `.../apt/latest latest main`), so
  `claude_code_cask`'s stable/latest choice needs a Debian equivalent rather
  than reuse. Needs `become: true` for the keyring and sources file, which no
  part of this topic currently requires. Note apt installs do not auto-update
  through Claude Code either, so currency still comes from the system upgrade
  pass. Done when the topic flips to `[Darwin, Debian]`, installs on the Debian
  box with the key verified before use rather than trusted blind, and
  `--tags remove` takes the repo file and keyring back out.

- **Extract the model benchmarking and scouting tools into their own repository.**
  Near-future and deliberate, not urgent — recorded now so it does not happen by
  accident. `bin/model-bench` is 1357 lines and `bin/model-scout` is 379, plus
  `apps/ollama/files/ollama-bench` and `ollama-evals`; that is a model
  evaluation toolkit living inside a machine-provisioning repo. It is also the
  clearest case of the `AGENTS.md` ladder: AI work belongs outside this repo,
  and benchmarking models is not configuring a machine. Same destination shape
  as `topical` — its own repo, installed back here as a normal tool by a thin
  topic, rather than vendored. Two things to settle before moving: the tools are
  referenced by name in `.claude/settings.local.json` allowlists and in launchd
  labels (`com.ollama-usage.snapshot`), so this shares the audit in A10 above;
  and `ollama-evals`/`ollama-bench` are topic-owned while the `bin/` pair are
  not, so the split is not along one clean line today. Done when benchmarking
  lives in its own repo, this repo installs it like any other tool, and nothing
  here imports it.
- **Create the `worktrunk` topic — the `wt` Git-worktree manager, installed
  via mise.** Parked by the author 2026-09-21 (write-and-forget, unassigned
  backlog). Binary through the mise `github:` backend per the
  `apps/mise/files/config.toml` convention (never `ubi:`); the mise registry
  entry is verified live — `mise ls-remote worktrunk` resolves through 0.79.0
  (checked 2026-09-21). `topic_requires: [mise]`, scaffolded per
  `dotfiles/docs/TOPICS.md`; settle the two chooser questions first (which
  machines run it, who upgrades — `dotfiles/docs/TOPIC-RECIPES.md`
  install-mechanism chooser) and apply the test-first recipe. [unassigned]
- **Add voice-typing topics: `apps/openwhispr` and `apps/superwhisper`, macOS
  first, with a Linux path that is not a cask.** Both exist as casks, verified
  2026-09-14: `openwhispr` 1.10.1 ("Privacy-first voice-to-text dictation with
  AI agents", open source, `OpenWhispr/openwhispr`) and `superwhisper` 2.18.3
  ("Dictation tool including LLM reformatting", commercial, macOS >= 14). Both
  declare `auto_updates`, so brew's recorded version drifts — the same
  `known_issues` entry `apps/claude-code` already carries for `Claude.app`.
  Start on Darwin because that is where the casks work; casks are macOS-only, so
  Debian needs a different mechanism and the honest first step is `topic_os:
  [Darwin]` rather than a half-built conditional, exactly as `apps/claude-code`
  did. For the Linux path, `whisper.cpp` is a cross-platform **formula** and is
  the likely base — note the handoff's "SoupaWhisper" sketch is essentially that.
  **An external briefing document exists for this work — not the session handoff
  above — and it does not describe this repo.** It assumes topics named `git/`, `zsh/`, `wayland/`, `macos/` and
  an `openrouter/` topic; this repo has Ansible roles under `dotfiles/apps/` with
  a fixed lifecycle, no `wayland` or `macos` topic, and OpenRouter reached
  through `apps/ori`. Translate it, do not follow it literally. What does carry
  over, and is worth keeping:
  - **No hardcoded credentials.** It wants `$OPENROUTER_API_KEY` from the
    environment rather than baked into a config file. That already matches
    practice here — `llm-openrouter` and `ori` both read it — and
    `AGENTS.md` § "Machine-specific values are resolved, never written out" is
    the rule it is reaching for.
  - **Wayland cannot be assumed.** Its text-injection rules (`ydotool`/`wtype`,
    `wl-clipboard`, adding the user to the `input` group for `/dev/uinput`)
    presuppose a Wayland desktop. **Verify the Debian box actually runs one
    before building any of it** — that is unconfirmed, and the whole Linux
    design rests on it.
  - **Hotkeys belong to the compositor, not the app**, with macOS parity via an
    Apple Shortcut or Automator action calling the same CLI. That shape is
    sound; it needs a real toggle command to exist first.
  **OpenWhispr on Linux is required, not optional** — Darwin-first is about
  sequence, not scope, and this one has to run on the Debian box too. Research
  it properly rather than assuming the cask story carries over; upstream already
  ships for Linux, verified 2026-09-14 against release `v1.10.1`:

      OpenWhispr-1.10.1-linux-amd64.deb        ← apt, matches apps/apt + become
      OpenWhispr-1.10.1-linux-x86_64.rpm
      OpenWhispr-1.10.1-linux-x86_64.AppImage
      OpenWhispr-1.10.1-linux-x64.tar.gz       ← tarball, the apps/ollama shape

  MIT, Electron, actively released. Prefer a package manager over a bare
  download — but note these are the *same* mechanism here, not alternatives:
  `ansible.builtin.apt` takes a `deb:` parameter and downloads it itself when
  given a URL, so "install via apt" and "fall back to the .deb" collapse into
  one task pointing at the release asset. Check first whether upstream publishes
  an actual apt *repository*, which would be better still since it makes
  upgrades ordinary; nothing in the v1.10.1 release assets suggests one, but
  that only rules out the release page. The tarball is the last resort and
  matches how `apps/ollama` already installs on Linux.

  **Architecture is confirmed: the Debian box is x86_64/amd64**, stated by the
  author 2026-09-14, so OpenWhispr's Linux builds apply and the `.deb` path
  stands. Worth keeping in view anyway, because it nearly went the other way:
  every OpenWhispr Linux artifact is x86_64 and there is **no arm64 Linux
  build**, while macOS ships both. Adopt the habit rather than the one-off
  answer — **check a release's actual architecture list before choosing a
  package format**, and prefer reading upstream's published metadata over
  assuming parity with macOS. `apps/ori` already does the honest version of
  this, resolving `arm64` vs `x64` from `ansible_facts` and verifying against a
  published `SHA256SUMS`. Second, the release carries
  `latest-linux.yml`, which is electron-updater metadata: the app self-updates,
  so it has the same two-owners question `apps/claude-code` answered for the
  desktop cask, and the answer has to be deliberate rather than inherited.

  Done when OpenWhispr installs, removes and upgrades cleanly on **both** this
  Mac and the Debian box — or, if the architecture rules it out, when that is
  recorded with the `whisper.cpp` alternative chosen — and superwhisper's
  Darwin-only status is stated as a decision rather than an omission.
- **Explore OpenTypeless before committing to it.** Named alongside OpenWhispr
  in the voice-typing handoff but not evaluated. Nothing is known here about its
  licence, its config format, whether it packages for macOS or Linux at all, or
  whether it duplicates what OpenWhispr already does. Deliberately an
  exploration, not an install task — `review-best-practices` is the shape, and
  the output is a recommendation with what was rejected, not a topic.
- **Give privileged topics a dedicated ansible user per environment, and a
  service that runs configuration updates.** Today the five apt-using topics
  (`docker`, `clamav`, `lynis`, `mise`, `ollama` — the only `become: true`
  topics, per `dotfiles/managers.yaml`) escalate through whoever happens to be
  running the playbook, which means an unattended update is impossible and an
  attended one carries the human's full sudo rights. A dedicated account fixes
  both: the service has an identity, and its powers can be smaller than a
  person's.
  **Scope the privileges before building anything.** A service that can apply
  machine configuration unattended is a standing grant, not a convenience — the
  sudoers entry should enumerate the specific commands the playbook actually
  needs rather than `NOPASSWD: ALL`, and `dotfiles/managers.yaml` already names
  which managers need escalation and which do not, so the list is derivable
  rather than guessed. `docs/PERMISSIONS.md` is the relevant prior art and is
  blunt that this layer stops accidents, not a misaligned or prompt-injected
  agent; a scheduled runner with root is exactly the thing that document warns
  is not contained by permissions. Decide deliberately whether the service ever
  runs agent-authored changes, or only reviewed ones.
  Per environment, because the two boxes differ: launchd on Darwin, systemd on
  Debian. Both have precedent here — `apps/ollama` installs a launchd agent and
  `apps/clamav` a systemd timer — so this is a new user and a new unit, not a
  new mechanism. Done when each machine has an ansible user whose sudo rights
  are enumerated and reviewable, a scheduled unit that applies configuration and
  reports what it changed, and a documented way to run it by hand.
- **Bootstrap a whole machine from chezmoi alone, including Ansible itself.**
  Later, deliberately. chezmoi ships as a self-contained static binary with no
  runtime, which makes it the one thing that can be present before anything else
  is — so `chezmoi init --apply <repo>` could pull the configuration *and* stand
  up the system dependencies it needs, rather than the current order where
  Ansible must already exist for the playbook to run. That removes the
  chicken-and-egg step in `bootstrap/` and shortens a new machine to one
  command. Worth checking before designing: chezmoi's `run_once_before_` scripts
  are the hook for this and already appear in the repo
  (`crontab/run_onchange_after_install-crontab.sh.tmpl`), so the mechanism is
  known rather than novel. The interesting question is what minimum must be
  bootstrapped — mise brings Ansible today, and mise itself has to arrive
  somehow.
- **Write a `ground-truth-a-dependency` skill from scratch.** The recurring need
  is what the 2026-09-12 dotagents failure took: reading a dependency's shipped
  source to find behaviour its docs never mention — an uncaught `SymlinkError`
  reaching stderr while stdout stayed empty. The method used that day is the
  whole content and owes nothing to any employer artifact: read the installed
  package rather than trusting docs, reproduce in an isolated `HOME` before
  believing a diagnosis, and mutation-test the resulting guard so a test that
  cannot fail is caught. **`what-would-kobby-do` is not a source** — it is an
  unlicensed internal tool, so it may not be read, quoted, paraphrased or
  "generalised". Name the skill for the work, not "reverse engineering", which
  drags in binary analysis and a legal frame that does not apply. Done when it
  takes an undocumented dependency failure to a cause with every claim tied to a
  file and line, authored in a session where the exclusion list below was in
  force.
- **[1] Promote `gpt-oss:20b` and `ministral-3:8b` in `bin/binned`.** Decided:
  use the cross-task evidence from judging. Record in the manifest that the
  number came from judging rather than generation, so the basis is not
  rediscovered as an error later.
- **[2] Repopulate `bin/binned`'s SaaS tier from the frontier evaluation.**
  Decided: repopulate rather than leave it thin. Depends on the frontier
  evaluation task, which needs OpenRouter calls and therefore an answer on cost.
- **[5] Give Ansible sole ownership of `_ollama_zsh_completion`.** Decided.
  chezmoi was involved because the file is a symlink; removing chezmoi's claim
  ends the dual ownership and the `chezmoi apply` reverts-a-re-download
  consequence documented in `apps/ollama/tasks/install.yaml`. Note the
  inversion while working: for this file the topic-root copy is live and the
  `files/zsh/` copy is dead, backwards from every other `*.zsh`.
- Evaluate frontier cloud alternatives to OpenAI/Grok as judge and generation
  candidates — Qwen, DeepSeek, Moonshot Kimi, Z.ai GLM, MiniMax, Mistral,
  ByteDance Seed, Cohere are all on the existing OpenRouter account. Rank them
  with `model-bench`, not by assertion: several post-date any model's training
  cutoff, so relative quality is genuinely unknown until measured.
- **Retired 2026-09-12 — do not hand-symlink skills into `~/.claude/skills`.**
  `apps/opencode` now declares `pii-redaction`, `commit-hygiene`,
  `review-best-practices`, `interaction-questioning` and `skillet-authoring` in
  its manifest, and dotagents installs them into `~/.agents/skills`, which
  `~/.claude/skills` is now a symlink to. The hand-made links were not merely
  redundant: they were the direct cause of the `dotagents add` failures on
  2026-09-12 (see `roles/guards/tasks/dotagents-skills-migration.yaml`), and
  dotagents silently replaces any it finds at the destination. If a skill really
  should point at a live working clone, declare it `path:.agents/skills/<name>`
  so dotagents adopts it in place — never `ln -s` by hand. `model-fitness` stays
  out: it is uncommitted in ai-prompt-library and belongs to another session.
  `no-ai-slop` remains a third-party vendored copy rather than a manifest entry:
  `gh api repos/petergyang/no-ai-slop/contents/skills/no-ai-slop/SKILL.md
  --jq .content | base64 -d`. See its `PROVENANCE.md` for the em-dash deviation.
- File the upstream issue on `simonw/llm-pdf-to-images`: it does `import fitz`,
  and PyMuPDF's shim prints a deprecation notice to **stdout**, corrupting any
  captured `llm` output. Draft is written; one-line fix is `import pymupdf`.
  **[unblocked: `gh auth status` reports a working keyring login as of 2026-09-11]**
- Move § Commit granularity and § Messages out of
  `dotfiles/docs/TOPICS.md` into `docs/COMMITS.md`. That document is
  titled "Topic conventions" and those two sections are not topic conventions —
  they are repository conventions that do not ship with the artifact, which is
  the split `docs/TOPICS.md` now describes. `AGENTS.md` § Commits cites
  them and would point at the new home.
  **Do it with the citation rewrite, not before.** 53 files reference
  `TOPICS.md`, 40 of them topic files using a deployed-tree-relative path,
  and those citations should be rewritten once rather than twice.
- Scope and apply retention to the 8 rows of work content already in the `llm`
  log. `company.yaml`'s `open_questions.indefinite_local_log` defaults to
  `treat_as_non_compliant`, so the current state is the non-compliant one by our
  own reading. Blocked on the resolver only for automation — the rows can be
  scoped by hand first.
- Add tests for `bin/triage`. It has none, which is why a `platform=None`
  reporting bug reached the deployed script and was caught by a manual smoke test
  rather than the 218-test suite. The env/flag/fallback resolution is the obvious
  first case.
- Define how this repo's policy reaches builders, and the save-back contract
  for tool-built policy. The author's requirement (2026-09-12): this repo may
  carry a policy that agents read or are fed; when a policy tool exists
  (impromptu), its output must have a known way to be saved into this
  machine-management repo where retention is wanted — or, if policy lives
  here, the tool takes over managing it. Done when the contract is written
  down: what a builder reads, from where, in what format, and what a tool
  must produce for this repo to retain it. The larger question this sits
  inside — whether over-arching policy is independent of this repo — is in
  `ROADMAP.md` § Over-arching policy and is the author's to settle.
- Run the eval suites for the library skills. **Re-homed 2026-09-12** to
  `ai-prompt-library` (its TASKS.md), per the author's scoping decision: AI
  work — skills, evals, policy, tooling — stops landing in this repository.
  This repo's provisioning (the dotagents topic, the opencode manifest)
  consumes the eval gate's verdicts but does not execute them.
- Evaluate whether contract testing earns its keep here. The candidate seams are
  real: `bin/policy`'s exit codes (0/1/2/3) consumed by several callers, the
  `ollama-evals` case schema shared by 25 YAML files, and the model-manifest
  shape that `sync`/`prune`/`status` all read. Today each consumer re-asserts the
  contract in its own tests, which is the duplication the item above is about.
  Decide: one contract per seam with consumer tests deriving from it, or leave it.
- Decide whether a panel-of-judges (LLM council) pattern earns its keep for work
  on this repo, specifically refactoring review and commit review, where a single
  model's agreement with itself is not evidence. Groupthink is the stated concern:
  one model, or several from one family, will ratify its own reasoning. Measure it
  rather than assume it — disagreement rate between judges is the signal that says
  whether the panel adds anything a single judge did not. Relates to the existing
  cheap-gate item above: the gate decides WHEN to convene a panel, this decides
  WHETHER a panel beats one judge, and they should be settled together.
- Adopt a technical plain-language standard as the default for technical docs in
  this repo, and sweep the existing ones to it. Exempt: `spec.md` and any skillet
  spec, which keep spec language (SHALL/MUST) and BDD scenarios — plain language
  and normative language are different jobs. Applies to `AGENTS.md`, `docs/*.md`,
  READMEs, changelog entries and user-facing output.
  **[open question: which published standard to cite — plainlanguage.gov's
  Federal Plain Language Guidelines and ISO 24495-1:2023 are the two candidates.
  Marked rather than guessed, per `spec.md` § Ambiguity is marked, not resolved.]**
- Reconcile changelog style: plain language, the house commit style in
  `docs/TOPICS.md` § Commit granularity, and the changelog standard have to
  intersect without contradicting.
  **[corrected 2026-09-16: the "no CHANGELOG.md — git log is the changelog"
  premise is stale. The repo adopted scriv (00e278e): fragments live in
  `changelog.d/` and collect into `CHANGELOG.md` on release, per
  `CONTRIBUTING.md` § Writing a changelog entry. Same session observed a
  second gap: sessions intermittently skip fragments — the 2026-09-16 opencode
  permission rework landed 14 commits with none, later backfilled — and nothing
  enforces one. The reconciliation should cover fragment *reliability*, not
  style alone.]**
  **[open question: which changelog standard to cite. `CHANGELOG.md` already
  names Keep a Changelog 1.1.0; `ai-prompt-library/CHANGELOG.md` cites 1.0.0.
  Common Changelog is the other candidate. Confirm which before writing the
  rule.]**
- Reconcile `prek` and `pre-commit`. Both are installed and both read
  `.pre-commit-config.yaml`. Pick one as the documented runner so hooks cannot
  pass under one and fail under the other, and say which in AGENTS.md § Commands.
- Add a pytest hook to pre-commit, or decide deliberately not to. The suite
  takes ~200s measured (215s and 199.5s on 2026-09-22, `-m "not llm_judge"`,
  documented command — the earlier 104s figure could not be reproduced and is
  treated as stale), which is too slow for every commit. **Three-tier design
  settled 2026-09-22 (shift-left study, advisor council, unanimous):** fast
  deterministic hooks only at commit; the full suite as an explicit
  **merge-gate** step, not pre-push — research found a 200s pre-push hook gets
  bypassed by habit within a week, and `--no-verify` silently kills the
  lint hooks sharing that stage too; `llm_judge` tests stay excluded-and-named,
  run by deliberate manual invocation, never in an automatic gate. This
  replaces the earlier "pre-commit fast / pre-push full" framing — pre-push is
  not the gate; the merge is.
- Use local models to generate a machine-local policy layer from on-device
  policy documents. The source documents cannot leave the device, which is
  exactly why a local model is the right tool: it reads them in place and emits
  an abstracted set of principles that the resolver can consume. The generated
  layer is machine-local and never versioned, same as `company.yaml` today.
  Output must be principles, not quotations — a generated layer that reproduces
  source text has moved the document, not abstracted it.
- Design the state backup path, classified by machine ownership and data
  sensitivity. **First slice approved 2026-09-23: BK1–BK4 below cover
  configuration backups**, under `PRD.md` § Configuration backups. They must
  pass their restore drills before real data enters the new machine files.
  The broader state design stays open: identify expensive-to-regenerate
  state (model weights, eval results, benchmark history), apply `spec.md`
  § Data to usage-derived content, and regenerate everything else. The
  configuration exception does not relax the internal-disk rules for other
  data. The AI state-contract item B3 precedes backing up those stores,
  not the machine-file slice. Done when the remaining stores have owners,
  retention rules and permitted destinations, and implementation tasks are
  queued. No backup mechanism has been verified yet. [me]
- Review what may and may not leave a machine the author does not own, against
  the governing policy for that machine. Feeds both the backup design above and
  the generated policy layer. Existing work on this is scattered — collect it
  first rather than restarting.
- Add employer-specific data filters as a machine-local, generated artifact.
  They must never be committed: a filter list names what it is filtering for, so
  a versioned one leaks the thing it exists to catch. Same shape as the
  generated policy layer above.
- Generalise the work/AI policy so topics consume it rather than embedding it.
  Policy governs actions on data — remote inference, body logging, device
  suitability — and those questions do not change when the model runtime does.
  Today `bin/policy`'s FIELDS are already product-neutral, which is the good
  half; the gap is that no topic declares the capabilities it exercises, so
  consumption is by hand at each call site and nothing stops a topic deciding
  for itself. Wanted: a topic declares which capabilities it uses, the resolver
  answers, and adding a second local runtime alongside or instead of ollama
  requires no policy change. Pairs with `spec.md` § Shared code does not assume
  a provider, which states the rule but has no mechanism behind it.

### Gita and machine-file backup — approved 2026-09-23

The author approved the following plan on 2026-09-23. Its goal is one
maintainable Ansible approach to populate and sync each machine's declared
repositories, reporting per-repo problems without stopping other topics.
Work macOS and home Linux keep separate local selections and private data.
The requirements below carry the plan without needing the archival branch.

**Binding execution order:** G0 → (G1 ∥ BK1 ∥ the existing second-machine
inventory) → G2 → BK2 → BK3 → BK4 → **real-data gate** → G3 → G4 → G5 → G7.
G6 may run any time, including alongside G2–G5. G4, G5 and G7 run serially:
all edit the gita upgrade path. The second-machine inventory is the existing
layout task, not another task to create here.

**Real-data gate:** backup is built and tested through BK4 before real data
enters any machine file. Use synthetic files for the preceding format and
restore checks. Seed Linux only after its inventory and this gate; seed the
Mac in a session on the Mac after the gate. Mac-side launchd, Homebrew and
work-1Password behaviour need a session there; Linux evidence cannot prove them.

**Configuration-backup rule:** customer data from a work machine never leaves
that machine and is never on the capture list. Work-derived configuration
lives only in the work secrets manager. Everything else is the author's data
and may be stored off-machine, encrypted. Home `machine.yaml` and
`private.yaml` go to local borg plus a borg host; work-Mac machine files go
only to work 1Password, with no borg or personal backup uploader on that Mac.
Machine-written records are rebuilt, never backed up. This rule is limited
to configuration backups; `spec.md` § Data still binds usage-derived data.
The existing employer-policy review stays open.

Each item has its own branch and review; deployed-tree and policy changes
need PR review. Claim hot files before editing them. Agents never run
`chezmoi apply`. Render Ansible templates for both OS families with
`StrictUndefined`, and run `bash -n` on rendered shell scripts. Prove guards
both decline and relent; record deliberate failures as `Mutation:` and
`Failing-test:` trailers. Keep removal with creation and name untested platforms.

**Open implementation questions from G0b (2026-09-23):** settle these with
the author at the named item, not by silently filling gaps in the handoff.
G2: does no local pick prevent tool installation too, or only repo actions;
which source files are required versus optional? G4/G5: define last good
run independently of exit 0, missing/first-run timestamps, and when
blocked-since resets. G7: does `off` stay off on timers, may timers clone
new explicit declarations, and which type wins for a fork that is also a
template? BK2: what counts as an empty required source? BK1 chooses numeric
retention and backup cadence; the eight-hour schedule belongs to gita.
Permission-work allocation: G2 owns machine-path read denial, BK2 owns
backup-store denial, BK3/BK4 carry it to their destinations. Remote-store
enforcement remains to be designed; the approved policy itself is unchanged.

- **G2 — document and establish the catalogue and machine-file contract.**
  After G1, BK1 and the second-machine inventory, add
  `dotfiles/config/repos.yaml`: personal repos and remotes, one shared set
  initially, with personal discovery sources. Remotes have their own file;
  adding or removing a declaration means editing that file and running the
  topic. This is a distinct catalogue domain with a subscriber and domain
  truth, not data to fold into `editors.yaml` or `agents.yaml`.
  Machine identity is named sets plus an unversioned local pick under
  `~/.local/state/machine/`, never a committed hostname. Split local files by
  what may travel: `machine.yaml` holds set picks, discovery modes and
  schedule; `private.yaml` holds personal private entries; `work.yaml` holds
  work entries and sources. Machine-written sync/discovery records live
  separately from hand-edited files, preserving comments, and are rebuilt
  rather than backed up. Declarations say what should exist; gita and disk
  say what is actually cloned or registered. A machine with no local pick
  gets a report and nothing else.
  Migrate `dotfiles/machines.yml` away from hostnames and update
  `docs/LAYOUT.md` to describe named sets and local selection. Live machine
  files are retained until the machine is decommissioned. Apply the approved
  agent-read denial for `~/.local/state/machine/`, following the
  `~/.local/state/chezmoi/` precedent in `dotfiles/docs/MULTI-MACHINE.md`;
  this permissions change needs policy-path PR review. No real machine-file
  seeding before BK2–BK4 prove backup and recovery.
  Done when the format and a working example are documented, the files
  parse, and no machine hostname values remain in the current tree. This
  hands the file contract to BK2 and, after the real-data gate, G3.

- **G3 — clone missing declarations and adopt existing gita registrations.**
  After the BK2–BK4 real-data gate, scaffold standalone `dotfiles/apps/gita`
  with `topic_provides: [gita]` and `topic_requires: [mise, python, git]`.
  Mise provides Python; git comes from apt/Homebrew prerequisites and is
  probed on PATH as in `apps/chrome`. Do not wait for the queued `apps/git`:
  it owns git configuration, not the binary. Claim
  `dotfiles/apps/mise/files/config.toml` before taking ownership of its
  existing `pipx:gita` entry using first-party mise commands, the herdr pattern.
  Resolve the repo list in `dotfiles/roles/repo-context`, modelled on
  `roles/topic-resolution`. Gita initially reads it role-relatively, like
  `config/editors.yaml`; the queued `topic_subscribes` machinery later makes
  the behaviour-preserving switch, as already planned for vscode.
  Match existing clones by normalised host/owner/repo remote before cloning
  anything. Keep the normaliser pure and property-tested. Report matches
  outside the declared layout type; never relocate them automatically.
  Groups mirror layout types, one per type. Registration recurses, excludes
  `.venv`, and detects duplicate-basename collisions; membership cites paths
  under the type directory, never bare names. `gita ls` is one line, so any
  local count uses `wc -w`, not `wc -l`; keep measured counts out of the queue.
  Adopt each target's existing `~/.config/gita/repos.csv` baseline instead
  of rediscovering it, checking existence and provenance on that target.
  The earlier study attributes its baseline to the Mac on 2026-09-15; the
  later handoff says "this box" but identifies its session as Linux. Do not
  assume that the Mac's observed baseline exists on Linux.
  Never auto-trust SSH host keys. Bootstrap already clones via SSH to
  github.com on a provisioned machine; report another untrusted host once.
  Tag clone-new tasks `[install, upgrade]`, since `update.sh` requests only
  `upgrade`. With no local pick, report and do nothing. Removal unregisters
  gita entries and drops the topic's mise entry, never clones. During normal
  reconciliation, unregister entries removed from declarations only with
  `gita_unregister_removed`, default off.
  Done when both-OS templates render with `StrictUndefined`, deliberate
  breaks fail the tests with mutation trailers, and `--check` on the Linux
  target changes nothing. This hands clone/registration state to G4.

- **G4 — sync on update without allowing repo problems to abort the run.**
  After G3, implement sync on `--tags upgrade`, using G1's decision about
  calling gita or git. Fetch every repo, including dirty ones: fetch never
  touches the working tree. Then fast-forward only clean repos with
  `git merge --ff-only`. Report per-repo verdicts: fast-forwarded; skipped
  for dirty state, conflicts, detached HEAD, no upstream or a mid-operation
  state; or failed fetch. Failed fetch means UNKNOWN, never "up to date".
  Repo problems are reported and the run exits 0. Only the topic's own
  checks fail the run, such as a missing provider or malformed catalogue or
  machine file. Record the deviation from `TOPIC-RECIPES.md`'s "fail once
  at the end" in the topic README: the parent playbook's topic loop has no
  rescue, so raising here skips later app topics.
  Each run writes separate machine-written records of per-repo last-fetch
  and blocked-since timestamps, feeding reports and G5's warning. Preserve
  the stored last-good-run timestamp needed by that warning; an exit-0
  report of repo problems is not evidence that a failed fetch succeeded.
  Done when a planted dirty repo is fetched, skipped and reported while a
  clean repo fast-forwards, and a failed fetch cannot pass as "up to date",
  proven by deliberate mutation. This hands the sync path and timestamps
  to G5; G4, G5 and G7 run serially on the shared upgrade path.

- **G5 — schedule sync and warn only when stored state is stale or blocked.**
  After G4, add a systemd user timer on Linux with `Persistent=true` for
  catch-up, and a launchd agent on macOS. Default to three runs a day,
  every eight hours, overridable per machine. Use the ollama timer/plist
  templates as precedent. The unit invokes
  `~/dotfiles/run-role.sh gita upgrade`; its playbook lookup is CWD-relative,
  so set `WorkingDirectory` to the resolved `~/dotfiles` directory, or the
  launchd equivalent, and supply the absolute resolved `~/.local/bin/mise`
  path because a service PATH will not contain it. Resolve target paths at
  deploy time. Timer-triggered discovery is report-only (G7), with no
  surprise discovered clones.
  Add the warning as topic shell wiring under `files/zsh/*.zsh`. It reads
  stored timestamps only: no git, network or `stat`. Print one line when
  the last good run is older than 12 hours, any repo has not fetched in
  12 hours, or a repo has been blocked longer than 12 hours; otherwise be
  silent. On Linux, report `loginctl enable-linger` as the fix for running
  while logged out; never enable it silently.
  At G5's start, confirm the author's distinction between classifying a
  new clone from gh metadata and forbidden self-healing relocation under
  `docs/LAYOUT.md`. The handoff places that confirmation here; G7 consumes it.
  Done when units pass their validators, the warning fires at 13 hours and
  stays silent at one hour with both directions mutation-proven, and
  removal leaves none of the scheduling or warning wiring behind. Verify
  Mac runtime behaviour in a Mac session. G7 follows this item serially.

- **G6 — give gh one installation owner and adopt the existing Debian install.**
  Add a small `dotfiles/apps/gh` topic: Homebrew on macOS and GitHub's signed
  apt repository at `cli.github.com` on Debian. The handoff's 2026-09-23
  evidence is `apt-cache policy`: gh is a dpkg package from
  `https://cli.github.com/packages stable/main`, installed by hand rather
  than by a topic or deb-get; `deb-get list --installed` had no match.
  Adopt with `state: present`, not a reinstall. `apps/deb-get` currently
  repairs that repository's keyring and protects gh during removal. Move
  the keyring-repair entry from `dotfiles/apps/deb-get/vars/main.yaml` to
  the gh topic so the key has one owner, and account for the existing
  removal protection. A stale third-party apt source also offers older gh
  builds on the Linux target; the recorded apt selection preferred
  GitHub's newer package. Keep that source collision visible during adoption.
  Check recent history and claim `dotfiles/apps/deb-get/` before editing.
  Done when `--check` on the Linux target adopts without reinstalling and
  removal leaves apt's sources clean; exercise Homebrew in a Mac session.
  G6 may run any time, including alongside G2–G5, because it touches
  different files. Missing gh remains G7's UNKNOWN discovery case.

- **G7 — discover repositories through gh with explicit per-machine modes.**
  After G5, implement G1's selected discovery approach. Personal sources
  live in the committed catalogue; private sources, including work orgs,
  live only in that machine's local file. A source's per-machine mode is
  `add`, `report` (default), or `off`. These modes apply to user-run update;
  timer runs report only, never adding discovered clones. Tag discovery
  tasks `[install, upgrade]` so update's upgrade-only invocation finds them.
  Missing gh, logged-out access, rate limiting or truncation means UNKNOWN,
  never an empty result: add nothing and unregister nothing, while explicit
  repos still sync. The handoff verified on 2026-09-23 that `gh repo list`
  defaults to `--limit 30`; always set a limit and treat a full page as
  truncated. Add at most ten repos per run. Skip archived repos by default.
  Classify forks into `forks/`, templates into `templates/`, and other new
  clones into the source's declared type, carrying the author confirmation
  requested at G5's start. Existing clones are not relocated automatically.
  Record which gh account listed the source; private repos invisible to
  another account make the report partial, not evidence of absence.
  Write discovered entries to a separate machine-written record, never
  back into hand-edited YAML or its comments, and never back that record up.
  Removing a discovered repo means adding it to the source's exclude list;
  otherwise the next update rediscovers it. Keep the opt-in unregister and
  never-delete-clones rules from G3.
  Done when `report` and `add` work end to end and a gh failure cannot read
  as "no repos", proven by mutation. This item runs serially after G4 and
  G5 because all three edit the gita upgrade path.

- **BK2 — prove home-machine local backup and explicit recovery in a sandbox.**
  After G2, implement BK1's borg 1.4.x/borgmatic design with a local repo,
  timer, runtime keyring passphrase, capture allowlist, staleness warning,
  monthly `borgmatic extract` test restore and restore runbook. Use synthetic
  machine files until the full BK2–BK4 real-data gate passes. Owner and
  bounded retention are fixed before any archive exists; never prune the
  newest archive. Keep one repository per machine per destination.
  Capture an explicit path allowlist starting with
  `~/.local/state/machine/`, never "home minus excludes". The home capture
  contains `machine.yaml` and `private.yaml`; work-derived configuration
  belongs only in work 1Password, machine-written records are rebuilt, and
  customer data is never on the list. Apply the agent-read denial for the
  backup store, matching the machine-state denial in G2; this is a
  policy-path change needing PR review.
  Missing or empty source files mean no archive is created and nothing is
  pruned: deletion must not become a version or rotate out good copies.
  Verify the handoff's proposed borgmatic `before_backup` exit-75 soft
  failure actually skips both create and prune; that mechanism is unproven,
  and a failure of the claim requires another guard, not weaker behaviour.
  Never restore automatically: report the latest archive and exact restore
  command. Test that a run never restores automatically and an explicit
  restore works. Test fresh silence versus the accepted 12-hour stale
  warning, and that a planted customer-data path never reaches an archive
  while listed paths always do. The allowlist and missing-source guards
  must both decline when required and proceed when permitted.
  The handoff's Linux evidence on 2026-09-23 was systemd 249 without
  `systemd-creds`, with `secret-tool` present and linger off. Use GNOME
  keyring for scheduled passphrases; logged-in runs are expected to find it
  unlocked, but prove that with an actual timer run. On lookup failure,
  report the problem and let the staleness warning fire.
  Done when sandbox deletion makes the next run skip both archive creation
  and pruning, an explicitly requested restore brings the files back, and
  each rule above has a test seen to fail when deliberately broken,
  including the customer-data test in both directions. Record the timer
  evidence and runbook; BK3 follows with independent off-machine recovery.

- **BK3 — prove lost-home-machine recovery from the independent borg host.**
  After BK2, add BK1's append-only SSH host repository, separate from the
  local repository and unique to this machine and destination. Write it
  with its own `borg create`; never sync/copy the live local repo to make
  the host copy. Append-only access prevents a buggy or compromised client
  from deleting past backups. Occasional prune/compact needs a separate
  delete-capable key and must preserve the newest archive under BK1's
  bounded retention. Carry BK2's allowlist, missing/empty-source guard and
  agent-read denial to the backup store; records and customer data remain
  excluded, and work-derived configuration stays only in work 1Password.
  Put independent exported borg keys and passphrases in Bitwarden as the
  recovery copy, not solely in the scheduled runtime keyring. Write the
  recovery runbook: sign in to Bitwarden from a clean device, using an
  offline 2FA recovery code if the phone was lost with the machine; fetch
  the key and passphrase; run `borgmatic config bootstrap`; extract; verify;
  then start a new repository for future backups. Do not resume writing
  the old repository from the fresh client: that risks counter reuse.
  Recovery remains explicit, never automatic; report the latest archive
  and exact command. Done when an empty-HOME drill with only Bitwarden and
  host access recovers the synthetic machine files and starts a new repo
  afterwards, with the runbook and independent key copy verified. Keep
  actual recovery material out of committed documentation. BK4 follows;
  real machine-file data still waits for that final restore drill.

- **BK4 — prove work-Mac machine-file recovery using work 1Password only.**
  After BK3, work in a session on the Mac. Keep that machine's files in
  work 1Password, with save-on-change during runs the user starts and a
  stale-copy warning. A 1Password service account is an option only if
  BK1 confirms the org permits it. Verify actual 1Password unlock/save
  behaviour on that machine; the handoff has not checked it.
  No borg runs on the work Mac, and no personal backup tool runs on or
  uploads from the company-managed device. Work-derived configuration,
  including `work.yaml`, lives only in the work secrets manager. Customer
  data never enters the capture list or leaves the Mac; its backup belongs
  to the employer. Machine-written state is rebuilt, never backed up.
  Restore machine files explicitly from work 1Password; work-repo recovery
  through discovery is G7's later work. Carry the agent-read denial for machine
  files and the backup store, and BK1's ownership/retention contract.
  Done when save-on-change, stale-copy warning and the restore drill pass
  on the Mac using synthetic files. Only then is the shared real-data gate
  satisfied: seed Linux after its inventory and the Mac in its own session,
  then proceed to G3 in the binding order.

- **Decide the history scrub for the published machine hostname.**
  The 2026-09-23 handoff identifies a Mac hostname already published in
  `dotfiles/machines.yml` on `origin/main`; its resemblance to a hardware
  serial is unverified. Do not reproduce the value in the queue or report.
  G2 drops hostnames from current files; this separate task is the author's
  decision about history, not permission to rewrite it now. Record whether
  to scrub and the intended scope. If a rewrite is authorised, its plan
  must include a backup branch and provenance notes under `spec.md`
  § Change records. A rewrite only bounds future exposure: it cannot
  retract fetched, forked or indexed copies.
  Done when the author's scrub-or-retain decision and, if needed, the
  bounded rewrite plan are recorded without republishing the identifier.

- **Amend Topic bundles' machine binding to named sets plus a local pick.**
  The author's 2026-09-23 decision supersedes the 2026-09-12
  hostname-to-groups binding in this queue's Topic bundles section. Add a
  dated supersession note before the unstarted bundle work is built: topic
  groups use the same named-set and machine-local selection boundary as
  the repo catalogue, without committing hostnames. G2 owns the current
  machine-file migration; this item owns correcting the bundle requirement.
  Done when that section records the dated amendment and its downstream
  tasks follow the new binding rather than the old hostname map. This
  transcribes a settled decision; it does not reopen the bundle design.

### Refactor A — the `topical` CLI (provisioning config, state, bootstrapping)

Design already exists: `dotfiles/docs/ROADMAP-topic-cli.md`, marked "designed,
not built", written 2026-09-09. **Do not redesign it.** MVP is two commands and
the roadmap says to resist a third. These items implement it. Read the roadmap's
§ Constraints that are verified, not assumed before starting — they were checked
against this machine and must not be re-litigated.
- A10. **Plan the sunset of the six `~/bin` tool names, and connect it to the
  dispatcher work.** The design is explicit that `topical` adds a front door and
  does not close the old one, because renaming is a breaking change — but
  "never" is not the intent either. This is the deliberate, separate change the
  design says it must be. Four reference classes have to be audited together,
  all verified in `dotfiles/docs/ROADMAP-topic-cli.md` § Migration inventory:
  `playbook.yaml:291,303` calling `~/bin/ollama-models sync` in `post_tasks`;
  `apps/ollama/tasks/remove.yaml:160-161` removing tools by absolute path;
  `.claude/settings.local.json` allowlisting `ollama-role get *` and others **by
  name**, so a rename silently costs permissions; and launchd labels that embed
  the name, like `com.ollama-usage.snapshot`. The six are `browser-ext`,
  `ollama-models`, `ollama-role`, `ollama-usage`, `ollama-bench`, `ollama-evals`.
  Sequence matters: the front door must be proven before the old door closes, so
  this is blocked on the dispatcher actually working. Done when a dated plan
  exists naming which names go, which stay, and what each retirement touches —
  not when anything is renamed.
- A2. Build `topical new <name>`. Replaces `init-config.sh`, which copies
  `template_dir/` and stops, leaving every `topic.yml` field and five lifecycle
  stubs to be hand-edited. Done when scaffolding firefox needs no hand-editing to
  reach a valid, installable topic — and when the generated topic carries its own
  removal path, per `spec.md` § Layering — teardown changes with the thing it
  creates. That property is the main reason this tool is worth building.
- A3. Generalise `browser-ext` into `topical <name> ext add ...`. It already
  validates IDs, resolves names, pins tags and appends without destroying
  comments — but it lives inside the chrome topic and only knows browsers. Done
  when it serves chrome and firefox with no browser-specific code in the CLI.
- A4. Add dependency add/remove for non-extension topics, following the same
  comment-preserving edit approach. Done when adding a package to a topic never
  requires hand-editing YAML.
- A5. Add `topical bootstrap` — run a topic's install and its late-stage
  initialization, per `PRD.md` § Architecture. Done when a topic goes from
  scaffolded to "ready to use" through the CLI alone.
- A6. Make the CLI the path an agent drives, with the CLI remaining the human
  fallback. One implementation behind both. Done when an agent can add a topic
  end-to-end without editing a topic file directly.
- A7. Work the roadmap's § Migration inventory. Explicitly out of MVP — do not
  start before A2 and A3 are working.
- A9. **Make `template_dir/` manager-aware and fold it into the CLI, with an
  optional agent pass on top.** Consumes A8. Today the template is one shape for
  every topic, so `init-config.sh` copies a scaffold that is wrong for whichever
  manager the topic actually uses — no `vars:` block for a cask, no `become` for
  apt, an empty `upgrade.yaml` stub even when the manager's system role will
  never reach the topic.

  **Decided 2026-09-14: one template plus a generator that emits only what
  applies, not a set of per-manager variants.** Variants would be five
  near-identical scaffolds to keep in step, and `dotfiles/managers.yaml` (A8,
  delivered) already holds the differences as data for the generator to read.
  Write the generator to be carried into the separate `topical` project rather
  than as something thrown away here. **Review the choice after using it, not
  before** — variants read and diff more easily, so if the generator's
  conditionals grow hairier than five small directories would have been, that is
  the signal to switch. The trade is recorded so that comparison stays possible.

  First thing the generator should delete: `template_dir/` scaffolds a commented
  `snap` block that **zero topics use**, and that boilerplate is most of the 37
  commented-out module lines now sitting in topics that never wanted them.
  Emitting the one block a topic needs removes the category rather than
  documenting it. **Also sweep for scaffold-residue artifacts when A9 runs**
  (author, 2026-09-20): a topic-root `tasks.yaml` carrying unedited template
  boilerplate is the known instance (deb-get ships one beside its real
  `tasks/`; ollama carries the same leftover) — the sweep greps topics for
  the template's comment markers and strips what no topic ever filled in,
  rather than leaving dead boilerplate beside live tasks.
  **Do not build a second agent mechanism for the rest.** `migrate-to-roles.sh`
  already does this job and is the thing to absorb: it treats `template_dir/` as
  canonical, checks conformance with a **local** LLM (an Ollama chain —
  devstral-small-2, qwen3.5, mistral-small3.1, with deepseek-r1 and phi4 for
  reasoning), is re-runnable, has `--dry-run` and prompt previews, and already
  knows real legacy shapes: `uninstall.yaml` / `cleanup.yaml` / `teardown.yaml`
  as remove-task sources, stray root files belonging in `files/`, and the
  system-role topics that carry extra subtasks. That is the "migrations from
  older or unsupported formats" capability, built and working, sitting outside
  the CLI that should own it. A7 already covers the migration *inventory*; this
  is the mechanism.
  Keep the two passes separate and the second optional: the deterministic
  scaffold must produce a valid topic on its own, with the agent extending it
  only for cases the template does not encode — a manager nobody has written a
  variant for yet, a topic arriving in a shape the rules do not describe. An
  agent pass that is required rather than optional makes every `topical new`
  depend on a model being installed and answering, which is a worse failure mode
  than a scaffold that needs one manual edit. Done when `topical new` emits a
  topic correct for its manager without an LLM in the loop, `migrate-to-roles.sh`
  has no logic the CLI lacks, and the agent pass is reachable by an explicit flag
  that says what it changed.

### Topic bundles — data-first grouping

Design settled with the author 2026-09-12: bundles are data, not directories —
apps/ stays flat, a bundle config object names its members and relationships,
and relationships live in the bundle rather than inside each topic (the
author's modularity requirement). Topics keep minimal `topic_requires` so they
stay standalone-installable; bundles complement and win on conflict. If
nesting ever comes, it happens together with the queued TOPICS-citation
rewrite — never as two rewrites of 40 files.

**Binding resolved 2026-09-12, after the author's expert challenge:** the
machine→groups map is `machines.yml` — a file that does not exist yet, settled design rather than precedent — kept as **plain data** (hostname →
groups), slurped by the parent playbook exactly like `topic.yml` files are
today — no Ansible inventory semantics. Disambiguation is
`ansible_facts['hostname']` (gathered every run) intersected with the map;
an inventory of named hosts would fight the self-applying `hosts: localhost`
design and buys nothing for a one-machine-at-a-time fleet. Inventory
`children:` remains the upgrade path if this ever becomes a true multi-host
fleet — the map's shape ports 1:1. Vocabulary: the config object is a
**group**, the selector is `-e group=<name>`, unmapped machines keep
all-topics+warn. The items below still say "bundle" and `-e bundle=` —
rewritten when the schema item lands.

- Define the bundle schema and document it in `dotfiles/docs/TOPICS.md`. A
  bundle config object (e.g. `apps/bundles/ai-strategy.yml`) names member
  topics, run order, shared configuration, machine targeting (os/arch
  filters), and teardown semantics. Done when the schema is documented with a
  worked example and validated against the parent playbook's discovery
  (find recurse depth 2 already tolerates future nesting; layout stays flat).
- Add bundle-aware limiting to the parent playbook: `-e bundle=<name>` with
  `--tags install|upgrade|remove` runs only that bundle's members for this
  machine (os-filtered). Done when a limited install touches exactly the
  bundle's members here, and a limited remove still consults `requires_map`
  before tearing any shared dep.
- Create the first bundle, `ai-strategy`: ollama, mise, opencode (+ the
  dotagents topic when it exists), ordered so mise precedes opencode (node).
  Done when the bundle exists, a limited run selects exactly those topics on
  this machine, and the Mac case is documented (topic_os filtering does the
  per-machine part).

### Refactor B — factor the AI/LLM tooling out of this repo

Required by `PRD.md`: dotfiles and provisioning are the trunk, this tooling is a
branch, and the architecture rule says provisioning may install and trigger a
tool but never contain its logic or state. The Ansible role STAYS — installing a
runtime and pulling weights is machine setup. What leaves is everything about the
author rather than the machine.
- B1. Decide the new home and its install method. **Home decided by the author
  2026-09-12:** `ai-prompt-library` now (skills, evals, policy, tooling work
  lands there), `impromptu` eventually once the tool is built up. **Addendum
  2026-09-14, a candidate supersession:** the author announced `llocallabs.ai`
  — a collection of repositories consolidating the AI tooling and agent
  projects, starting with a new anchor repo, with AI research, testing and
  benchmarking moving out of this repo (tasks in § Now). ai-prompt-library
  and impromptu may consolidate under it; whether that replaces the 09-12
  home decision or sits above it is part of what B1 still answers. Still
  open, and deliberately so: the install method this repo pins (B1's other
  half), and whether policy management has full scope in any home — the
  author marked this unresolved; see `ROADMAP.md` § Over-arching policy.
  Blocks B2 below only on the install-method half.
- B2. Write the move manifest — every affected file classified as leaves, stays,
  or is deleted. Done when the list exists and later items cite it instead of
  re-deciding per file.
  **The llocallabs cluster and its timing dependencies (recorded 2026-09-14,
  corrected by the advisor pass 2026-09-15).** Six queued items cite each
  other. The gate structure has TWO independent roots, not one linear order:
  the manifest needs the anchor repo to exist (a manifest naming a
  nonexistent home is a guess) AND B1's install-method answer, which is
  deliberately still open. (2) The three research projects queued in § Now
  and § Planned (sandboxing, session-management handoff, RAG/graphs) are
  first-class llocallabs candidates — but which branch fires, start-there
  or start-here, is the AUTHOR'S call, made and recorded in the session
  that starts the work; without that arbiter two machines can pick opposite
  branches and both be following this file. (3) gita is a consumer, not a
  gate: its per-machine inventory must include the collection once it
  exists, but it waits on nothing here. (4) The strategy/policy agent
  consumes the research projects and cannot be stood up ahead of them.
  (6) The R&D factory is gated on the anchor repo and is the umbrella the
  research methods feed — it belongs to the collection from day one.
  Prerequisite the cluster silently assumed, now named: the capture store
  (`~/code/personal/llocallabs-capture/`) is unversioned,
  single-machine, and mixes private with shareable notes — before any
  cluster item starts on the second machine it must be versioned or synced
  AND separated (see the capture-store contract task in § Planned). Until
  the manifest lands, nothing in the cluster moves, and no item in it
  should be worked on the assumption it stays here forever.
- B3. Define the state contract for the new utility: one owner and one retention
  rule for data currently scattered across `~/.local/share/ollama-{usage,bench,
  evals}` and the `llm` sqlite log. This closes the standing data-ownership
  finding and is a precondition for the backup work, not a follow-up to it.
- B4. Topics consume policy through a declared capability, from its new home.
  One item, stated as the outcome rather than as its parts. It was originally
  cut as two — extract the resolver, then add the interface — and that cut was
  wrong: the first half alone relocates the call-site duplication instead of
  removing it, while looking finished. Take the resolver first inside this item,
  since it is the most self-contained piece and everything else depends on it.
  Done when the resolver runs from its new home, this repo installs it, topics
  declare the capabilities they exercise rather than deciding for themselves,
  and `tests/policy` passes against the moved copy with both directions still
  asserted.
- B5. Extract the eval harness — `ollama-evals`, cases, taxonomy. Largest surface
  and the most tests. Done when the suite is green from the new home.
- B6. Extract `ollama-profile` and `ask-research`.
- B7. Rewire the ollama role to install the utility pinned and trigger its
  initialization at a late stage, per `PRD.md`. Done when a fresh provision
  reaches "tools initialized" without this repo containing any tooling logic.
- B8. Delete the vacated code and update `spec.md`, `PRD.md` and `AGENTS.md` to
  point outward. Done when no AI tooling logic remains here and no doc describes
  it as if it were still local.
- Build a CLI that manages provisioning config and state, including
  bootstrapping. Think mise or apt, but for topics and their files: scaffold a
  new topic from a template, add or remove a dependency, run the bootstrap, and
  report state. One of the refactors named in `PRD.md`.
  Why it is worth building rather than tolerating:
  - It is what makes the PRD's complexity governor true instead of aspirational.
    The governor says a routine change must never require touching `spec.md` or
    writing a test — that only holds if a tool does the routine change correctly
    by construction.
  - It makes `spec.md` § Layering — teardown changes with the thing it creates
    structural rather than a discipline. A template that scaffolds install and
    removal together cannot forget the removal, which is the exact failure that
    rule was bought by: a hand-copied `launchctl unsetenv` list silently stopped
    covering a newly added variable.
  - Adding a topic by hand is the current cost, and it is being paid right now
    for the chrome topic. That is the motivating case, not a hypothetical.
  Target shape: the CLI is the trusted process, and an agent drives it rather
  than editing topic files directly. The CLI stays as the fallback for when the
  agent is not trusted or not present, so machine configuration can be updated
  as-you-go by either. Both paths go through one implementation, because two
  paths means two behaviours.
  Constraints it inherits: it belongs to the provision layer, so it may install
  and trigger but must never hold a tool's logic or state (`PRD.md`
  § Architecture). It must be topic-neutral — no topic gets special handling —
  and it consumes policy generally rather than embedding rules, per the policy
  generalisation item above.
- Research best practices for multi-agent branch orchestration, then design the
  state file. Wanted: a file the orchestrating agent maintains that records which
  branch each work item is on, what it is based on, and what needs rebasing when
  main moves — so a subagent is handed a rebase instead of discovering a conflict
  mid-task. Stress-testing branch-per-item already surfaced what it must handle:
  stacked branches for dependent items (A3 on A2), items that must not be split
  (the original B4/B5 cut), shared `conftest.py` fixtures, and governance-doc collisions across
  unrelated branches. Use the questioning skill in
  `~/code/personal/ai-prompt-library`. Should land before more than two agents
  run in parallel.
- Get a fast test loop. The full suite takes ~200s measured (two runs
  2026-09-22: 215s, 199.5s; the older 104s figure is stale), which is too slow
  to run per change — at that price the loop collapses into run-once-and-hope,
  which is precisely how regressions slip through. Target a change-relevant
  subset in around ten seconds. `-m "not llm_judge"` exists already; what is
  missing is a way for an agent to select the suites matching the files it
  touched. Slowest offenders measured 2026-09-22 (`--durations`): the two
  `tests/topic_resolution/test_opencode_both_os.py` renders (18.1s, 12.4s),
  three `tests/binned/test_binned_judge.py` cases (6.7s, 6.7s, 4.5s), then a
  long ~3s tail of policy/guards subprocess tests. **Sequencing from the
  shift-left study's advisor council, unanimous: fix these five slow tests
  first (200s to an estimated ~120s serial, zero flake risk), add
  `pytest-randomly` as a cheap order-dependence detector, and only then
  consider `pytest-xdist`** — parallelizing a suite this skewed before fixing
  its outliers buys 3-4x at real flake cost for half the win a serial fix gets
  free. `pytest-testmon`/`pytest-picked` were researched and rejected for the
  file-selection half of this task: both are blind to shell/YAML/`topic.yml`
  changes (testmon traces Python coverage only; picked maps by path and
  this repo's `tests/<script>/` layout breaks that mapping), and picked can
  select zero tests and exit green — exactly this repo's signature failure
  mode. Any selection mechanism built here must therefore guard against
  silent zero-selection.
- **Add a periodic (nightly) full-suite run, separate from any per-merge
  gate.** Settled with the author and a fusion council 2026-09-22, deciding
  decision 5 (minimum gate set per task class): a merge gate proves *this
  change* didn't break anything; it says nothing about whether the trunk
  was already broken, and that's a different job — one this repo has no
  mechanism for today (no CI service). Per-environment, matching existing
  precedent (`apps/ollama` installs a launchd agent, `apps/clamav` a
  systemd timer — new unit, not a new mechanism): a launchd agent on
  Darwin, a systemd timer on Debian, running the documented full-suite
  command and reporting failures somewhere the author will actually see
  them. Done when one machine has the timer installed, a deliberately
  broken test is shown to be caught by a scheduled run rather than only by
  a merge, and the report mechanism is named (not just "runs and logs to a
  file nobody reads").
- Add a `collected == 0` tripwire. A pytest hook that fails loudly if a run
  collects no tests — cheap (a few lines), and it closes the exact failure
  class already hit twice in this repo (the `clipped.bats` path pointing at a
  nonexistent binary; the empty-grep-passes pattern named in AGENTS.md §
  Prove the test fails). Named 2026-09-22 by the shift-left study's advisor
  council as the single highest payoff-per-line item researched. Done when a
  deliberately-broken test path or an empty `-k` filter is shown to fail the
  run rather than exit 0.
- **Generalize the golden-transcript pattern for `llm_judge` tests, instead
  of a VCR-style HTTP recorder.** Researched 2026-09-22, prompted by
  `pytest-recording` (kiwicom, real and mature — 615★, MIT): it doesn't fit
  here. VCR.py patches HTTP libraries inside the *test process*; this repo's
  `llm_judge` tests call models via `subprocess.run` (`pii-redactor` → the
  real `llm` CLI, a grandchild process) — the network call never happens
  where an in-process recorder is watching. The herdr work already proved
  the right-shaped mechanism once: "a golden transcript against the real
  binary caught the `letta (experimental)` wire variant" no library would
  have shown. Generalize that into a convention — record subprocess stdout
  to a fixture file once, replay from file by default, `--record` flag (or
  `llm_judge`-style marker) re-runs against the real model to refresh it —
  rather than adopting a tool that architecturally cannot reach the calls.
  Also verified the same session: `pytest-agentkit`, `pytest-agentprobe`,
  `pytest-agent-eval`, `pytest-agent-health` — not adopted now, watch-listed
  instead (§ Planned, "Watch the pytest-agent-* ecosystem").
- Add `pytest-timeout`. Formalizes the ad hoc `timeout N` wrapping AGENTS.md
  already documents as a lesson (a cold model load can exceed a short
  timeout and cascade into every subsequent run failing) — a per-test
  timeout marker on anything that shells out to a model makes the failure
  mode a named, bounded one instead of an open-ended hang. `pytest-cov`,
  `pytest-mock`, `pytest-env` researched and not adopted the same pass:
  `pytest-mock` is a convenience wrapper this repo's consistent
  `monkeypatch` usage doesn't need; `pytest-env` sets static config-file
  values and can't supply the *dynamic*, per-test `tmp_path`-derived paths
  the `$HOME`-sandbox fixture (above) requires. `pytest-rerunfailures`
  researched and explicitly rejected as a default: auto-rerun-until-green
  is the same shape as this repo's dominant failure mode (tests passing
  while testing nothing) — a test that passes on retry is evidence to
  investigate, not noise to suppress. If ever adopted, scope it to named
  environmental flakes only.
- Put the AI tooling under characterization tests BEFORE starting refactor B, and
  use them as the parity bridge. Audit the existing behaviour, add tests that pin
  it, then let the reimplementation run against the same tests. Parity becomes
  proven rather than assumed, and the rewrite stops being gated on a human
  re-reading every line. B5 needs this most — the eval harness is the largest
  surface being moved.
- Build the LEDGER for the trust ladder. The ladder itself — rungs, promotion
  streaks, incident classes A-D, what is explicitly not an incident, and ageing
  — is defined in `AGENTS.md` § Trust ladder. What remains is the record. The ladder widens an agent's autonomy
  per task class and blast radius rather than globally; the ledger is what makes
  promotion evidence-based instead of felt. Rungs: 0 propose only; 1 branch and
  PR; 2 self-merge docs and tests; 3 self-merge code inside a named blast radius;
  4 unattended on a task class with an async report. `AGENTS.md` § Merge gates
  already describes rungs 2 and 3 — what is missing is the record to promote
  against. Ledger: one line per completed agent item recording the item, the rung
  it ran at, which gates passed, whether the author corrected it, and the class
  of any correction. Promote on a streak of clean items at a rung; demote one
  rung on a single incident of a defined class. The incident classes were defined before any
  promotion existed to argue about, which was the point. Note this is the same discipline `spec.md` § Evidence
  applies to measured numbers: a trust claim carries its conditions or it is an
  assertion. **[open question: whether the ledger is committed or machine-local.
  It records this repo's work rather than usage, which argues for committing it,
  but it is also a running record of agent-versus-author correction that may not
  want to be public.]**
  **Two-track model, settled with the author 2026-09-22 (shift-left study):**
  trust attaches to the *mechanism*, not the commit or session — a
  deterministic check that has proven itself doesn't re-earn trust each run.
  This is what makes trust transferable rather than reset-per-item, per the
  author: "once we've built repeatable patterns we can label as high trust,
  they should in theory be transferrable — we don't want to start from
  scratch on stages for every commit." Two tracks, not one funnel:
  - **Deterministic track** (prek/shellcheck, bats, pytest exit codes, ruff,
    ty — anything with a binary, reproducible outcome). Entry gate: seen to
    fail once (mutation-proven, per § Prove the test fails). Graduation:
    short streak of clean runs. Once graduated, trusted permanently until it
    changes or a false negative is found.
  - **Judgment track** (agent code-gen, skill output, LLM-judge verdicts —
    anything with output variance). No single-run entry gate ("passed"
    doesn't mean the same thing twice); graduates on a rolling
    correction-rate window instead of a streak, and the trust *level* moves
    with the window rather than becoming permanent.
  **Bypass state — provisional, 2026-09-22.** The ledger schema needs a
  `bypassed(reason)` state alongside ran/failed, so a `--no-verify` push is
  recorded rather than invisible. Author: "we don't yet have a more nuanced
  set of use cases and edge cases; we're still building and experimenting a
  lot, so this isn't wrong but I don't know yet" — added now as a field,
  not as settled policy on when bypassing is acceptable. Revisit once real
  bypass cases accumulate; the field just has to exist before the first one
  happens, or it gets hidden instead of recorded.
  **Auditor of the auditor — designed 2026-09-22, consolidated from the
  advisor council.** Once the ledger exists: a small trigger script (`shuf`
  over the trailing window of ledger lines — a one-liner, not a build, same
  "provisioning installs and triggers, never contains logic" shape as
  everything else here) periodically samples one past merged item and asks
  the author two questions cold, without re-reading the original quiz
  notes first: do I still understand what this changed and why, and would I
  still approve it today? Recorded alongside the ledger: item id, date,
  outcome (`still-understand` / `drifted` / `would-not-approve-now`), and
  if drifted, what didn't hold up. A drifted outcome is not an incident
  against the agent — the code didn't change — it's a signal about review
  depth at the time; two or more in a window is the trigger to look at
  whether quizzing has gotten shallow, not to relitigate the item. Cadence
  starts light (1 per ~10 merged items, or monthly, whichever is less
  frequent) and is itself a judgment-track mechanism under the two-track
  model above — it earns a tighter cadence over time rather than starting
  maximal.
  Latency tolerance is a property of *where an item sits on its track*, not a
  global clock: the funnel starts deliberately slow (least-privilege as the
  starting metaphor) and tightens toward the author's stated destination of
  under 5 seconds for fully-graduated deterministic checks, as the ladder's
  existing 5/10/20-clean-item promotion numbers are satisfied per mechanism.
  **[open question, routed rather than decided here: is a mechanism's earned
  trust keyed globally (e.g. "ruff" is trusted everywhere) or scoped per-repo
  — and is a *skill's* trust portable across repos?** This is the same
  question as the agent→function graduation policy already blocked on
  `ai-prompt-library`'s TASKS.md (§ Now, "Check AGENTS.md and CONTRIBUTING.md
  for places the agent→function graduation policy should apply") — the
  author approved routing it there rather than deciding it in this repo;
  no text lands here until that artifact exists.]
- Factor a general git repository template out of this work, using copier
  (9.17.2, installed). **Its own repository at `~/code/personal/`**, alongside
  ai-prompt-library and impromptu — not a directory here, and not under
  `~/code/work/`. Name is not settled; it is the reusable half of this repo's
  practice, so something like `spec-driven-repo-template` describes it. What has
  earned its place and is not dotfiles-specific: the document set and its
  separation of concerns (PRD what-for, spec what-must-stay-true, ROADMAP
  what-is-next, TASKS what-is-now, AGENTS how), the RECL loop, the verification
  practices (both-directions, prove-the-test-fails, property and fuzz guidance),
  the branching and merge-gate conventions, and the Python toolchain section.
  Excluded: anything chezmoi, Ansible or model-specific, and anything
  language-specific — language conventions are a pluggable `<LANGUAGE>.md`
  chosen by copier prompt, so the template ships `docs/PYTHON.md` as one
  option rather than baking Python into AGENTS.md. `docs/` is the unit
  the template plugs into — adding a language means dropping one file there. That is what lets the template grow to
  cover other languages without a rewrite. This template IS the
  reusable AGENTS.md baseline, so the baseline-versus-overlay split happens here
  rather than separately. Done when a fresh repo scaffolded from it has the full
  document set, passes `skillet validate`, and asks its project-specific parts as
  copier prompts rather than leaving placeholders to hand-edit.
- Factor a copier template for the chezmoi-Ansible topic format. **Its own
  repository at `~/code/personal/`**, same placement as the general template
  above. It **builds on the general template rather than duplicating it** — but
  by composition, not inheritance. Verified against copier 9.17.2: there is no
  `extends`, `inherit`, `parent_template` or `base_template` keyword anywhere in
  the source. Three primitives do the job instead:

  - `answers_file` lets each template record its answers somewhere other than
    the default `.copier-answers.yml`. That is what makes two templates on one
    project possible, and `copier update -a <file>` then updates each
    independently.
  - `_external_data` (a name-to-YAML-path map, exposed to Jinja as
    `external.<name>`) lets the topic template READ the general template's
    answers file and reuse those answers instead of re-asking. Note the path
    must resolve inside the generated project unless `--trust` is passed, so
    the parent's answers file has to be committed there — which it is by
    default.
  - `_tasks` can shell out to `copier copy` of the general template. Available,
    and the most fragile of the three; prefer the first two.

  So: apply the general template first writing `.copier-answers.general.yml`,
  then the topic template writing `.copier-answers.topic.yml` and declaring
  `_external_data` against the first. The topic template contributes only what
  is specific to a chezmoi-Ansible topic.

  **The trap to avoid:** if both templates write to the same default answers
  file, the second silently overwrites the first's tracking and the general
  template can never be updated in that project again. Separate answers files
  are the whole mechanism, not a detail — and getting them right is what
  delivers the actual goal, which is that improving the general template later
  flows into every project built from it, topic repos included. Purpose is that someone can build a topic from scratch with an
  agent, and borrow one piece of this configuration without adopting the whole
  repo — see `PRD.md` § Topics are installable modules. Overlaps refactor A:
  `topical new` scaffolds a topic INSIDE this repo and this template scaffolds one
  for a repo that is not this one. They should share the canonical template
  rather than diverge — decide which owns it before the second is built. The
  module boundary itself is deferred to `ROADMAP.md` and is not a blocker; build
  against the format as it stands.
- Keep `docs/REFERENCES.md` current. The register exists and is verified
  as of 2026-09-11; what is missing is the habit. Re-check on quarter boundaries
  and whenever a listed tool is upgraded, updating `verified` even when nothing
  moved — a stale date is the signal, not the version. Two rows need action now:
  skillet 1.8.0 is out while `spec.md` pins 1.7.0, and ruff is installed but
  wired to nothing. **[open question: worth automating? A check comparing
  installed `--version` output against the register is easy; comparing against
  upstream release feeds is not, and would add network calls to the test suite.]**
- Build a dotagents topic and make opencode's skill set an optional dependency
  of it. **The manager decision is made — see
  `dotfiles/docs/AGENT-ARTIFACTS.md` (2026-09-12): dotagents installs, pinned
  refs and committed lock; agentskills.io is the tracked format standard;
  skills.sh is discovery only.** The topic owns: the dotagents declaration
  (currently mise-managed via config.toml — decide which topic owns it), the
  user-global skill declaration in `apps/opencode/defaults/main.yaml`, and
  the install/sync trigger. **That is no longer a per-skill manifest** (changed
  2026-09-12, another session): it is a list of approved *sources* plus a
  `[trust]` allowlist dotagents enforces itself, per-source `exclude` vetoes, and
  a `roles/guards/` check that shells out to `tools/skill-trust`. Three pieces
  move, not one — and they argue for this task rather than against it, since
  source trust and a provenance guard belong to a dotagents topic far more
  clearly than to opencode. opencode stays fully usable without it — the
  binary and config remain its own — and gets skills only through the
  dependency. Done when the skill manifest lives in the dotagents topic,
  skills install from it alone, and apps/opencode carries no skill manifest
  of its own. Open before building: run the skillet evals, since the eval
  gate is now policy. (The agents.lock verification resolved 2026-09-12: the
  lock records resolved commit SHAs — see the record's exit-path section.)
- Choose a project templating tool, and benchmark rather than assume. `copier`
  9.17.2 is installed and is the incumbent, so it is the baseline to beat, not
  the default to accept. Candidates worth measuring: copier, cookiecutter,
  cruft (cookiecutter plus the update story it lacks), projen, yeoman, plop,
  degit, cargo-generate, and plain GitHub template repositories via
  `gh repo create --template`.
  Rank on what this project actually needs, in priority order: **update after
  generation** — the ability to improve the template later and pull the change
  into projects already built from it, which is the whole stated goal and the
  thing most of these tools simply do not do; composition, since the topic
  template has to build on the general one; conditional prompts, for selecting a
  `docs/<LANGUAGE>.md`; language-neutrality; and dependency footprint.
  Do this BEFORE building either template, since the answer decides their shape.
- Rebuild the 64 allow rules in `~/.claude/settings.json`. One of four settings scopes on this machine (257 allow rules
  in total). Machine-local, applies to **every** project including work repositories, and deliberately left alone
  when the project config was rebuilt — changing it from inside this repo would
  have silently altered agent behaviour in `~/code/work/`. Same approach as
  `docs/PERMISSIONS.md`, but the allow set has to serve repos this one
  knows nothing about, so start by finding out which projects depend on it.
- Deal with `~/dotfiles/.claude/settings.local.json` — **80 allow rules in no
  repository at all.** `~/dotfiles` is the chezmoi deploy target and a separate
  Claude project scope, so an agent started there gets these rules and none of
  the project's. One of them is `Bash(chezmoi apply *)`, which is the rule
  `AGENTS.md` § Applying is main-only exists to prevent. Not git-tracked and not
  chezmoi-managed, so nothing versions it and no review has seen it. Decide
  whether agents should ever run there at all — if the answer is no, the fix is
  to stop, not to curate the file.
- Prune `.claude/settings.local.json` — 25 accreted personal allows that no
  review has seen. Lower priority than the two above because a local ALLOW
  cannot re-open what a project DENY closes, **assuming deny wins across cascade
  layers**. That assumption is unverified; confirm it in a fresh session before
  relying on it, and if it is wrong this item becomes urgent rather than tidy.
- Resolve the CONTRIBUTING.md question and the repo-root `docs/` topology.
  The stale root `docs/CONTRIBUTING.md` copy is already trashed (`db4fc0e`) —
  but the advisor pass found the "older copy" story is wrong for three LIVE
  files: `docs/PYTHON.md`, `docs/PERMISSIONS.md` and `docs/REFERENCES.md`
  exist only in the root tree while AGENTS.md directs editors to
  `dotfiles/docs/` copies that do not exist for them. Decide: consolidate
  the root tree into `dotfiles/docs/` or document the split honestly —
  includes the original question of whether the whole root `docs/` tree
  goes.
- **Make `rerere.enabled` and `merge.conflictstyle=zdiff3` portable.** Both are
  set on this machine's `.git/config` for the chezmoi repo (2026-09-23) and reach
  every worktree, because worktrees share the common `.git/config`. They do not
  travel to another machine. `rerere` records a conflict resolution and replays
  it when the same conflict reappears, which is worth far more under the
  one-writer-per-worktree model than it was before: a tree merge surfaces the
  same conflict once per level, and resolving it three times by hand is three
  chances to resolve it differently. `zdiff3` adds the common ancestor to
  conflict markers, which is what distinguishes "both sides added a line, keep
  both and renumber" from "both sides renamed the same line, pick one" — the
  markers are identical without it, and the wrong reading silently deletes a
  value other code already branches on.

  Blocked on a decision, not on work: there is no chezmoi-managed git config and
  no `apps/git` topic, so this needs either adopting the unmanaged
  `~/.gitconfig` into chezmoi or creating a git topic. An agent cannot do the
  first — `~/.gitconfig` is outside the agent sandbox, so it cannot be read, and
  `spec.md` § Data forbids committing employer-identifying strings sight unseen.
  Either the author adopts it, or the sandbox grants read access, or the topic
  route is chosen. Done when both settings land on a second machine without
  being typed there. Note this is a deployed-tree path, so it is PR-and-review
  either way per `AGENTS.md` § Merge gates.

  **Done 2026-09-23** in `d9b15a1` and `cf30fb7`, on branch
  `skill-trust-foreign-buckets`. The author supplied `~/.gitconfig`, so the
  adoption route was taken: it is now `dot_gitconfig.tmpl`, with its three
  hardcoded `/Users/ben.davis` paths resolved through `.chezmoi.homeDir` —
  they would have failed silently on Linux. Two questions were left open
  rather than decided quietly: `user.email` is a personal address that will
  follow this file onto a work machine, and the empty-named `[mergetool ""]`
  and `[difftool ""]` sections look vestigial, their `cmd` lines starting at
  `"$LOCAL"` where a program name should be. Still PR-and-review before it
  merges, being a deployed-tree path.

  **Both since resolved on main:** the identity now prompts through
  `promptStringOnce` (`gitconfig: parameterize the user identity`), and the
  empty-named mergetool/difftool sections were confirmed dead and deleted.

- **Promote the bucketing procedure to a skill in `ai-prompt-library`.**
  Author-chosen 2026-09-24 over docs-only and a tool requirement. The steps in
  `docs/WORKTREES.md` § Bucketing are repo-agnostic, so a skill carries them to
  every repo an agent works in. Per AGENTS.md § Observations are deliverables,
  promote once the practice has earned its keep: trigger is PR #11 and #12
  reaching merge through the procedure, so the skill is written from two real
  cycles (PR #5's split, and that merge) rather than one. Lives in
  `ai-prompt-library`, not here. Automating the checks (bucket detection,
  merge-tree in every order, combined suite) is a separate, later requirement
  for the merge-gate checker above.

## History was rewritten on 2026-08-21 — reset before you resume

`main` was force-pushed. Every SHA from `bc72f5c` onward is new. Two mixed
commits were unscrambled: `b3ad740` split into a clamav half and a pii-redactor
half, and `5692a86` reworded to describe the 52 zsh deletions it actually
contains. Verified lossless — the tree is byte-identical to before, and the suite
is 218 passed / 7 deselected.

**Anything holding the old history must hard-reset, not pull.** A pull merges old
and new and resurrects the mixed commits.

```bash
git fetch origin
git reset --hard origin/main
git fetch origin 'refs/notes/*:refs/notes/*'   # notes are published now
```

Who needs this:

- **The second machine.** Not currently contributing, so no work is at risk — but
  it must reset before its next commit or it will reintroduce the old SHAs.
- **Any session idle-but-not-finished.** Reset before resuming; a commit against
  the old HEAD undoes the unscramble.

Pre-rewrite history is on `backup/pre-unscramble-272bdf7` if anything needs
recovering. Rollback is `git reset --hard backup/pre-unscramble-272bdf7` plus a
force-push, valid until someone pushes on top.

Each of the three commits carries a `git notes` PROVENANCE entry explaining the
split and pointing at the prevention. Read with `git notes show <sha>`.

## Private tasks

Some work cannot be described here without reproducing the thing it is trying to
remove. Those live in `~/.local/state/chezmoi/private-tasks.md` — machine-local,
never in git, same pattern as `~/.local/state/ai-policy/company.yaml`.

Currently one item there: a history-rewrite to remove an employer-domain string
from file contents. Scope, method and prerequisites are recorded in that file.

Note for whoever runs it: `TASKS.md` itself is in scope. An earlier revision of
this section quoted the target string literally before it was redacted, so the
purge must cover this file as well as the original.

Updated 2026-09-10 — the repo was public until that date and is now private, so
the rewrite is cleanup rather than mitigation; anything fetched during the window
is already out of reach. Scope grew: the `chrome` topic, added after the original
audit, carried more than the email. Its prose is fixed at tip, one functional
path is knowingly left, and a scoping test was agreed that settles the open
employer-URL question. Detail in that file. A committed doc for this was tried
and withdrawn — it reproduced the patterns, exactly as warned above.

## Decisions waiting on the author

From the shift-left testing study (2026-09-22). All four answered and
landed: the LEDGER item's bypass-state note and auditor-of-the-auditor
design (§ Now); the `$HOME`-exception reopen trigger (§ Planned); and
decision 5 — minimum gate set per task class, resolved 2026-09-22 with a
fusion council as "computed from the diff, not a per-class table"
(AGENTS.md § Merge gates). None open.

## Sandbox isolation — verified findings, 2026-09-20

Measured on this machine, for the coordination work in § Now. Recorded because
the next session would otherwise re-probe it, and the `external_directory` deny
makes that expensive.

**Host attribution needs confirmation (2026-09-24).** The Linux-specific
measurements below do not establish capabilities on the current macOS host.
The September 24 comparison measured macOS only; Debian verification remains
open. Its local report is
`.worktrees/wt-restart/.claude/RESEARCH-modular-agent-runtime.md`.

- **This box supports unprivileged bubblewrap.** `bwrap`, `podman`, `docker`,
  `systemd-run`, `unshare` and `qemu-system-x86_64` are all on `PATH`;
  `firejail`, `lima` and `colima` are absent. `user.max_user_namespaces` is
  115796, and both `kernel.unprivileged_userns_clone` and
  `kernel.apparmor_restrict_unprivileged_userns` are absent — no
  Ubuntu-style userns restriction applies. The `overlay` module is present, so
  an overlayfs upperdir can serve as a write audit trail.
- **macOS has no equivalent, and that shapes the design.** No mount
  namespaces, no Landlock, no overlayfs. Seatbelt (`sandbox-exec`) is the only
  native path-level mechanism and is deprecated with an undocumented profile
  language, though Chromium, Bazel, Nix, Codex CLI and Claude Code all ship it.
  App Sandbox needs a signed bundle and cannot express an admin-supplied path
  list; Endpoint Security needs an Apple-granted entitlement and a system
  extension. So: **state the guarantee at the weakest platform**, make the
  portable git-level path gate the invariant, and treat bwrap/Seatbelt as
  defence in depth that turns a commit-time rejection into a write-time
  `EACCES`. A future `sandbox-exec` removal is then an inconvenience, not a hole.
- **Choose VM-backed execution by workload and configuration cost.** The
  earlier recommendation against a Linux VM default was too broad for the
  current brief. On 2026-09-24 the author accepted low-configuration non-root
  containers, including Sandcastle's approach, as primary candidates. Check
  host prerequisites, filesystem/watch behavior and native macOS dependencies
  for the actual workload. VM-backed containers are not limited to an optional
  high-assurance mode.
- **Subtree confinement exists; shared-writer safety is a different question.**
  The earlier ecosystem-wide absence claim was too broad. On macOS 26.6.2,
  SRT 0.0.77 allowed a synthetic write under `./allowed` while denying one at
  the workspace root. The research agent and coordinator reproduced this on
  2026-09-24. It does not isolate a shared index or a concurrently changing
  test tree, so it does not establish safe multi-writer use of one checkout.
- **Adopt, don't build** (AGENTS.md ladder): `anthropics/sandbox-runtime`
  wraps a process in Seatbelt-or-bubblewrap from one policy. Candidate source
  checks on 2026-09-24 changed the earlier descriptions: Treebeard couples
  worktree/overlay lifecycle and has no verified Debian backend; nixcage is
  Nix/VM infrastructure; sandnix uses Seatbelt/Landlock; cco selects backends
  but deliberately permits networking. The report carries pins and limits.
  Installed mise also has optional Seatbelt/Landlock controls, separate from
  its ordinary environment setup. Building another runtime here remains out
  of scope.
  Name collision to avoid: three different projects are called
  `sandbox-runtime` (Anthropic's, `carderne/`, and a Rust crate).
- **Destructive git operations defeat any path allow-list.** `checkout`,
  `restore`, `reset --hard`, `clean` and a stray `gc` destroy other agents'
  work while touching only permitted paths. This is the strongest argument for
  worktree-per-agent and for `.git` read-only inside worktrees.
- **Allow-list directories, not files** — editors, formatters and compilers
  write temp-file-plus-rename, which needs write permission on the directory.
- **The cheapest high-value control is not confinement.** An out-of-scope write
  is recoverable from git; `push --force`, `gh pr merge` and `npm publish` are
  not. Deny push to protected refs and require human merge.
- **The chezmoi deployed tree is the gap the portable layer cannot see.**
  `~/bin` and `~/dotfiles` live outside the repo, so a git-level gate cannot
  detect a `chezmoi apply` violation — only OS confinement can. That is the
  strongest reason to keep bwrap despite its cost.

## Cross-session hazards

Files with more than one session touching them recently. Check `git log -3 <file>`
and `chezmoi status` before editing.

- `bin/executable_fetchurl` — actively developed; caused the only real merge
  conflict so far.
- `bin/executable_pii-redactor` — ported to Python, then extended with layered
  redaction by another session. Suite is 63 tests; run it after any change.
  Its conftest default mock is a *working* model, not `cat`: a pass-through mock
  plus exit-status assertions is green exactly when the tool leaks, which is the
  defect the layers exist to prevent. Ask for `mock_llm("cat")` explicitly.
- `bin/executable_model-bench` — multi-case judge suite; the reference scorecards
  in `CASES` must be re-derived if a case script changes.
- `dotfiles/apps/mise/files/config.toml` — two sessions edited it within an hour
  on 2026-09-11 (`b038cbe` removed two broken pipx tools, `907f3d0` pinned
  skillet). It rebased cleanly because the edits were in different regions, but
  it is a long flat list of tools that everything installs through, so the next
  pair of edits may not be so lucky. `~/.config/mise/config.toml` is a symlink
  to this file, so editing the source changes what mise reads immediately —
  before any `chezmoi apply`.

  2026-09-22: seen live again — during an unrelated commit, a mise run
  auto-bumped `github:danielmiessler/fabric` 1.4.478 → 1.4.479 in the working
  tree (reverted; the pin is deliberate, see the comment above the fabric
  line) and the `npm:@openai/codex` install failed with Permission denied
  (os error 13) on `/tmp/fslock/...`. Standing machine issue, not a one-off.
- `pyproject.toml` / `uv.lock` — the root project's declaration pair. A
  lockfile conflict is resolved by merging `pyproject.toml` and re-running
  `uv lock`, never by editing the lock. Both are ignored by chezmoi (never
  deploy); `.gitattributes` carries `uv.lock merge=binary`. Register any
  dependency change here.

## Standing reminders

- `bin/` scripts are chezmoi source (`executable_<name>`); `~/bin/<name>` is what
  runs. Check `chezmoi status` before editing or you will silently revert the
  working copy.
- A bare `pytest tests` reports "24 passed, 89 skipped" and looks green while
  testing almost nothing. Run it with `typer`, `questionary` and `hypothesis`
  present — see AGENTS.md.
