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
- **One task, one session, one worktree.** Claiming a second task after
  finishing your first is a branch decision: ask the author — carry on here
  only under the shared-branch exceptions, otherwise a fresh worktree and
  branch; an unavailable author defaults to fresh. A forked session leaves
  its parent's worktree before its first commit. Subtasks are the same rule
  one level down: the subtask's line is its single source of truth, its
  worktree is `<sid>_sub_<slug>` off the parent branch, and the parent
  integrates. Execution sessions are budgeted per contributor, per machine —
  set `.agent-budget.toml` from the sample before writing; an absent budget
  means ask. See `AGENTS.md` § Everything is branched.

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

- 2026-10-03T00:00Z — close out two landed-but-still-open § Now items
  (skill-trust foreign buckets, test-perf-xdist) into TASKS-RESOLVED
  (branch `agent/queue_closeout`, worktree `.worktrees/queue-closeout`) —
  `TASKS.md`, `TASKS-RESOLVED.md`

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

<!-- Migrated to the backlog-py task queue 2026-10-23: the former § Now items live in backlog/tasks/ as TASK-3..TASK-51, order preserved via ordinals. The board (backlog-py board / `task list`) is the source of truth for "what's next". New work is queued there, not here. -->
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
  **Ownership decided 2026-10-20 (author):** topical owns the canonical
  template first — the skeleton and manager block templates live in the
  topical repo with the generator — and this template inherits from there
  rather than copying.
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

- **Make docs repo-only by relocating them out of the payload.** [decision
  2026-10-03: docs are excluded from provisioned files; ROADMAP "Docs
  excluded from provisioned files"] `git mv dotfiles/docs/*` into root
  `docs/`, reconciling the two ARCHITECTURE.md and two USAGE.md copies —
  the maintained `dotfiles/docs/` content wins where the copies differ,
  root `docs/` becomes the one docs tree — and update every citation
  (~39 topic files cite `dotfiles/docs/TOPICS.md`; AGENTS.md, spec.md,
  CONTRIBUTING.md, ROADMAP-topic-cli). Root `docs/ARCHITECTURE.md`,
  `docs/USAGE.md` and `RESOURCES.md` drop out of `chezmoi managed` here or
  at the payload move, whichever lands first. Done when: nothing remains
  under `dotfiles/docs/`; `chezmoi managed` lists no docs path; doc-link/
  doc-integrity tests and skillet green; AGENTS.md § What this repo is
  points at root `docs/`. Lands before the payload move so that move
  carries no docs; the move item inherits a smaller tree. [unclaimed]

- **Clean dead payload before the source-root move.** [prep for the
  `.chezmoiroot` refactor] Root `executable_update.sh` is managed yet
  references a nonexistent root `playbook.yaml` — it deploys to
  `$HOME/executable_update.sh` broken today. `crontab/` is fully ignored,
  its `run_onchange_after_install-crontab.sh.tmpl` never runs, and nothing
  reads it. Delete both. Done when: both gone from source, `chezmoi
  status` shows exactly the two targets as pending removals and nothing
  else, suite green. Hands the move item a payload with no known-dead
  entries. Touches managed files → PR + human review. [unclaimed]

- **Move the payload under `home/` via `.chezmoiroot`.** [decisions
  2026-10-03: mechanism `.chezmoiroot`, subdir `home`; structure B — one
  branch, piecewise commits, squash-merged; ROADMAP "Move the deployed tree
  under `.chezmoiroot`"] Runs under the ground-shift protocol
  (`dotfiles/docs/research/coordinating-parallel-work-across-refactors.md`):
  runbook landed first (this item plus the research doc are it), census
  recorded there § Applied with author-confirmed dispositions, sentinel
  test proven red-on-old/green-on-new before the flip, session-start sync,
  observe-don't-patch with the 4h expiry, post-merge reconciliation pass
  re-running the census. Branch `agent/payload-home` off post-landing main
  (after the four census landings plus the author's run-role-cwd-fix).
  Internal commit sequence, each green: (1) pin the layout seam —
  `PAYLOAD_ROOT` in the root test conftest, ~25 fixture files rewired,
  still resolving to today's layout; (2) binned resolves its source path
  dynamically (`chezmoi source-path` / git-root walk) instead of hardcoding
  `:3100`, with `:3123`'s test-context walk re-anchored; (3) hooks match
  the payload root in either layout — `.pre-commit-config.yaml:44` and
  `scripts/run-bats.sh:31` regexes → `^((home/)?bin|scripts)/`, mutation-
  proven both directions; (4) pin the gate checker to real managed output —
  the committed real-data test; (5) the flip — `.chezmoiroot` containing
  `home`, `git mv` of `bin/`, `dotfiles/` (post docs-relocation),
  `dot_config/`, `dot_functions`, `dot_gitconfig.tmpl`, `dot_zprofile`,
  `dot_zshrc.tmpl`, `.chezmoiignore`, `.chezmoi.toml.tmpl`, `.chezmoidata/`
  into `home/` (`RESOURCES.md` stays root — repo-only by construction;
  special files move INTO `home/`, probe-verified unread at root; prune
  .chezmoiignore's now-noop tooling entries; payload-relative patterns
  survive), P1's constant → `home`, checker git-path normalization (git
  paths gain `home/`, managed source-relative forms don't change),
  governance-test advice line (`:83`). Squash-merge the five into ONE
  commit on main — chezmoi's failure mode is `.chezmoiroot` with an
  empty/misnamed subdir: silent empty source state, apply plans mass
  deletion — so main never holds the move half-landed. Mutation/
  `Failing-test` trailers consolidate into the squash commit message.
  Preps P1–P4 run as parallel sub-branches off the move branch, merged
  back by its owner (sequential by the mover is the fallback if the bench
  is empty). Verification: `chezmoi status` clean immediately post-flip;
  managed census compared at TARGET level before/after (delta = the
  cleanup plus docs items only); scratch clone `chezmoi init --apply`
  verified; suite green from a neutral cwd; checker normalization mutation
  seen to fail; bats hook proven to fire on a staged `home/bin/*.sh`.
  Lands after the docs relocation and ideally after PR #41 merges — both
  touch `dotfiles/apps/ollama`. The author runs `chezmoi apply` from main
  after review. [unclaimed]

- **Sweep docs/governance for the new layout.** [after the move] AGENTS.md
  (§ bin/ scripts description, § worktree `-S` recipe, run-role command,
  § Merge gates — docs are now repo-only, closing the dotfiles/docs
  deployed-docs finding), spec.md § Behavior layering, docs/GLOSSARY.md
  source-tree definition, docs/LANGUAGES.md, docs/PERMISSIONS.md
  (138/147/169/241), docs/WORKTREES.md, docs/USAGE.md, docs/ARCHITECTURE.md,
  CONTRIBUTING.md, topic READMEs (opencode, uv), roles/guards phrasing.
  Done when no doc claims the repo root is the chezmoi source or that docs
  deploy; doc-link/doc-integrity tests green. Depends on the move item
  (nothing to describe until it exists). [unclaimed]

- **Restore ruff coverage for the extensionless Python scripts, and fix
  what it surfaces.** [queued 2026-10-13; follow-up to PR #49] The ruff
  hooks now select their input by type, and pre-commit's tags come from
  identify, whose shebang detection requires the exec bit — chezmoi sources
  carry that bit in the `executable_` name prefix at mode 644, so the ~15
  extensionless Python scripts under `bin/` (8 `python3` shebangs, 6-7 PEP
  723 `uv run --script` scripts) no longer reach ruff through any hook;
  measured, `identify` tags `bin/executable_mailbox` (`#!/usr/bin/env
  python3`) non-executable and not python. Restore the coverage as a test,
  not a filter: a pytest globs `bin/` and `dotfiles/`, selects scripts
  whose first line names `python` or `uv run --script`, and runs ruff with
  the repo config — the test can decide "is this Python" by shebang, which
  neither identify nor a filename filter can do here. One finding already
  measured: `bin/executable_triage` D205 (docstring layout); fix it in the
  same change so the test lands green. Done when: the test passes on every
  selected script, has been seen to fail (mutation: make the selector match
  nothing — the grep-over-empty trap), and no hook change is needed.

- **Build a declarative mise module or role so Ansible calls mise the way it
  calls apt/homebrew.** Every mise-managed tool — gita, codex, roborev,
  skillet, and every future pipx: entry — currently shells out to
  `mise use -g` / `mise unuse --global` / `mise upgrade` in its topic, with
  probe-first greps to stay idempotent. A module or role turns those into
  declarative tasks (present/absent, reported change, check-mode aware) like
  `community.general.homebrew`. The gita topic's install/remove are the first
  consumer and the migration pattern. Done when that topic runs through the
  module and its mise shell-outs are gone. Gated on the backlog-md-py
  migration below.

- **Migrate the task queue to backlog-md-py, paired with worktrunk.**
  Author direction 2026-10-18: before the mise module above, move full-time
  to backlog-md-py (the markdown-native task tool under evaluation — see
  PROCESS.md § Where the queue lives) and refactor/migrate all of `TASKS.md`
  into it, paired with worktrunk (the mise wrapper that generates and checks
  worktree-local denylists; evaluated 2026-09-24). Done when `TASKS.md` is an
  index over per-task files and a task line never lives only in a chat.

- **Refactor dotfiles storage and automate its presence, not its updates.**
  Dotfiles stays a top-level repo (`~/.local/share/chezmoi`, deployed to
  `~/dotfiles`), outside the `~/code` taxonomy. Requirement (author
  2026-10-18): a target machine must GET dotfiles automatically, but dotfiles
  is never auto-updated — pulling is deliberate. Two parts: (a) automate the
  add — a fresh box gets the checkout from one step, no scheduled pass pulls
  it; (b) refactor how it is stored and how changes are made to it to be
  more seamless — this design is open. Interview the author before cutting
  tasks; record the storage shape in `PRD.md`/`docs/LAYOUT.md` and the work
  items here. Done when a fresh machine clones dotfiles automatically and no
  update path pulls it.

- **Root-cause the two trunk regressions that landed with PRs #58–63.**
  [observed 2026-10-19 by the coordinator collecting payload-seam; both
  reproduced on pristine origin/main 92615ec in a scratch checkout] (a)
  tests/topics/test_opencode_config_layers.py:
  test_os_then_host_layers_override_common and
  test_ruling3_small_model_and_trivial_agents_render fail — opencode-layer
  rendering, likely from the oc2 work. (b) tests/topics/test_apt_source_audit.py:
  seven tests error at fixture setup with CalledProcessError — the fixture
  shells out to dotfiles/apps/apt/files/apt_keyring.py, which a PR in this
  range changed; the fixture and the script need reconciling. Note for the
  fixer: the pre-commit pyrefly hook checks project state and now excludes
  dotfiles/apps/opencode/molecule (merge de46484) because testinfra is
  group-scoped; check whether these failures share a root cause with that
  environment split. Done when both suites pass on main from a default
  environment (no extra groups) or each failure has a named owner and an
  open PR. [unclaimed]
- Audit the three filled-in old-style root `tasks.yaml` files the A9 sweep
  left behind. starship (169 lines), zim (111) and ollama (281) carry
  pre-roles-migration task bodies that nothing loads; the A9 sweep deleted
  the boilerplate and verified duplicates but left these three because
  their content may not have been fully absorbed by the migration —
  starship's Fira Code font install is the visible example. Done when each
  file's content is either confirmed absorbed by the topic's `tasks/`
  lifecycle files (and the file deleted) or the missing pieces are moved
  into the lifecycle files first. [unclaimed]

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
open. Its report is committed at `.claude/RESEARCH-modular-agent-runtime.md`
on `main`.

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
